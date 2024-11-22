import os

from langchain_community.embeddings import LlamaCppEmbeddings

from db import DB
import args
from langchain_chroma import Chroma

from lost_link.ai.models import ModelManager
from lost_link.dir_manager import DirManager
from lost_link.models.local_file import LocalFileManager
from lost_link.settings import Settings
from lost_link.sources.dir_scanner import DirScanner
from lost_link.sources.dir_watcher import DirWatcher

def main():
    parser = args.init_argparser()
    arguments = parser.parse_args()
    run_debug = arguments.debug

    dir_manager = DirManager("../workdir")
    dir_manager.create_workspace()

    settings = Settings(dir_manager.get_settings_path())

    db = DB(dir_manager.get_db_path(), debug=run_debug)
    local_file_manager = LocalFileManager(db)

    if arguments.background:
        dir_watcher = DirWatcher(local_file_manager)
        dir_watcher.watch(local_paths, ALLOWED_EXTENSIONS)
        return

    model_manager = ModelManager(dir_manager.get_model_dir())
    vector_db = Chroma(persist_directory=dir_manager.get_vector_db_dir())

    print("Started File History AI:")

    print("Prepare ai models")
    model_manager.init_models()

    embeddings_model = LlamaCppEmbeddings(
        model_path=os.path.join(dir_manager.get_model_dir(), model_manager.get_embedding_model_filename()),
        n_gpu_layers=-1,  # Set to 0 for only cpu
        verbose=run_debug
    )

    #print("--- authenticate for graph api")
    #print("--- find and download files via api ---")
    #print("--- load files ---")
    #print("--- create embeddings ---")
    #print("--- cluster files ---")
    #print("--- create history for clusters")




if __name__ == "__main__":
    main()
