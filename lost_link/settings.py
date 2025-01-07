import os
import json
from typing import Any


class Settings:
    KEY_APP_ID = "APP_ID"
    KEY_LOCAL_PATHS = "LOCAL_PATHS"
    KEY_TARGET_DAYS = "TARGET_DAYS"
    GROUP_KEY_HDBSCAN = "HDBSCAN"
    KEY_HDBSCAN_MIN_SAMPLES = "MIN_SAMPLES"
    KEY_HDBSCAN_MIN_CLUSTER_SIZE = "MIN_CLUSTER_SIZE"

    _SETTINGS_TEMPLATE: dict[str, Any] = {
        KEY_APP_ID: "",
        KEY_TARGET_DAYS: 90,
        KEY_LOCAL_PATHS: [

        ],
        GROUP_KEY_HDBSCAN: {
            KEY_HDBSCAN_MIN_SAMPLES: 3,
            KEY_HDBSCAN_MIN_CLUSTER_SIZE: 2
        }
    }

    def __init__(self, path: str):
        self._settings = self._SETTINGS_TEMPLATE

        settings_exists = os.path.exists(path)

        if not settings_exists:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(self._SETTINGS_TEMPLATE, file, ensure_ascii=False, indent=4)
        else:
            with open(path, 'r', encoding='utf-8') as file:
                self._settings = json.load(file)

    def get(self, key: str, default=None):
        return self._settings.get(key, default)
