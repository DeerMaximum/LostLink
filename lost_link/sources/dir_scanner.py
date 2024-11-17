import os
from datetime import datetime
from stat import FILE_ATTRIBUTE_HIDDEN

from lost_link.models.local_file import LocalFile, LocalFileManager

class DirScanner:
    MAX_FILE_SIZE = 1024 * 1024 * 50 # 50 MB

    def __init__(self,  local_file_manager: LocalFileManager):
        self._file_manager = local_file_manager

    @staticmethod
    def _is_entry_hidden(entry: os.DirEntry) -> bool:
        return bool(entry.stat().st_file_attributes & FILE_ATTRIBUTE_HIDDEN)

    @staticmethod
    def _file_has_extension(entry: os.DirEntry, extensions: list[str]) -> bool:
        if len(extensions) == 0:
            return True
        return os.path.splitext(entry.name)[1] in extensions

    def _file_is_in_size_limit(self, entry: os.DirEntry) -> bool:
        return os.path.getsize(entry) <= self.MAX_FILE_SIZE

    def _scan(self, path, allowed_extensions=[]) -> list[str]:
        subfolders, files = [], []

        for file in os.scandir(path):
            if file.is_dir():
                if not self._is_entry_hidden(file):
                    subfolders.append(file.path)
            else:
                try:
                    if self._file_has_extension(file, allowed_extensions) and self._file_is_in_size_limit(file) and not self._is_entry_hidden(file):
                        files.append(file.path)
                except OSError:
                    pass

        for folder in subfolders:
            files_in_folder = self._scan(folder, allowed_extensions)
            files.extend(files_in_folder)

        return files

    def fetch_changed_files(self, path: str, allowed_extensions=[]):
        scan_date = datetime.now()

        for file in self._scan(path, allowed_extensions):
            change_time = os.path.getmtime(file)

            db_file = self._file_manager.get_file_by_path(file)

            #New files
            if db_file is None:
                self._file_manager.add_file(LocalFile(
                    path=file,
                    last_change_date=change_time,
                    embeddings_id=None,
                    last_seen=scan_date
                ))

            #Edited
            if db_file and not db_file.deleted:
                db_file.last_seen = scan_date

                if change_time != db_file.last_change_date:
                    db_file.last_change_date = change_time
                    db_file.edited = True

        #Deleted files
        for delete_file in self._file_manager.get_all_files_seen_before(scan_date):
            delete_file.deleted = True
            delete_file.edited = False

        self._file_manager.save_updates()