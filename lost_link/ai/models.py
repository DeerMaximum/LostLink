import os.path
import requests
from tqdm import tqdm

class ModelManager:
    EMBEDDING_MODEL = ("mxbai-embed-large.gguf", "https://huggingface.co/ChristianAzinn/mxbai-embed-large-v1-gguf/resolve/main/mxbai-embed-large-v1.Q8_0.gguf?download=true")

    ALL_MODELS = [EMBEDDING_MODEL]

    def __init__(self, model_paths):
        self._model_paths = model_paths

    @staticmethod
    def _download_file(url: str, path:str):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        block_size = 4096
        with tqdm(total=total_size, unit="B", unit_scale=True, leave=False) as progress_bar:
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    progress_bar.update(len(chunk))
                    file.write(chunk)

                if total_size != 0 and progress_bar.n != total_size:
                    raise RuntimeError("Heruntergeladene Datei ist korrupt")

    def init_models(self):
        for filename, dl_link in self.ALL_MODELS:
            target_path = os.path.join(self._model_paths, filename)
            if not os.path.exists(target_path):
                print(f"Lade {filename} von {dl_link} herunter")
                self._download_file(dl_link, target_path)

    def need_init(self) -> bool:
        for filename, dl_link in self.ALL_MODELS:
            target_path = os.path.join(self._model_paths, filename)
            if not os.path.exists(target_path):
                return True
        return False

    def get_embedding_model_filename(self):
        return self.EMBEDDING_MODEL[0]
