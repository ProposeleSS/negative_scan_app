from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer

class UIHelpers:
    @staticmethod
    def toggle_all_sliders(window, enable):
        """Disables or enables signal blocks on all adjustment sliders safely."""
        sliders = [
            window.workspace.sld_cr, window.workspace.sld_mg, 
            window.workspace.sld_yb, window.workspace.sld_exp, 
            window.workspace.sld_contrast, window.workspace.sld_crop_t, 
            window.workspace.sld_crop_b, window.workspace.sld_crop_l, 
            window.workspace.sld_crop_r
        ]
        for sld in sliders:
            sld.blockSignals(not enable)

    @staticmethod
    def show_flash_notification(parent_window, message):
        """Spawns a clean, non-blocking notification overlay that fades out automatically."""
        overlay = QLabel(message, parent_window)
        overlay.setStyleSheet(
            "background-color: rgba(46, 125, 50, 230); "
            "color: white; "
            "font-weight: bold; "
            "font-size: 14px;"
            "padding: 12px 24px; "
            "border-radius: 6px;"
        )
        overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        overlay.adjustSize()
        
        # Position the toast box right in the upper center of the viewport window
        x = (parent_window.width() - overlay.width()) // 2
        y = 60
        overlay.move(x, y)
        overlay.show()
        
        # Destroys label container memory safely after 1500 milliseconds
        QTimer.singleShot(1500, overlay.deleteLater)