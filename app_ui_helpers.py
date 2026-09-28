# app_ui_helpers.py
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