from db import DB
import args

from sources.dir_watcher import DirWatcher
from models.delta_link_manager import DeltaLinkManager
from models.local_file_manager import LocalFileManager
from models.remote_file_manager import RemoteFileManager
from remote.remote_file_synchronizer import RemoteFileSynchronizer

def main():
    parser = args.init_argparser()
    arguments = parser.parse_args()
    run_debug = arguments.debug

    db = DB(r"test.db", debug=run_debug)
    local_file_manager = LocalFileManager(db)

    remote_file_manager = RemoteFileManager(db)
    delta_link_manager = DeltaLinkManager(db)
    remote_file_synchronizer = RemoteFileSynchronizer(remote_file_manager, delta_link_manager)

    remote_file_synchronizer.update_remote_files()

    if arguments.background:
        dir_watcher = DirWatcher(local_file_manager)
        dir_watcher.watch([r"C:\tmp\Neuer Ordner"])
        return





if __name__ == "__main__":
    main()
