import os
from datetime import datetime
from stat import FILE_ATTRIBUTE_HIDDEN

from lost_link.const import ALLOWED_EXTENSIONS
from lost_link.local.dir_scanner import DirScanner
from lost_link.db.local_file_manager import LocalFileManager, LocalFile
from watchfiles import watch, Change


class DirWatcher:
    MAX_FILE_SIZE = 1024 * 1024 * 50  # 50 MB

    def __init__(self, local_file_manager: LocalFileManager):
        self._file_manager = local_file_manager

    def _file_is_in_size_limit(self, path: str) -> bool:
        if not os.path.exists(path):
            return True
        return os.path.getsize(path) <= self.MAX_FILE_SIZE

    @staticmethod
    def _file_has_extension(path: str, extensions: list[str]) -> bool:
        if len(extensions) == 0:
            return True
        return os.path.splitext(path)[1] in extensions

    @staticmethod
    def _is_path_hidden(path: str) -> bool:
        if not os.path.exists(path):
            return False
        return bool(os.stat(path).st_file_attributes & FILE_ATTRIBUTE_HIDDEN)
    
    @staticmethod
    def _is_path_folder(path: str) -> bool:
        return not os.path.splitext(path)[1]

    @staticmethod
    def _get_last_modification_date(path: str) -> float:
        try:
            return os.path.getmtime(path)
        except FileNotFoundError:
            return datetime.now().timestamp()

    def _handle_add(self, event: tuple[Change, str]):
        path = event[1]
        if not os.path.exists(path):
            # Path of new file should exist, otherwise don't add to DB
            # (also handles simultaneous add and delete event of temporary files)
            return
        change_time = self._get_last_modification_date(path)
        local_file = self._file_manager.get_file_by_path(path)

        if local_file:
            local_file.deleted = False
            local_file.edited = True
            local_file.last_change_date = change_time
            return

        self._file_manager.add_file(LocalFile(
            path=path,
            last_change_date=change_time,
            last_seen=datetime.now()
        ))

    def _handle_modified(self, event: tuple[Change, str]):
        path = event[1]
        change_time = self._get_last_modification_date(path)
        local_file = self._file_manager.get_file_by_path(path)
        if local_file is None:
            self._handle_add(event)
        else:
            local_file.deleted = False
            local_file.edited = True
            local_file.last_change_date = change_time

    def _handle_deleted(self, event: tuple[Change, str]):
        path = event[1]
        change_time = self._get_last_modification_date(path)
        local_file = self._file_manager.get_file_by_path(path)
        if local_file:
            local_file.deleted = True
            local_file.edited = False
            local_file.last_change_date = change_time

    def _handle_folder_add(self, event: tuple[Change, str]):
        dir_scanner = DirScanner(self._file_manager)
        folder_path = event[1]
        dir_scanner.fetch_new_files(folder_path, ALLOWED_EXTENSIONS)

    def _handle_folder_delete(self, event: tuple[Change, str]):
        folder_path = event[1]
        contained_files = self._file_manager.get_all_files_in_folder(folder_path)
        for local_file in contained_files:
            local_file.deleted = True
            local_file.edited = False
            local_file.last_change_date = self._get_last_modification_date(folder_path)

    def watch(self, paths: list[str], allowed_extensions=[]):
        for event in watch(*paths, raise_interrupt=False, ignore_permission_denied=True):
            for change in event:
                path = change[1]

                if self._is_path_folder(path):
                    if change[0] == 1:
                        self._handle_folder_add(change)
                    elif change[0] == 3:
                        self._handle_folder_delete(change)
      

                if (os.path.isdir(path) or
                        not self._file_is_in_size_limit(path) or
                        not self._file_has_extension(path, allowed_extensions) or
                        self._is_path_hidden(path)):
                    continue

                if change[0] == 1:
                   self._handle_add(change)
                elif change[0] == 2:
                    self._handle_modified(change)
                else:
                   self._handle_deleted(change)

            self._file_manager.save_updates()