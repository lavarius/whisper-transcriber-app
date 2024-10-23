import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                              QFileDialog, QTextEdit, QVBoxLayout, 
                              QWidget, QComboBox, QLabel, QHBoxLayout,
                              QProgressBar, QMessageBox)
import sys
import torch
import whisper
from whisper import (_download, _MODELS)
import warnings
from functools import partial
from pathlib import Path

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
        
        # Model selection section with download button
        model_layout = QHBoxLayout() # Create the horizontal layout

        model_label = QLabel("Whisper Model:")
        model_layout.addWidget(model_label)
        
        self.model_selector = QComboBox()
        self.model_selector.addItems(["base", "small", "large"])
        model_layout.addWidget(self.model_selector)

        self.download_button = QPushButton("Download Selected Model")
        self.download_button.clicked.connect(self.download_model)
        model_layout.addWidget(self.download_button)

        layout.addLayout(model_layout)

        # Progress bar for downloads
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Device info
        device_info = "CUDA Available" if torch.cuda.is_available() else "Using CPU"
        device_label = QLabel(f"Device Status: {device_info}")
        layout.addWidget(device_label)

        # Transcribe button
        self.transcribe_button = QPushButton("Select Audio File and Transcribe")
        self.transcribe_button.clicked.connect(self.transcribe_audio)
        layout.addWidget(self.transcribe_button)

        # Copy button
        self.copy_button = QPushButton("Copy Transcription")
        self.copy_button.clicked.connect(self.copy_transcription)
        layout.addWidget(self.copy_button)
        
        # Status and results
        self.status_text = QLabel("Status: Ready")
        layout.addWidget(self.status_text)
        
        self.result_text = QTextEdit()
        layout.addWidget(self.result_text)

        # Create main container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def get_model_path(self, model_name):
        """Get the path where the model should be stored"""
        # Use user's home directory for model storage
        home = Path.home()
        whisper_dir = home / '.cache' / 'whisper'
        whisper_dir.mkdir(parents=True, exist_ok=True)
        return whisper_dir

    def is_model_downloaded(self, model_name):
        """Check if the model is already downloaded"""
        model_path = self.get_model_path(model_name) / f"{model_name}.pt"
        return model_path.exists()

    def download_model(self):
        """Download the selected model"""
        model_name = self.model_selector.currentText()
        
        if self.is_model_downloaded(model_name):
            reply = QMessageBox.question(
                self, 
                'Model exists',
                f'The {model_name} model is already downloaded. Download again?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        self.status_text.setText(f"Status: Downloading {model_name} model...")
        self.progress_bar.setVisible(True)
        self.download_button.setEnabled(False)
        QApplication.processEvents()

        try:
            # Get the download directory
            download_dir = self.get_model_path(model_name)
            
            # Use whisper's internal download function
            _download(_MODELS[model_name], download_dir, in_memory=False)
            
            self.status_text.setText(f"Status: Successfully downloaded {model_name} model")
            QMessageBox.information(self, "Success", f"Successfully downloaded {model_name} model!")
            
        except Exception as e:
            error_msg = f"Error downloading model: {str(e)}"
            self.status_text.setText(f"Status: {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
            
        finally:
            self.progress_bar.setVisible(False)
            self.download_button.setEnabled(True)

    def load_model(self):
        model_name = self.model_selector.currentText()

        if not self.is_model_downloaded(model_name):
            reply = QMessageBox.question(
                self,
                'Model not found',
                f'The {model_name} model is not downloaded. Would you like to download it now?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.download_model()
            else:
                return False
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            self.status_text.setText(f"Status: Loading {model_name} model...")
            QApplication.processEvents()
            
            # Use the default cache location for loading
            self.model = whisper.load_model(model_name, device=device)
            self.status_text.setText(f"Status: Successfully loaded {model_name} model")
            return True
            
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            self.status_text.setText(f"Status: {error_msg}")
            self.result_text.setText(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            raise

    def transcribe_audio(self):
        # possibly needs edit MDB
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