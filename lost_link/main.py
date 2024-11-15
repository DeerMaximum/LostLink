from db import DB
import args

from lost_link.ai.models import ModelManager
from lost_link.dir_manager import DirManager
from lost_link.models.local_file import LocalFileManager
from lost_link.sources.dir_watcher import DirWatcher

def main():
    parser = args.init_argparser()
    arguments = parser.parse_args()
    run_debug = arguments.debug

    dir_manager = DirManager("../workdir")
    dir_manager.create_workspace()

    db = DB(dir_manager.get_db_path(), debug=run_debug)
    local_file_manager = LocalFileManager(db)

    if arguments.background:
        dir_watcher = DirWatcher(local_file_manager)
        dir_watcher.watch([r"D:\tmp\Neuer Ordner"])
        return

    model_manager = ModelManager(dir_manager.get_model_dir())

    print("Started File History AI:")
    print("Prepare ai models")
    model_manager.init_models()
    #print("--- authenticate for graph api")
    #print("--- find and download files via api ---")
    #print("--- load files ---")
    #print("--- create embeddings ---")
    #print("--- cluster files ---")
    #print("--- create history for clusters")




if __name__ == "__main__":
    main()
