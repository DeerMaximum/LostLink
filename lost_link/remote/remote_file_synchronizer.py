import json
import os
import requests

from lost_link.db.db_models import OneDriveFile, SharePointFile
from lost_link.db.delta_link_manager import DeltaLinkManager
from lost_link.db.one_drive_file_manager import OneDriveFileManager
from lost_link.db.share_point_file_manager import SharePointFileManager
from lost_link.remote.graph_api_access import OneDriveAccess, SharePointAccess
from lost_link.service_locator import ServiceLocator


class RemoteFileSynchronizer:

    def __init__(self,  one_drive_file_manager: OneDriveFileManager, share_point_file_manager: SharePointFileManager, delta_link_manager: DeltaLinkManager):
        self._one_drive_file_manager = one_drive_file_manager
        self._share_point_file_manager = share_point_file_manager
        self._delta_link_manager = delta_link_manager

    def update_remote_files(self):
        one_drive_synchronizer = OneDriveSynchronizer(self._one_drive_file_manager, self._delta_link_manager)
        one_drive_synchronizer.update_one_drive_files()

        share_point_synchronizer = SharePointSynchronizer(self._share_point_file_manager, self._delta_link_manager)
        share_point_synchronizer.update_share_point_files()
    

class OneDriveSynchronizer:
    def __init__(self,  one_drive_file_manager: OneDriveFileManager, delta_link_manager: DeltaLinkManager):
        self._file_manager = one_drive_file_manager
        self._delta_link_manager = delta_link_manager

    def update_one_drive_files(self):
        """
        Synchronizes the local database with remote file changes from OneDrive.

        - Fetches the delta changes from OneDrive.
        - Updates the local database to reflect added, modified, or deleted files.
        """
        one_drive_access = OneDriveAccess(self._delta_link_manager)
        delta_changes = one_drive_access.get_delta_changes()
        file_changes = SynchUtil.filter_document_files(delta_changes)

        for file_change in file_changes:
            self._handle_file(file_change)

        one_drive_access.save_delta_link()
        
    
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
            self._file_manager.add_file(
                SynchUtil.create_remote_file(drive_item, OneDriveFile)
            )
            SynchUtil.generate_file_embeddings(drive_item, OneDriveFile)
            self._file_manager.save_updates()

        # Changed files
        if db_file and not "deleted" in file_change:
            self._file_manager.remove_file(db_file)
            drive_item = OneDriveAccess.search_drive_item(id)
            self._file_manager.add_file(
                SynchUtil.create_remote_file(drive_item, OneDriveFile)
            )
            SynchUtil.generate_file_embeddings(drive_item, OneDriveFile)
            self._file_manager.save_updates()

        # Deleted files
        if db_file and "deleted" in file_change:
            self._file_manager.remove_file(db_file)
            self._file_manager.save_updates()

    


class SharePointSynchronizer:
    def __init__(self,  remote_file_manager: SharePointFileManager, delta_link_manager: DeltaLinkManager):
        self._file_manager = remote_file_manager
        self._delta_link_manager = delta_link_manager

    def update_share_point_files(self):
        """
        Synchronizes the local database with remote file changes from SharePoint.

        - Fetches the delta changes from all SharePoint-Sites.
        - Updates the local database to reflect added, modified, or deleted files.
        """
        share_point_access = SharePointAccess(self._delta_link_manager)
        response = share_point_access.get_all_share_point_sites()
        SynchUtil.pretty_print_json(response)
        site_ids = [site.get("id") for site in response.get("value", []) if "id" in site]
        for site_id in site_ids:
            delta_changes = share_point_access.get_delta_changes(site_id)
            file_changes = SynchUtil.filter_document_files(delta_changes)
            for file_change in file_changes:
                self._handle_file(file_change, site_id)
            share_point_access.save_delta_link()
                
    def _handle_file(self, file_change: dict, site_id):
        if not file_change:
            return
        file_id = file_change.get("id", "")
        if not file_id:
            return

        db_file = self._file_manager.get_file_by_id(site_id, file_id)

        # New files
        if db_file is None:
            drive_item = SharePointAccess.search_drive_item(site_id, file_id)
            self._file_manager.add_file(
                SynchUtil.create_remote_file(drive_item, SharePointFile, site_id=site_id)
            )
            SynchUtil.generate_file_embeddings(drive_item, SharePointFile, site_id)
            self._file_manager.save_updates()

        # Changed files
        if db_file and not "deleted" in file_change:
            self._file_manager.remove_file(db_file)
            drive_item = SharePointAccess.search_drive_item(site_id, file_id)
            self._file_manager.add_file(
                SynchUtil.create_remote_file(drive_item, SharePointFile, site_id=site_id)
            )
            SynchUtil.generate_file_embeddings(drive_item, SharePointFile)
            self._file_manager.save_updates()

        # Deleted files
        if db_file and "deleted" in file_change:
            self._file_manager.remove_file(db_file)
            self._file_manager.save_updates()

    

class SynchUtil:
    @staticmethod
    def filter_document_files(delta_changes: dict) -> dict:
        """ Filters out folders and keeps only document files from the delta response. """
        documents_only = [item for item in delta_changes if "file" in item]
        return documents_only
    
    @staticmethod
    def create_remote_file(drive_item: dict, file_class: type, **extra_fields):
        """
        Creates an instance of a remote file object based on the provided data.

        Args:
            drive_item (dict): Metadata of the remote file retrieved from the drive.
            file_class (type): The class representing the file type (e.g., OneDriveFile or SharePointFile).
            **extra_fields: Additional fields required for specific file types (e.g., site_id for SharePointFile).

        Returns:
            An instance of the specified file_class with the populated fields, or None if drive_item is invalid.
        """
        if not drive_item:
            return None

        id = drive_item.get("id", "")
        name = drive_item.get("name", "")
        parent_path = drive_item.get("parentReference", {}).get("path", "")
        path = parent_path + "/" + name
        url = drive_item.get("webUrl", "")

        # Gemeinsame Felder
        file_data = {
            "id": id,
            "name": name,
            "path": path,
            "url": url,
        }

        # Zusätzliche Felder nur hinzufügen, wenn sie gebraucht werden
        file_data.update(extra_fields)
        return file_class(**file_data)

    @staticmethod
    def generate_file_embeddings(drive_item: dict, file_type: type, site_id=None) -> int:
        file_path = SynchUtil.download_file(drive_item)
        embedding_generator = ServiceLocator.get_service("embedding_generator")
        embedding_generator.generate_and_store_embeddings(file_path, file_type, drive_item["id"], site_id)
        #TODO Embeddings generieren
        return None

    @staticmethod
    def download_file(file_item: str) -> str:
        """
        Downloads a file from OneDrive or SharePoint using the given metadata and saves it locally.

        Args:
            file_item: A dictionary containing metadata of the file, including its `@microsoft.graph.downloadUrl` URL.
            save_dir: The directory where the file will be saved.

        Returns: the path of the downloaded file
        """
        dir_manager = ServiceLocator.get_service("dir_manager")
        save_dir = dir_manager.get_tmp_dir()
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
            return file_path
        except Exception as e:
            print(f"Failed to download file {file_item['name']}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
    

    @staticmethod
    def pretty_print_json(json_dict: dict):
        pretty_json = json.dumps(json_dict, indent=4)
        print(pretty_json)