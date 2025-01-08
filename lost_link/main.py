import logging
import os
import warnings

import art
import questionary
import webbrowser
from questionary import Choice
from halo import Halo
from langchain_chroma import Chroma
from langchain_community.embeddings import LlamaCppEmbeddings

import args
from lost_link.ai.cluster import Cluster
from lost_link.ai.embedding_generator import EmbeddingGenerator
from lost_link.ai.file_to_document import FileToDocumentConverter
from lost_link.ai.models import ModelManager
from lost_link.const import ALLOWED_EXTENSIONS
from lost_link.db.attachment_manager import AttachmentManager
from lost_link.db.db import DB
from lost_link.db.delta_link_manager import DeltaLinkManager
from lost_link.db.embedding_manager import EmbeddingManager
from lost_link.db.local_file_manager import LocalFileManager
from lost_link.db.one_drive_file_manager import OneDriveFileManager
from lost_link.db.share_point_file_manager import SharePointFileManager
from lost_link.dir_manager import DirManager
from lost_link.local.dir_scanner import DirScanner
from lost_link.local.dir_watcher import DirWatcher
from lost_link.local.local_file_processor import LocalFileProcessor
from lost_link.remote.graph_api_access import OutlookAccess
from lost_link.remote.graph_api_authentication import GraphAPIAuthentication
from lost_link.remote.outlook import Outlook
from lost_link.remote.remote_file_synchronizer import RemoteFileSynchronizer
from lost_link.result import ResultEntry, ResultMapper
from lost_link.service_locator import ServiceLocator
from lost_link.settings import Settings

