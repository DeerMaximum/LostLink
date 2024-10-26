# Projektarbeit Lost-Link

## Installation

1. Erstelle ein neues Python venv:
 
    ``python -m venv venv``

2. Wechsle in das Erstelle venv:
    
    Powershell: ``./venv/Scripts/activate.ps1`` <br>
    CMD: ``./venv/Scripts/activate.bat``

3. Installiere die benötigten Pakete:

    ``pip install -r requirements.txt``

4. *(Optional)* Für nicht Ollama-Modelle installiere noch LlamaCpp

    > Für GPU-Unterstützung folge [dieser Anleitung](https://llama-cpp-python.readthedocs.io/en/latest/). Für NVIDIA Grafikkarten kannst du CUDA nehmen, für andere Vulkan.
    
    > Beachte die Installation dauert sehr lange (ca. 30min)

    ``pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu``
    

## Modelle

### Ollama

Falls du Ollama für die Modelle benutzt musst du sie vorher einmal herunterladen. Führe dafür folgende Befehle aus:

``ollama pull llama3.2:latest`` <br>
``ollama pull mxbai-embed-large:latest``

### Lokale Modelle

Wenn du die lokalen Modelle ohne Ollama-Server benutzen möchtest, musst du sie vorher einmal herunterlanden und in den `models` Ordner legen.

* [Llama3.2-3b](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q6_K_L.gguf?download=true)
* [mxbai-embed-large](https://huggingface.co/ChristianAzinn/mxbai-embed-large-v1-gguf/resolve/main/mxbai-embed-large-v1.Q8_0.gguf?download=true)

## Testdaten

Alle PDF- und Textdateien im Unterordner test-data werden verwendet.