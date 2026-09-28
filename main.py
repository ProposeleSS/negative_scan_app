import sys
import os
from PyQt6.QtWidgets import QApplication
from app_controller import MainApp

def configure_environment():
    """
    Optimizes system paths and locks C-extensions to prevent 
    multithreading memory leak crashes during RAW post-processing.
    """
    # Prevent rawpy/OpenCV library clashes on certain desktop kernels
    os.environ["OPENCV_VIDEOIO_PRIORITY_INTEL_mfx"] = "0"
    
    # Disable gPhoto2 standard lockouts if another process claimed the USB port
    os.environ["I_MUT_EXCL"] = "1"

if __name__ == "__main__":
    # Initialize optimization flags
    configure_environment()

    # Create the core application instance
    app = QApplication(sys.argv)
    
    # Set the native cross-platform rendering aesthetic
    app.setStyle("Fusion")
    
    # Instantiate and display the centralized orchestration brain window
    window = MainApp()
    window.show()
    
    # Start the desktop runtime loops
    sys.exit(app.exec())