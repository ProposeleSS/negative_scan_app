import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from app_controller import MainApp

def apply_dark_monochrome_palette(app):
    """Overrides system accessibility rules to enforce a strict dark charcoal profile."""
    app.setStyle("Fusion")
    
    dark_palette = QPalette()
    
    # Core surface colors (Deep Anthracite Charcoal)
    bg_dark = QColor(26, 26, 26)       # #1a1a1a window background
    panel_dark = QColor(43, 43, 43)    # #2b2b2b boxes and fields
    text_light = QColor(220, 220, 220) # Clean off-white
    text_muted = QColor(136, 136, 136) # Medium grey for hints
    
    # Set the Window and General Widget States
    dark_palette.setColor(QPalette.ColorRole.Window, bg_dark)
    dark_palette.setColor(QPalette.ColorRole.WindowText, text_light)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, bg_dark)
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, text_light)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, text_light)
    
    # Text states
    dark_palette.setColor(QPalette.ColorRole.Text, text_light)
    dark_palette.setColor(QPalette.ColorRole.Button, panel_dark)
    dark_palette.setColor(QPalette.ColorRole.ButtonText, text_light)
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    
    # Selection and Muted/Disabled states
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(74, 74, 74))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(74, 74, 74))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, text_muted)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, text_muted)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, text_muted)
    
    app.setPalette(dark_palette)
    
    # Inject application-wide style tweaks to override native button behaviors
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1a1a1a;
        }
        QGroupBox {
            border: 1px solid #333333;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: bold;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 4px;
        }
        QPushButton {
            background-color: #2b2b2b;
            color: #dddddd;
            border: 1px solid #3d3d3d;
            font-weight: bold;
            padding: 6px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #383838;
            border: 1px solid #555555;
        }
        QPushButton:pressed {
            background-color: #1f1f1f;
            color: #ffffff;
        }
        QPushButton:checked {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #666666;
        }
        QLineEdit {
            background-color: #121212;
            color: #aaaaaa;
            border: 1px solid #333333;
            padding: 4px;
            border-radius: 4px;
        }
    """)

if __name__ == "__main__":
    os.environ["OPENCV_VIDEOIO_PRIORITY_INTEL_mfx"] = "0"
    os.environ["I_MUT_EXCL"] = "1"

    app = QApplication(sys.argv)
    
    # Enforce the master palette mask override
    apply_dark_monochrome_palette(app)
    
    window = MainApp()
    window.show()
    sys.exit(app.exec())