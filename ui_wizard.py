from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class WizardView(QWidget):
    def __init__(self, on_folder_click):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Film Scanning Setup Wizard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #ffffff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.btn_dslr = QPushButton("📷 Capture via USB DSLR (Inactive)")
        self.btn_dslr.setFixedSize(350, 50)
        self.btn_dslr.setEnabled(False)
        self.btn_dslr.setStyleSheet(
            "background-color: #222222; color: #666666; border: 1px solid #333333; border-radius: 5px; font-weight: bold;"
        )
        layout.addWidget(self.btn_dslr)

        self.btn_folder = QPushButton("📁 Open Folder with RAW Files")
        self.btn_folder.setFixedSize(350, 50)
        self.btn_folder.setStyleSheet(
            "font-weight: bold; background-color: #2b2b2b; color: #ffffff; border: 1px solid #444444; border-radius: 5px;"
        )
        self.btn_folder.clicked.connect(on_folder_click)
        layout.addWidget(self.btn_folder)

        self.lbl_status = QLabel("Select an input source to begin your scanning session.")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(self.lbl_status)