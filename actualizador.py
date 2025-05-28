import os
import sys
import shutil
import subprocess
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# CONFIG
GITHUB_REPO_URL = "https://github.com/pato-404/v1.0-TR.git"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/pato-404/v1.0-TR/main/version.txt"
TEMP_FOLDER = "_actualizacion_temp"
EXCEPT_FILES = ["actualizador.py", "version.txt"]

# FUNCIONES
def get_remote_version():
    try:
        r = requests.get(GITHUB_VERSION_URL, timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except Exception as e:
        print("Error obteniendo versión remota:", e)
    return None

def get_local_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except:
        return "v0.0.0"

def set_local_version(version):
    with open("version.txt", "w") as f:
        f.write(version)

def borrar_archivos_locales():
    for item in os.listdir():
        if item in EXCEPT_FILES or item == TEMP_FOLDER:
            continue
        try:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)
        except Exception as e:
            print(f"Error borrando {item}: {e}")

def copiar_nuevos_archivos():
    for item in os.listdir(TEMP_FOLDER):
        origen = os.path.join(TEMP_FOLDER, item)
        destino = os.path.join(".", item)
        try:
            if os.path.isfile(origen):
                shutil.copy2(origen, destino)
            elif os.path.isdir(origen):
                shutil.copytree(origen, destino, dirs_exist_ok=True)
        except Exception as e:
            print(f"Error copiando {item}: {e}")

def actualizar():
    try:
        if os.path.exists(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)
        subprocess.check_call(["git", "clone", "--depth=1", GITHUB_REPO_URL, TEMP_FOLDER])

        borrar_archivos_locales()
        copiar_nuevos_archivos()
        shutil.rmtree(TEMP_FOLDER)
        return True
    except Exception as e:
        print("Error en actualización:", e)
        return False

# INTERFAZ
class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comprobando actualización")
        self.setFixedSize(400, 200)
        self.setStyleSheet("background-color: #1e1e2f; color: white;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        self.label = QLabel("Cargando...")
        self.label.setFont(QFont("Arial", 16))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #2c2c3e;
            }
            QProgressBar::chunk {
                background-color: #00cc99;
                width: 20px;
            }
        """)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)

    def update_progress(self):
        self.counter += 1
        self.progress.setValue(self.counter)
        if self.counter >= 100:
            self.timer.stop()
            self.check_update()

    def check_update(self):
        local = get_local_version()
        remote = get_remote_version()
        if remote and remote != local:
            self.label.setText(f"🔄 Actualizando a {remote}...")
            ok = actualizar()
            if ok:
                set_local_version(remote)
                self.label.setText("✅ Actualización completada")
            else:
                self.label.setText("❌ Error actualizando")
        else:
            self.label.setText("✅ Ya está actualizado")
        QTimer.singleShot(3000, self.close_and_launch)

    def close_and_launch(self):
        self.close()
        subprocess.Popen(["python", "launcher.py"])

# MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = LoadingScreen()
    splash.show()
    sys.exit(app.exec())
