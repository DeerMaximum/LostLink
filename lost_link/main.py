import  datetime
import os

from langchain_community.embeddings import LlamaCppEmbeddings

import args
from langchain_chroma import Chroma

from lost_link.db.delta_link_manager import DeltaLinkManager
from lost_link.db.one_drive_file_manager import OneDriveFileManager
from lost_link.db.share_point_file_manager import SharePointFileManager
from lost_link.ai.embedding_generator import EmbeddingGenerator
from lost_link.ai.file_to_document import FileToDocumentConverter
from lost_link.ai.models import ModelManager
from lost_link.const import ALLOWED_EXTENSIONS
from lost_link.db.attachment_manager import AttachmentManager
from lost_link.db.db import DB
from lost_link.dir_manager import DirManager
from lost_link.db.local_file_manager import LocalFileManager
from lost_link.db.embedding_manager import EmbeddingManager
from lost_link.remote.graph_api_access import OutlookAccess, GraphAPIAccess
from lost_link.remote.graph_api_authentication import GraphAPIAuthentication
from lost_link.remote.outlook import Outlook
from lost_link.settings import Settings
from lost_link.sources.dir_scanner import DirScanner
from lost_link.sources.dir_watcher import DirWatcher
from lost_link.sources.local_file_processor import LocalFileProcessor
from lost_link.remote.remote_file_synchronizer import RemoteFileSynchronizer
from lost_link.service_locator import ServiceLocator


def main():
    parser = args.init_argparser()
    arguments = parser.parse_args()
    run_debug = arguments.debug

    dir_manager = DirManager("../workdir")
    dir_manager.create_workspace()
    ServiceLocator.register_service("dir_manager", dir_manager)

    settings = Settings(dir_manager.get_settings_path())

    db = DB(dir_manager.get_db_path(), debug=run_debug)
    local_file_manager = LocalFileManager(db)
    embeddings_manager = EmbeddingManager(db)
    attachment_manager = AttachmentManager(db)

    one_drive_file_manager = OneDriveFileManager(db)
    share_point_file_manager = SharePointFileManager(db)
    delta_link_manager = DeltaLinkManager(db)

    graph_api_authentication = GraphAPIAuthentication(dir_manager,settings)
    ServiceLocator.register_service("auth", graph_api_authentication)

    if arguments.background:
        local_paths = settings.get(settings.KEY_LOCAL_PATHS, [])
        if local_file_manager.get_file_count() == 0:
            print("Running first dir scan")
            dir_scanner = DirScanner(local_file_manager)
            for path in local_paths:
                dir_scanner.fetch_changed_files(path, ALLOWED_EXTENSIONS)

        dir_watcher = DirWatcher(local_file_manager)
        dir_watcher.watch(local_paths, ALLOWED_EXTENSIONS)
        return

    model_manager = ModelManager(dir_manager.get_model_dir())

    print("Started File History AI:")

    print("Prepare ai models")
    model_manager.init_models()

    embeddings_model = LlamaCppEmbeddings(
        model_path=os.path.join(dir_manager.get_model_dir(), model_manager.get_embedding_model_filename()),
        n_gpu_layers=-1,  # Set to 0 for only cpu
        verbose=run_debug
    )

    print("Update embeddings")

    vector_db = Chroma(persist_directory=dir_manager.get_vector_db_dir(), embedding_function=embeddings_model)
    file_converter = FileToDocumentConverter()
    embedding_generator = EmbeddingGenerator(vector_db, embeddings_manager, file_converter)
    ServiceLocator.register_service("embedding_generator", embedding_generator)

    o_acc = OutlookAccess()
    outlook = Outlook(o_acc, attachment_manager, embeddings_manager, vector_db, dir_manager.get_tmp_dir(), settings)

    local_file_processor = LocalFileProcessor(local_file_manager, embeddings_manager,file_converter, vector_db)
    remote_file_synchronizer = RemoteFileSynchronizer(one_drive_file_manager, share_point_file_manager, delta_link_manager)

    local_file_processor.process_changes()
    remote_file_synchronizer.update_remote_files()
    outlook.update()


if __name__ == "__main__":
    main()
