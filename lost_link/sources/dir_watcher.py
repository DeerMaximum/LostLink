import os
from datetime import datetime

from lost_link.models.local_file import LocalFileManager, LocalFile
from watchfiles import watch, Change


class DirWatcher:

    def __init__(self, local_file_manager: LocalFileManager):
        self._file_manager = local_file_manager

    def _handle_add(self, event: tuple[Change, str]):
        path = event[1]
        change_time = os.path.getmtime(path)
        local_file = self._file_manager.get_file_by_path(path)

        if local_file:
            local_file.deleted = False
            local_file.edited = True
            local_file.modified = change_time
            return

        self._file_manager.add_file(LocalFile(
            path=path,
            last_change_date=change_time,
            embeddings_id=None,
            last_seen=datetime.now()
        ))

    def _handle_modified(self, event: tuple[Change, str]):
        path = event[1]
        change_time = os.path.getmtime(path)
        local_file = self._file_manager.get_file_by_path(path)
        if local_file is None:
            self._handle_add(event)
        else:
            local_file.deleted = False
            local_file.edited = True
            local_file.last_change_date = change_time

    def _handle_deleted(self, event: tuple[Change, str]):
        path = event[1]
        local_file = self._file_manager.get_file_by_path(path)
        if local_file:
            local_file.deleted = True
            local_file.edited = False

    def watch(self, paths: list[str]):
        for event in watch(*paths, raise_interrupt=False, ignore_permission_denied=True):
            for change in event:
                path = change[1]

                if os.path.isdir(path):
                    continue

                if change[0] == 1:
                   self._handle_add(change)
                elif change[0] == 2:
                    self._handle_modified(change)
                else:
                   self._handle_deleted(change)

            self._file_manager.save_updates()