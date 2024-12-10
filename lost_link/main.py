import os

from langchain_community.embeddings import LlamaCppEmbeddings

import args
from langchain_chroma import Chroma

from lost_link.ai.file_to_document import FileToDocumentConverter
from lost_link.ai.models import ModelManager
from lost_link.const import ALLOWED_EXTENSIONS
from lost_link.db.db import DB
from lost_link.dir_manager import DirManager
from lost_link.db.local_file_manager import LocalFileManager
from lost_link.db.embedding_manager import EmbeddingManager
from lost_link.settings import Settings
from lost_link.sources.dir_scanner import DirScanner
from lost_link.sources.dir_watcher import DirWatcher
from lost_link.sources.local_file_processor import LocalFileProcessor


def main():
    parser = args.init_argparser()
    arguments = parser.parse_args()
    run_debug = arguments.debug

    dir_manager = DirManager("../workdir")
    dir_manager.create_workspace()

    settings = Settings(dir_manager.get_settings_path())

    db = DB(dir_manager.get_db_path(), debug=run_debug)
    local_file_manager = LocalFileManager(db)
    embeddings_manager = EmbeddingManager(db)

    one_drive_file_manager = OneDriveFileManager(db)
    share_point_file_manager = SharePointFileManager(db)
    delta_link_manager = DeltaLinkManager(db)
    remote_file_synchronizer = RemoteFileSynchronizer(one_drive_file_manager, share_point_file_manager, delta_link_manager)

    remote_file_synchronizer.update_remote_files()

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

    vector_db = Chroma(persist_directory=dir_manager.get_vector_db_dir(), embedding_function=embeddings_model)
    file_converter = FileToDocumentConverter()

    local_file_processor = LocalFileProcessor(local_file_manager, embeddings_manager,file_converter, vector_db)

    print("Update embeddings")
    local_file_processor.process_changes()


if __name__ == "__main__":
    main()
