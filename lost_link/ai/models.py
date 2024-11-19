import os.path
import requests
from tqdm import tqdm

class ModelManager:
    LLM_MODEL = ("llama3.2-3b.gguf", "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q6_K_L.gguf?download=true",)
    EMBEDDING_MODEL = ("mxbai-embed-large.gguf", "https://huggingface.co/ChristianAzinn/mxbai-embed-large-v1-gguf/resolve/main/mxbai-embed-large-v1.Q8_0.gguf?download=true")

    ALL_MODELS = [LLM_MODEL, EMBEDDING_MODEL]

    def __init__(self, model_paths):
        self._model_paths = model_paths

    @staticmethod
    def _download_file(url: str, path:str):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        block_size = 4096
        with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
            with open(path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    progress_bar.update(len(chunk))
                    file.write(chunk)

                if total_size != 0 and progress_bar.n != total_size:
                    raise RuntimeError("Could not download file")

    def init_models(self):
        for filename, dl_link in self.ALL_MODELS:
            target_path = os.path.join(self._model_paths, filename)
            if not os.path.exists(target_path):
                print(f"Download {filename} from {dl_link}")
                self._download_file(dl_link, target_path)

    def get_embedding_model_filename(self):
        return self.EMBEDDING_MODEL[0]

    def get_llm_model_filename(self):
        return self.LLM_MODEL[0]