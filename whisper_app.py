import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                              QFileDialog, QTextEdit, QVBoxLayout, 
                              QWidget, QComboBox, QLabel)
import sys
import torch
import whisper
import warnings
from functools import partial

# Suppress FP16 warning
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

def custom_load_model(name: str, device: str = None, download_root: str = None, in_memory: bool = False):
    # Override the torch.load function in whisper's _load_model
    original_torch_load = torch.load
    torch.load = partial(original_torch_load, weights_only=True)
    
    try:
        # Load the model using whisper's load_model function
        model = whisper.load_model(name, device, download_root, in_memory)
    finally:
        # Restore the original torch.load function
        torch.load = original_torch_load
    
    return model

class WhisperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whisper Transcriber")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
        self.model = None
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Model selection section
        model_label = QLabel("Whisper Model:")
        layout.addWidget(model_label)
        
        self.model_selector = QComboBox()
        self.model_selector.addItems(["small", "large"])
        layout.addWidget(self.model_selector)
        
        # Device info
        device_info = "CUDA Available" if torch.cuda.is_available() else "Using CPU"
        device_label = QLabel(f"Device Status: {device_info}")
        layout.addWidget(device_label)

        # Transcribe button
        self.transcribe_button = QPushButton("Select Audio File and Transcribe")
        self.transcribe_button.clicked.connect(self.transcribe_audio)
        layout.addWidget(self.transcribe_button)

        # Status and results
        self.status_text = QLabel("Status: Ready")
        layout.addWidget(self.status_text)
        
        self.result_text = QTextEdit()
        layout.addWidget(self.result_text)

        self.copy_button = QPushButton("Copy Transcription")
        self.copy_button.clicked.connect(self.copy_transcription)
        layout.addWidget(self.copy_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_model(self):
            model_size = self.model_selector.currentText()
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            try:
                self.status_text.setText(f"Status: Loading {model_size} model...")
                QApplication.processEvents()

                # Create a cache directory in user's home directory if it doesn't exist
                cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
                os.makedirs(cache_dir, exist_ok=True)
                
                # Use the custom load_model function
                self.model = custom_load_model(
                    model_size,
                    device=device,
                    download_root=None,
                    in_memory=True
                )
                
                self.status_text.setText(f"Status: Successfully loaded {model_size} model on {device}")
                
            except Exception as e:
                error_msg = f"Error loading model: {str(e)}"
                self.status_text.setText(f"Status: {error_msg}")
                self.result_text.setText(error_msg)
                raise

    def transcribe_audio(self):
        if self.model is None:
            try:
                self.load_model()
            except Exception:
                return  # Error already handled in load_model
        
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.m4a *.wma)"
        )
        
        if file_name:
            try:
                self.status_text.setText("Status: Transcribing audio...")
                QApplication.processEvents()  # Ensure UI updates
                
                result = self.model.transcribe(file_name)
                self.result_text.setText(result["text"])
                self.status_text.setText("Status: Transcription complete")
                
            except Exception as e:
                error_msg = f"Error during transcription: {str(e)}"
                self.status_text.setText(f"Status: {error_msg}")
                self.result_text.setText(error_msg)

    def copy_transcription(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_text.toPlainText())
        self.status_text.setText("Status: Transcription copied to clipboard")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperApp()
    window.show()
    sys.exit(app.exec())