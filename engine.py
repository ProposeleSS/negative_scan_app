import cv2
import numpy as np
import rawpy
import os

class ImageEngine:
    def __init__(self):
        self.original_img = None
        self.processed_img = None
        self.is_monochrome = False
        self.is_inverted = True

    def load_file(self, filepath):
        """Automatically handles JPEGs or high-fidelity RAW files."""
        while isinstance(filepath, (tuple, list)):
            if len(filepath) > 0:
                filepath = filepath[0]
            else:
                return False
                
        filepath = str(filepath)
        ext = os.path.splitext(filepath)[1].lower()
        raw_extensions = ('.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.rw2', '.raf')

        try:
            if ext in raw_extensions:
                with rawpy.imread(filepath) as raw:
                    rgb = raw.postprocess(use_camera_wb=False, half_size=False, no_auto_bright=True)
                    self.original_img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            else:
                self.original_img = cv2.imread(filepath)
                
            return self.original_img is not None
        except Exception as e:
            print(f"Error loading image file {filepath}: {e}")
            return False

    def run_pipeline(self, cr, mg, yb, exp, crop_t=0, crop_b=0, crop_l=0, crop_r=0):
        """Processes inversion, asymmetric cropping, color modes, and slider adjustments."""
        if self.original_img is None:
            return None

        # 1. Apply Independent Multi-Side Crop Matrix slicing
        h, w = self.original_img.shape[:2]
        
        top = int(h * (crop_t / 100.0))
        bottom = h - int(h * (crop_b / 100.0))
        left = int(w * (crop_l / 100.0))
        right = w - int(w * (crop_r / 100.0))

        # Core safety verification checks to avoid inverted dimensions crash loops
        if bottom > top and right > left:
            working_src = self.original_img[top:bottom, left:right]
        else:
            working_src = self.original_img

        # 2. Base Negative Inversion
        if self.is_inverted:
            working_img = 255 - working_src.astype(np.int32)
        else:
            working_img = working_src.copy().astype(np.int32)

        # 3. Split channels (BGR)
        b, g, r = cv2.split(working_img)

        # 4. Apply Slider Matrix Corrections
        r = np.clip(r + cr + exp, 0, 255)
        g = np.clip(g + mg + exp, 0, 255)
        b = np.clip(b + yb + exp, 0, 255)

        # 5. Recombine
        processed = cv2.merge([b, g, r]).astype(np.uint8)

        # 6. Handle Monochrome Toggle
        if self.is_monochrome:
            gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            processed = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        self.processed_img = processed
        return self.processed_img

    def get_histogram_arrays(self):
        if self.processed_img is None:
            return None
        b_hist = cv2.calcHist([self.processed_img], [0], None, [256], [0, 256]).flatten()
        g_hist = cv2.calcHist([self.processed_img], [1], None, [256], [0, 256]).flatten()
        r_hist = cv2.calcHist([self.processed_img], [2], None, [256], [0, 256]).flatten()
        return r_hist, g_hist, b_hist

    def calculate_grey_world_offsets(self):
        if self.processed_img is None:
            return 0, 0, 0
        b_mean, g_mean, r_mean = cv2.mean(self.processed_img)[:3]
        if b_mean == 0 or g_mean == 0 or r_mean == 0:
            return 0, 0, 0
        avg_mean = (b_mean + g_mean + r_mean) / 3.0
        return int(avg_mean - r_mean), int(avg_mean - g_mean), int(avg_mean - b_mean)

    def export_current_image(self, save_path):
        if self.processed_img is None:
            return False
        return cv2.imwrite(save_path, self.processed_img)