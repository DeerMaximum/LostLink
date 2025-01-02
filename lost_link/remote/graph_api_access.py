import requests
import urllib
from datetime import datetime
from typing import Any

import pytz

from lost_link.db.delta_link_manager import DeltaLinkManager
from lost_link.service_locator import ServiceLocator

from requests import Response

class GraphAPIAccess:

    @staticmethod
    def api_request(request_url: str) -> dict[str, Any]:
        response = GraphAPIAccess.raw_request(request_url)
        return response.json()

    @staticmethod
    def raw_request(request_url: str) -> Response:
        graph_api_authentication = ServiceLocator.get_service("auth")
        headers = graph_api_authentication.get_access_token_header()
        headers["Prefer"] = "deltaExcludeParent"
        return requests.get(request_url, headers=headers)

class OutlookAccess:
    BASE_URL = "https://graph.microsoft.com/v1.0/me/messages"
    TRASH_URL = "https://graph.microsoft.com/v1.0/me/mailFolders/RecoverableItemsDeletions/messages"

    @staticmethod
    def _build_fetch_url(base_url: str, start_date: datetime) -> str:
        filters = ["hasAttachments eq true"]

        timestamp = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        filters.append(f"receivedDateTime ge {timestamp}")

        filter_query = " and ".join(filters)

        return f"{base_url}?$select=internetMessageId,id&$filter={filter_query}"

    def get_message_ids(self, start_date: datetime) -> list[tuple[str, str]]:
        url = self._build_fetch_url(self.BASE_URL, start_date)

        response = GraphAPIAccess.api_request(url)

        return [(x["id"], x["internetMessageId"]) for x in response.get("value", [])]

    def get_message_ids_trash(self, start_date: datetime) -> list[str]:
        url = self._build_fetch_url(self.TRASH_URL, start_date)

        response = GraphAPIAccess.api_request(url)

        return [x["internetMessageId"] for x in response.get("value", [])]


    def get_attachments(self, msg_id: str) -> list[tuple[str, str]]:
        att_id_url = f"{self.BASE_URL}/{msg_id}/attachments?$select=id,name"
        att_ids_response = GraphAPIAccess.api_request(att_id_url)

        return [(a["id"], a["name"])
                for a in att_ids_response.get("value", [])
                if a.get("@odata.type", "") == "#microsoft.graph.fileAttachment"]

    def download_attachment(self, msg_id: str, att_id:str, path: str):
        url = f"{self.BASE_URL}/{msg_id}/attachments/{att_id}/$value"

        try:
            response = GraphAPIAccess.raw_request(url)
            response.raise_for_status()
            with open(path, mode="wb") as file:
                file.write(response.content)
        except Exception as e:
            print(f"Failed to download attachment {att_id}: {e}")



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