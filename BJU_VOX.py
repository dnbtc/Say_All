import sys
import subprocess
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSlider, QLineEdit, QLabel, QFileDialog, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Thread class for running the export process
class ExportThread(QThread):
    progress = pyqtSignal(str)

    def __init__(self, text, rate, base_filename, output_directory, voices):
        super().__init__()
        self.text = text
        self.rate = rate
        self.base_filename = base_filename
        self.output_directory = output_directory
        self.voices = voices

    def run(self):
        # Create a subfolder with the base filename
        folder_path = os.path.join(self.output_directory, self.base_filename)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for voice in self.voices:
            filename = f"{folder_path}/{self.base_filename}_{voice}.aiff"
            command = f'say -v "{voice}" -r {self.rate} -o "{filename}" "{self.text}"'
            subprocess.call(command, shell=True)
            self.progress.emit(f"Exported: {filename}")

# Main application window
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.textEdit = QLineEdit(self)
        layout.addWidget(QLabel("Enter Text:"))
        layout.addWidget(self.textEdit)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(100)
        self.slider.setMaximum(500)
        self.slider.setValue(200)  # Default speed set to normal (200)
        layout.addWidget(QLabel("Speech Speed:"))
        layout.addWidget(self.slider)

        self.filenameEdit = QLineEdit(self)
        layout.addWidget(QLabel("Filename:"))
        layout.addWidget(self.filenameEdit)

        self.selectFolderButton = QPushButton("Select Output Folder", self)
        self.selectFolderButton.clicked.connect(self.selectFolder)
        layout.addWidget(self.selectFolderButton)

        self.exportButton = QPushButton("Export", self)
        self.exportButton.clicked.connect(self.export)
        layout.addWidget(self.exportButton)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.setLayout(layout)
        self.setWindowTitle("Text to Speech Exporter")
        self.setGeometry(300, 300, 300, 150)

    def selectFolder(self):
        self.output_directory = QFileDialog.getExistingDirectory(self, "Select Directory")

    def export(self):
        text = self.textEdit.text()
        rate = self.slider.value()
        base_filename = self.filenameEdit.text()
        voices = self.getVoices()

        self.thread = ExportThread(text, rate, base_filename, self.output_directory, voices)
        self.thread.progress.connect(self.updateLog)
        self.thread.start()

    def getVoices(self):
        result = subprocess.check_output("say -v '?'", shell=True).decode('utf-8')
        voices = [line.split()[0] for line in result.strip().split('\n')]
        return voices

    def updateLog(self, message):
        self.log.append(message)

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
