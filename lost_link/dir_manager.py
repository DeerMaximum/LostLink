import os

class DirManager:
    def __init__(self, workspace_path):
        self._workspace_path = workspace_path
        self._db_path = os.path.join(self._workspace_path, 'data.db')
        self._model_dir = os.path.join(self._workspace_path, 'models')

    def create_workspace(self):
        if not os.path.exists(self._workspace_path):
            os.makedirs(self._workspace_path)

        if not os.path.exists(self._model_dir):
            os.makedirs(self._model_dir)

    def get_workspace_path(self):
        return self._workspace_path

    def get_model_dir(self):
        return self._model_dir

    def get_db_path(self):
        return self._db_path