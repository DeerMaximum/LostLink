from datetime import datetime
import requests
import json
import os

from db.delta_link_manager import DeltaLinkManager
from remote.graph_api_authentication import GraphAPIAuthentication
from service_locator import ServiceLocator



class GraphAPIAccess:

    @staticmethod
    def api_request(request_url: str):
        graph_api_authentication = ServiceLocator.get_service("auth")
        headers = graph_api_authentication.get_access_token_header(['Files.Read', 'Sites.Read.All'])
        headers["Prefer"] = "deltaExcludeParent"      
        response = requests.get(request_url, headers=headers)
        return response.json()


class OneDriveAccess:

    def __init__(self, delta_link_manager: DeltaLinkManager):
        self._delta_link_manager = delta_link_manager

    def get_delta_changes(self):
        request_url = "https://graph.microsoft.com/v1.0/me/drive/root/delta"
        delta_link = self._delta_link_manager.get_delta_link("OneDrive")
        if delta_link:
            request_url = delta_link
        
        response = GraphAPIAccess.api_request(request_url)
        self._new_delta_link = response.get("@odata.deltaLink", "")
        next_link = response.get("@odata.nextLink", "")
        delta_changes = response.get("value", "")

        while next_link:
            next_link_response = GraphAPIAccess.api_request(next_link)
            self._new_delta_link = next_link_response.get("@odata.deltaLink", "")
            next_link = next_link_response.get("@odata.nextLink", "")
            delta_changes = delta_changes + next_link_response.get("value", "")

        return delta_changes
    
    def save_delta_link(self):
        if self._new_delta_link:
            self._delta_link_manager.save_delta_link("OneDrive", self._new_delta_link)

    staticmethod
    def search_drive_item(item_id: str):
        request_url = "https://graph.microsoft.com/v1.0/me/drive/items/" + item_id
        response = GraphAPIAccess.api_request(request_url)
        return response


class SharePointAccess:
    def __init__(self, delta_link_manager: DeltaLinkManager):
        self._delta_link_manager = delta_link_manager

    def get_all_share_point_sites(self):
        request_url = "https://graph.microsoft.com/v1.0/sites?search=*"
        response = GraphAPIAccess.api_request(request_url)
        return response

    def get_delta_changes(self, site_id):
        request_url = "https://graph.microsoft.com/v1.0/sites/" + site_id + "/drive/root/delta"
        self._delta_link_key = "SharePoint-" + site_id
        delta_link = self._delta_link_manager.get_delta_link(self._delta_link_key)
        if delta_link:
            request_url = delta_link
        
        response = GraphAPIAccess.api_request(request_url)
        self._new_delta_link = response.get("@odata.deltaLink", "")
        next_link = response.get("@odata.nextLink", "")
        delta_changes = response.get("value", "")

        while next_link:
            next_link_response = GraphAPIAccess.api_request(next_link)
            self._new_delta_link = next_link_response.get("@odata.deltaLink", "")
            next_link = next_link_response.get("@odata.nextLink", "")
            delta_changes = delta_changes + next_link_response.get("value", "")

        return delta_changes
    
    def save_delta_link(self):
        if self._new_delta_link:
            self._delta_link_manager.save_delta_link(self._delta_link_key, self._new_delta_link)

    staticmethod
    def search_drive_item(site_id: str, item_id: str):
        request_url = "https://graph.microsoft.com/v1.0/sites/" + site_id + "/drive/items/" + item_id
        response = GraphAPIAccess.api_request(request_url)
        return response