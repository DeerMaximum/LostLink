import os.path
import requests

class ModelManager:
    MODELS: dict[str, str] = {
        "llama3.2-3b.gguf": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q6_K_L.gguf?download=true",
        "mxbai-embed-large.gguf": "https://huggingface.co/ChristianAzinn/mxbai-embed-large-v1-gguf/resolve/main/mxbai-embed-large-v1.Q8_0.gguf?download=true"
    }

    def __init__(self, model_paths):
        self._model_paths = model_paths

    @staticmethod
    def _download_file(url: str, path:str):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=4096):
                file.write(chunk)

    def init_models(self):
        for filename, dl_link in self.MODELS.items():
            target_path = os.path.join(self._model_paths, filename)
            if not os.path.exists(target_path):
                print(f"Download {filename} from {dl_link}")
                self._download_file(dl_link, target_path)