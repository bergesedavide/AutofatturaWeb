import subprocess
import webbrowser
import time
import sys

def open_browser():
    time.sleep(2)  # aspetta che server sia attivo
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    # Avvia il server Flask in un processo separato
    proc = subprocess.Popen([sys.executable, "app.py"])
    open_browser()

    # Aspetta che il processo Flask finisca (CTRL+C per chiudere)
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