class LostLink:

    def __init__(self):
        warnings.filterwarnings("ignore")
        logger = logging.getLogger("pypdf")
        logger.setLevel(logging.ERROR)

        self._spinner = Halo(spinner='dots')
        self._args = args.init_argparser().parse_args()
        self._debug = self._args.debug

        self._dir_manager = DirManager("../workdir")
        ServiceLocator.register_service("dir_manager", self._dir_manager)
        self._dir_manager.create_workspace()

        self._settings = Settings(self._dir_manager.get_settings_path())
        self._db = DB(self._dir_manager.get_db_path(), debug=self._debug)

        self._local_file_manager = LocalFileManager(self._db)
        self._embeddings_manager = EmbeddingManager(self._db)
        self._attachment_manager = AttachmentManager(self._db)

        self._one_drive_file_manager = OneDriveFileManager(self._db)
        self._share_point_file_manager = SharePointFileManager(self._db)
        self._delta_link_manager = DeltaLinkManager(self._db)

        self._graph_api_authentication = GraphAPIAuthentication(self._dir_manager, self._settings)
        ServiceLocator.register_service("auth", self._graph_api_authentication)

    @staticmethod
    def validate_path(path: str) -> bool:
        return os.path.exists(path) and not os.path.isdir(path) and os.path.splitext(path)[1] in ALLOWED_EXTENSIONS

    @staticmethod
    def filter_file_completion(path) -> bool:
        if os.path.isdir(path):
            return True
        return os.path.splitext(path)[1] in ALLOWED_EXTENSIONS

    def _background_job(self):
        if self._local_file_manager.get_file_count() == 0:
            self._spinner.start("Führe erstes Scannen der Verzeichnisse durch")
            self._local_scan()
            self._spinner.succeed()

        print("Höre auf Änderungen")
        dir_watcher = DirWatcher(self._local_file_manager)
        local_paths = self._settings.get(self._settings.KEY_LOCAL_PATHS, [])
        dir_watcher.watch(local_paths, ALLOWED_EXTENSIONS)

    def _prepare_ai(self):
        model_manager = ModelManager(self._dir_manager.get_model_dir())
        if model_manager.need_init():
            self._spinner.warn("Kein Modell gefunden. Starte Download")
            model_manager.init_models()
            self._spinner.start()

        self._embeddings_model = LlamaCppEmbeddings(
            model_path=str(os.path.join(self._dir_manager.get_model_dir(), model_manager.get_embedding_model_filename())),
            n_gpu_layers=-1,  # Set to 0 for only cpu
            verbose=self._debug
        )

    def _local_scan(self):
        dir_scanner = DirScanner(self._local_file_manager)
        for path in self._settings.get(self._settings.KEY_LOCAL_PATHS, []):
            dir_scanner.fetch_changed_files(path, ALLOWED_EXTENSIONS)

    def _update_embeddings(self):
        self._vector_db = Chroma(persist_directory=self._dir_manager.get_vector_db_dir(),
                                 embedding_function=self._embeddings_model)
        self._file_converter = FileToDocumentConverter()

        embedding_generator = EmbeddingGenerator(self._vector_db, self._embeddings_manager, self._file_converter)
        ServiceLocator.register_service("embedding_generator", embedding_generator)

        o_acc = OutlookAccess()
        outlook = Outlook(o_acc, self._attachment_manager, self._embeddings_manager, self._vector_db,
                          self._dir_manager.get_tmp_dir(), self._settings)

        local_file_processor = LocalFileProcessor(self._local_file_manager, self._embeddings_manager,
                                                  self._file_converter, self._vector_db)
        remote_file_synchronizer = RemoteFileSynchronizer(self._one_drive_file_manager, self._share_point_file_manager,
                                                          self._delta_link_manager)

        local_file_processor.process_changes()
        remote_file_synchronizer.update_remote_files()
        outlook.update()

    def _cluster_files(self):
        self._cluster = Cluster(self._vector_db, self._settings)
        self._cluster.create_cluster()

    def _get_search_embeddings(self) -> list[list[float]]:
        search_type = questionary.select("Wie möchtest du suchen?",
                                         choices=["Suchbegriff", "Datei"],
                                         instruction="(Pfeiltasten verwenden)"
                                         ).ask()
        if search_type == "Suchbegriff":
            # Suchbegriff
            search_term = questionary.text("Suchbegriff:").ask()
            return [self._embeddings_model.embed_query(f"Search for: {search_term}")]
        else:
            # File
            path = (questionary.path("Dateipfad:",
                                     validate=lambda text: self.validate_path(text),
                                     file_filter=lambda text: self.filter_file_completion(text)
                                     ).ask())
            content = [x.page_content for x in self._file_converter.convert(path)]
            self._spinner.start("Datei verarbeiten")
            search_embeddings = self._embeddings_model.embed_documents(content)
            self._spinner.succeed()
            return search_embeddings

    def prepare_results(self, cluster_id: int) -> list[ResultEntry]:
        mapper = ResultMapper(self._local_file_manager, self._attachment_manager, self._one_drive_file_manager, self._share_point_file_manager)
        return mapper.map(self._cluster.get_file_ids_for_cluster(cluster_id))

    @staticmethod
    def _print_results(results: list[ResultEntry]):
        choices: list[Choice] = []

        for result in sorted(results):
            choices.append(
                Choice(title=f"{result.filename} - {result.last_modified.strftime('%x %X')} - {result.source}", value=result.open_url)
            )

        choices.append(
            Choice(title="Beenden", value="exit")
        )

        while True:
            url_to_open = questionary.select("Welche Datei möchtest du öffnen?",choices=choices, instruction="(Pfeiltasten verwenden)").ask()
            if url_to_open == "exit":
                return

            webbrowser.open(url_to_open)


    def main(self):
        if self._args.background:
            return self._background_job()

        art.tprint("File History AI")

        self._spinner.start("KI Modelle vorbereiten")
        self._prepare_ai()
        self._spinner.succeed()

        if self._local_file_manager.get_file_count() == 0:
            self._spinner.start("Führe erstes Scannen der Verzeichnisse durch")
            self._local_scan()
            self._spinner.succeed()

        self._graph_api_authentication.login_if_needed()

        self._spinner.start("Dateien aktualisieren und Embeddings generieren")
        self._update_embeddings()
        self._spinner.succeed()

        self._spinner.start("Daten clustern")
        self._cluster_files()
        self._spinner.succeed()

        search_embeddings = self._get_search_embeddings()

        self._spinner.start("Cluster finden")
        target_cluster = self._cluster.get_nearest_cluster_for_vectors(search_embeddings)
        self._spinner.succeed()

        self._spinner.start("Ergebnisse erstellen")
        results = self.prepare_results(target_cluster)
        self._spinner.succeed()

        self._print_results(results)

if __name__ == "__main__":
    app = LostLink()
    app.main()
