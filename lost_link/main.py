from db import DB
import args

from models.share_point_file_manager import SharePointFileManager
from sources.dir_watcher import DirWatcher
from models.delta_link_manager import DeltaLinkManager
from models.local_file_manager import LocalFileManager
from models.one_drive_file_manager import OneDriveFileManager
from remote.remote_file_synchronizer import RemoteFileSynchronizer

def main():
    parser = args.init_argparser()
    arguments = parser.parse_args()
    run_debug = arguments.debug

    db = DB(r"test.db", debug=run_debug)
    local_file_manager = LocalFileManager(db)

    one_drive_file_manager = OneDriveFileManager(db)
    share_point_file_manager = SharePointFileManager(db)
    delta_link_manager = DeltaLinkManager(db)
    remote_file_synchronizer = RemoteFileSynchronizer(one_drive_file_manager, share_point_file_manager, delta_link_manager)

    remote_file_synchronizer.update_remote_files()

    if arguments.background:
        dir_watcher = DirWatcher(local_file_manager)
        dir_watcher.watch([r"C:\tmp\Neuer Ordner"])
        return





if __name__ == "__main__":
    main()
