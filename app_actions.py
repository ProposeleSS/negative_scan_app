# app_actions.py
import os
from PyQt6.QtWidgets import QFileDialog
from app_ui_helpers import UIHelpers

class AppActions:
    @staticmethod
    def toggle_crop_view(window):
        """Swaps layout view modes between the full frame or zoomed crop."""
        window.engine.is_crop_committed = window.workspace.btn_commit_crop.isChecked()
        if window.engine.is_crop_committed:
            window.workspace.btn_commit_crop.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 6px;")
            window.workspace.lbl_canvas.hide_overlay_lines = True
        else:
            window.workspace.btn_commit_crop.setStyleSheet("background-color: #e65100; color: white; font-weight: bold; padding: 6px;")
            window.workspace.lbl_canvas.hide_overlay_lines = False
        window.update_pipeline()

    @staticmethod
    def toggle_inversion(window):
        window.engine.is_inverted = window.workspace.btn_invert.isChecked()
        color = "#007acc" if window.engine.is_inverted else "#3a3a3a"
        window.workspace.btn_invert.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; padding: 6px;")
        window.update_pipeline()

    @staticmethod
    def toggle_monochrome(window):
        window.engine.is_monochrome = window.workspace.btn_mono.isChecked()
        color = "#007acc" if window.engine.is_monochrome else "#3a3a3a"
        window.workspace.btn_mono.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold; padding: 6px;")
        window.update_pipeline()

    @staticmethod
    def execute_auto_balance(window):
        dr, dg, db = window.engine.calculate_grey_world_offsets()
        UIHelpers.toggle_all_sliders(window, False)
        window.workspace.sld_cr.setValue(max(-100, min(dr, 100)))
        window.workspace.sld_mg.setValue(max(-100, min(dg, 100)))
        window.workspace.sld_yb.setValue(max(-100, min(db, 100)))
        window.workspace.sld_exp.setValue(0)
        UIHelpers.toggle_all_sliders(window, True)
        window.update_pipeline()

    @staticmethod
    def execute_reset(window):
        UIHelpers.toggle_all_sliders(window, False)
        window.engine.is_crop_committed = False
        
        window.workspace.btn_commit_crop.setChecked(False)
        window.workspace.btn_commit_crop.setStyleSheet("background-color: #e65100; color: white; font-weight: bold; padding: 6px;")
        window.workspace.btn_mono.setChecked(False)
        window.workspace.btn_mono.setStyleSheet("background-color: #3a3a3a; color: white; font-weight: bold; padding: 6px;")
        window.workspace.btn_invert.setChecked(True)
        window.workspace.btn_invert.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 6px;")
        window.workspace.lbl_canvas.hide_overlay_lines = False
        
        for sld in [window.workspace.sld_crop_t, window.workspace.sld_crop_b, window.workspace.sld_crop_l, window.workspace.sld_crop_r,
                    window.workspace.sld_cr, window.workspace.sld_mg, window.workspace.sld_yb, window.workspace.sld_exp, window.workspace.sld_contrast]:
            sld.setValue(0)
        UIHelpers.toggle_all_sliders(window, True)
        window.update_pipeline()