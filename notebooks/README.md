## Modelle

> [!CAUTION]
> Wenn von einem Ollama Notebook zu einem lokalen gewechselt wird. Vorher die Ollama-Modelle aus dem RAM laden. Sonst kann es zu abstürzen führen!<br>
> ``ollama stop llama3.2:latest`` <br>
> ``ollama stop mxbai-embed-large:latest``

### Ollama

Falls du Ollama für die Modelle benutzt musst du sie vorher einmal herunterladen. Führe dafür folgende Befehle aus:

``ollama pull llama3.2:latest`` <br>
``ollama pull mxbai-embed-large:latest``

### Lokale Modelle

Wenn du die lokalen Modelle ohne Ollama-Server benutzen möchtest, musst du sie vorher einmal herunterlanden und in den `models` Ordner legen.

* [mxbai-embed-large](https://huggingface.co/ChristianAzinn/mxbai-embed-large-v1-gguf/resolve/main/mxbai-embed-large-v1.Q8_0.gguf?download=true)

## Testdaten

Alle PDF- und Textdateien im Unterordner test-data werden verwendet.