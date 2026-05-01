import subprocess
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

IGNORAR = {'.git', '__pycache__', '.pyc', '.tmp', '~$'}

def ignorar_archivo(path):
    return any(p in path for p in IGNORAR)

class GitAutoPush(FileSystemEventHandler):
    def __init__(self):
        self._pendiente = False
        self._ultimo_evento = 0

    def on_modified(self, event):
        if not event.is_directory and not ignorar_archivo(event.src_path):
            self._pendiente = True
            self._ultimo_evento = time.time()

    def on_created(self, event):
        if not event.is_directory and not ignorar_archivo(event.src_path):
            self._pendiente = True
            self._ultimo_evento = time.time()

    def procesar_si_listo(self):
        # Espera 3 segundos sin cambios antes de hacer push
        if self._pendiente and (time.time() - self._ultimo_evento) >= 3:
            self._pendiente = False
            self.git_push()

    def git_push(self):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{fecha}] Cambios detectados — subiendo a GitHub...")
        try:
            subprocess.run(["git", "add", "."], check=True)
            resultado = subprocess.run(
                ["git", "diff", "--cached", "--quiet"], capture_output=True
            )
            if resultado.returncode != 0:
                subprocess.run(
                    ["git", "commit", "-m", f"auto: guardado {fecha}"],
                    check=True
                )
                subprocess.run(["git", "push"], check=True)
                print(f"[{fecha}] Subido correctamente a GitHub.")
            else:
                print(f"[{fecha}] Sin cambios nuevos para commitear.")
        except subprocess.CalledProcessError as e:
            print(f"Error al hacer push: {e}")

if __name__ == "__main__":
    print("Vigilando cambios... (Ctrl+C para detener)")
    print("Cada vez que guardes un archivo se subirá a GitHub automaticamente.\n")

    handler = GitAutoPush()
    observer = Observer()
    observer.schedule(handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            handler.procesar_si_listo()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nVigilancia detenida.")
    observer.join()
