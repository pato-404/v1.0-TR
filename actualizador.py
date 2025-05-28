import os
import sys
import shutil
import subprocess
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# --- CONFIGURACIÓN ---
REPO_URL = "https://github.com/pato-404/v1.0-TR.git"
VERSION_URL = "https://raw.githubusercontent.com/pato-404/v1.0-TR/main/version.txt"
TEMP_FOLDER = "_actualizacion_temp"

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
            self.verificar_actualizacion()

    def verificar_actualizacion(self):
        self.label.setText("Verificando versión remota...")
        QApplication.processEvents()

        try:
            version_remota = requests.get(VERSION_URL, timeout=5).text.strip()
        except Exception as e:
            self.label.setText(f"❌ Error al obtener versión remota:\n{e}")
            return

        version_local = "0.0.0"
        if os.path.exists("version.txt"):
            with open("version.txt", "r", encoding="utf-8") as f:
                version_local = f.read().strip()

        if version_local == version_remota:
            self.label.setText("✅ Todo está actualizado")
            self.progress.setValue(100)
            QTimer.singleShot(1500, self.ejecutar_y_cerrar)
        else:
            self.label.setText("🔄 Nueva versión encontrada. Actualizando...")
            self.progress.setValue(50)
            QApplication.processEvents()
            self.actualizar(version_remota)

    def actualizar(self, nueva_version):
        try:
            if os.path.exists(TEMP_FOLDER):
                shutil.rmtree(TEMP_FOLDER)

            subprocess.check_call(["git", "clone", "--depth=1", REPO_URL, TEMP_FOLDER])

            # Buscar carpeta más profunda
            actual = TEMP_FOLDER
            while True:
                elementos = os.listdir(actual)
                if len(elementos) == 1 and os.path.isdir(os.path.join(actual, elementos[0])):
                    actual = os.path.join(actual, elementos[0])
                else:
                    break

            # Borrar todo menos este actualizador y version.txt
            for item in os.listdir():
                if item in ["actualizador.py", "version.txt"] or item == TEMP_FOLDER:
                    continue
                try:
                    if os.path.isfile(item):
                        os.remove(item)
                    elif os.path.isdir(item):
                        shutil.rmtree(item)
                except Exception as e:
                    print(f"❌ Error eliminando {item}: {e}")

            # Copiar archivos nuevos
            for item in os.listdir(actual):
                src = os.path.join(actual, item)
                dst = os.path.join(".", item)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

            shutil.rmtree(TEMP_FOLDER)

            # Guardar nueva versión
            with open("version.txt", "w", encoding="utf-8") as f:
                f.write(nueva_version)

            self.label.setText("✅ Actualización completada")
            self.progress.setValue(100)
            QTimer.singleShot(1500, self.ejecutar_y_cerrar)

        except Exception as e:
            self.label.setText(f"❌ Error al actualizar:\n{e}")
            self.progress.setValue(0)

    def ejecutar_y_cerrar(self):
        try:
            subprocess.Popen(["main.exe"], shell=True)
        except Exception as e:
            print(f"Error al ejecutar main.exe: {e}")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = LoadingScreen()
    splash.show()
    sys.exit(app.exec())
