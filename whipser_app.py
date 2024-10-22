import sys
import torch
import whisper
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QWidget

class WhisperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whisper Transcriber")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        
        self.transcribe_button = QPushButton("Select Audio File and Transcribe")
        self.transcribe_button.clicked.connect(self.transcribe_audio)
        layout.addWidget(self.transcribe_button)

        self.result_text = QTextEdit()
        layout.addWidget(self.result_text)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def transcribe_audio(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav)")
        if file_name:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = whisper.load_model("base").to(device)
            result = model.transcribe(file_name)
            self.result_text.setText(result["text"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperApp()
    window.show()
    sys.exit(app.exec())