# engine.py
import cv2
import numpy as np
import rawpy
import os

class ImageEngine:
    def __init__(self):
        self.original_img = None           # Continuous full-resolution master RAW matrix
        self.preview_src = None           # Lightweight performance optimization buffer
        self.processed_preview = None     # Core full overview display buffer
        self.processed_roi = None         # Isolated cropped region matrix buffer
        self.is_monochrome = False
        self.is_inverted = True
        self.is_crop_committed = False
        self.rotation_angle = 0

    def load_file(self, filepath):
        while isinstance(filepath, (tuple, list)):
            if len(filepath) > 0: filepath = filepath
            else: return False
                
        filepath = str(filepath)
        _, ext_raw = os.path.splitext(filepath)
        ext = ext_raw.lower()
        raw_extensions = ('.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.rw2', '.raf')

        try:
            if ext in raw_extensions:
                with rawpy.imread(filepath) as raw:
                    rgb = raw.postprocess(use_camera_wb=False, half_size=False, no_auto_bright=True)
                    self.original_img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            else:
                self.original_img = cv2.imread(filepath)
                
            if self.original_img is None:
                return False

            # Cache the lightweight execution view layer (Max threshold: 1280px dimension)
            h, w = self.original_img.shape[:2]
            max_dim = 1280
            if max(h, w) > max_dim:
                scale = max_dim / float(max(h, w))
                self.preview_src = cv2.resize(self.original_img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
            else:
                self.preview_src = self.original_img.copy()

            self.rotation_angle = 0
            return True
        except Exception as e:
            print(f"Error loading file {filepath}: {e}")
            return False

    def rotate_image(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        return self.rotation_angle

    def run_math_pipeline(self, src_matrix, cr, mg, yb, exp, contrast):
        if src_matrix is None:
            return None

        # Geometric transformations check
        if self.rotation_angle == 90:
            rotated = cv2.rotate(src_matrix, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.rotation_angle == 180:
            rotated = cv2.rotate(src_matrix, cv2.ROTATE_180)
        elif self.rotation_angle == 270:
            rotated = cv2.rotate(src_matrix, cv2.ROTATE_90_CLOCKWISE)
        else:
            rotated = src_matrix.copy()

        # Inversion pass
        if self.is_inverted:
            working = 255 - rotated.astype(np.int32)
        else:
            working = rotated.copy().astype(np.int32)

        # Balance multipliers
        b, g, r = cv2.split(working)
        r = r + cr + exp
        g = g + mg + exp
        b = b + yb + exp

        # Midpoint contrast expansion matrix
        factor = 1.0 + (contrast / 33.3) if contrast >= 0 else 1.0 + (contrast / 111.0)
        r = np.clip(128.0 + factor * (r - 128.0), 0, 255)
        g = np.clip(128.0 + factor * (g - 128.0), 0, 255)
        b = np.clip(128.0 + factor * (b - 128.0), 0, 255)

        corrected = cv2.merge([b, g, r]).astype(np.uint8)

        if self.is_monochrome:
            gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)
            corrected = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        return corrected

    def process_preview_frame(self, cr, mg, yb, exp, contrast, crop_t, crop_b, crop_l, crop_r):
        if self.preview_src is None:
            return None

        self.processed_preview = self.run_math_pipeline(self.preview_src, cr, mg, yb, exp, contrast)
        
        # Explicit crop boundary constraints clipping protections
        h, w = self.processed_preview.shape[:2]
        t_pct = max(0, min(crop_t, 45))
        b_pct = max(0, min(crop_b, 45))
        l_pct = max(0, min(crop_l, 45))
        r_pct = max(0, min(crop_r, 45))

        top = int(h * (t_pct / 100.0))
        bottom = h - int(h * (b_pct / 100.0))
        left = int(w * (l_pct / 100.0))
        right = w - int(w * (r_pct / 100.0))

        if bottom > top + 20 and right > left + 20:
            self.processed_roi = self.processed_preview[top:bottom, left:right]
        else:
            self.processed_roi = self.processed_preview.copy()

        if self.is_crop_committed:
            return self.processed_roi
        return self.processed_preview

    def get_histogram_arrays(self):
        if self.processed_roi is None: 
            return None
        b_hist = cv2.calcHist([self.processed_roi], [0], None, [256], [0, 256]).flatten()
        g_hist = cv2.calcHist([self.processed_roi], [1], None, [256], [0, 256]).flatten()
        r_hist = cv2.calcHist([self.processed_roi], [2], None, [256], [0, 256]).flatten()
        return r_hist, g_hist, b_hist

    def calculate_grey_world_offsets(self):
        if self.processed_roi is None: 
            return 0, 0, 0
        b_mean, g_mean, r_mean = cv2.mean(self.processed_roi)[:3]
        if b_mean == 0 or g_mean == 0 or r_mean == 0: 
            return 0, 0, 0
        avg_mean = (b_mean + g_mean + r_mean) / 3.0
        return int(avg_mean - r_mean), int(avg_mean - g_mean), int(avg_mean - b_mean)

    def export_full_resolution(self, save_path, cr, mg, yb, exp, contrast, crop_t, crop_b, crop_l, crop_r):
        if self.original_img is None:
            return False

        full_output = self.run_math_pipeline(self.original_img, cr, mg, yb, exp, contrast)
        
        h, w, ch = full_output.shape
        t_pct = max(0, min(crop_t, 45))
        b_pct = max(0, min(crop_b, 45))
        l_pct = max(0, min(crop_l, 45))
        r_pct = max(0, min(crop_r, 45))

        top = int(h * (t_pct / 100.0))
        bottom = h - int(h * (b_pct / 100.0))
        left = int(w * (l_pct / 100.0))
        right = w - int(w * (r_pct / 100.0))

        if bottom > top + 20 and right > left + 20:
            final_crop = full_output[top:bottom, left:right]
        else:
            final_crop = full_output

        # FIX: Force a continuous memory layout block so OpenCV writes the file successfully
        contiguous_output = np.ascontiguousarray(final_crop)
        return cv2.imwrite(save_path, contiguous_output)