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

## Zu .exe konvertieren

Führe diesen Befehl im venv aus: ``pyinstaller .\LostLink.spec`` <br>
Die fertige Exe wird dann im ``dist`` Ordner liegen