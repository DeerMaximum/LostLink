from datetime import datetime
import json
import os

import requests
from models.remote_file import RemoteFile, RemoteFileManager
from remote.graph_api_access import OneDriveAccess


class RemoteFileSynchronizer:

    def __init__(self,  remote_file_manager: RemoteFileManager):
        self._file_manager = remote_file_manager

    def update_remote_files(self):
        """
        Synchronizes the local database with remote file changes from OneDrive.

        - Fetches the delta changes from OneDrive.
        - Updates the local database to reflect added, modified, or deleted files.
        """
        one_drive_access = OneDriveAccess()
        delta_changes = one_drive_access.get_delta_changes()
        file_changes = self._filter_document_files(delta_changes)
        # self._pretty_print_json(file_changes)

        for file_change in file_changes:
            self._handle_file(file_change)
        
        self._file_manager.save_updates()
    
    def _handle_file(self, file_change: dict):
        if not file_change:
            return
        id = file_change.get("id", "")
        if not id:
            return

        db_file = self._file_manager.get_file_by_id(id)

        # New files
        if db_file is None:
            drive_item = OneDriveAccess.search_drive_item(id)
            embeddings_id = self._download_file_and_generate_embeddings(drive_item)
            self._file_manager.add_file(
                self._create_remote_file(drive_item, embeddings_id)
            )

        # Changed files
        if db_file and not "deleted" in file_change:
            self._file_manager.remove_file(db_file)
            drive_item = OneDriveAccess.search_drive_item(id)
            embeddings_id = self._download_file_and_generate_embeddings(drive_item)
            self._file_manager.add_file(
                self._create_remote_file(drive_item, embeddings_id)
            )

        # Deleted files
        if db_file and "deleted" in file_change:
            self._file_manager.remove_file(db_file)
        
    def _create_remote_file(self, drive_item: dict, embeddings_id: int) -> RemoteFile:
        if not drive_item:
            return None
        id = drive_item.get("id", "")
        name = drive_item.get("name", "")
        last_modified = drive_item.get("lastModifiedDateTime", "")
        last_modified_datetime = datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
        synchronization_date = datetime.now()
        if id and name and last_modified_datetime:
            return RemoteFile(
                id=id,
                name=name,
                embeddings_id=embeddings_id,
                last_modified_date=last_modified_datetime,
                last_seen=synchronization_date
            )
        return None
        
    def _download_file_and_generate_embeddings(self, file: dict) -> int:
        self._download_file(file)
        #TODO Embeddings generieren
        self._clear_download_files(exceptions=[".gitignore", ".gitkeep"])
        return None

    def _download_file(self, file_item: str, save_dir: str="file-downloads"):
        """
        Downloads a file from OneDrive using the given metadata and saves it locally.

        Args:
            file_item: A dictionary containing metadata of the file, including its `@microsoft.graph.downloadUrl` URL.
            save_dir: The directory where the file will be saved.
        """
        download_url = file_item.get("@microsoft.graph.downloadUrl", "")
        if not download_url:
            print("Error, no download URL found")
            return
        file_path = os.path.join(save_dir, file_item['name'])
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            with open(file_path, mode="wb") as file:
                file.write(response.content)
        except Exception as e:
            print(f"Failed to download file {file_item['name']}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)

        

    def _clear_download_files(self, directory_path: str="file-downloads", exceptions: list[str] = []):
        """
        Clears the specified directory by deleting all files except those listed in exceptions.
        Args:
            directory_path: The path to the directory to clean.
            exceptions: A list of filenames to exclude from deletion.
        """
        if exceptions is None:
            exceptions = []

        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist.")
            return

        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if filename in exceptions:
                continue
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path) 
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

    @staticmethod
    def _filter_document_files(delta_changes: dict) -> dict:
        """
        Filters out folders and keeps only document files from the delta response.
        """
        documents_only = [item for item in delta_changes if "file" in item]
        return documents_only

    @staticmethod
    def _pretty_print_json(json_dict: dict):
        pretty_json = json.dumps(json_dict, indent=4)
        print(pretty_json)

