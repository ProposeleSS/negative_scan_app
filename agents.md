# OpenFilmScan - Multi-Agent Architecture & Pipeline System

This document maps out the system roles, component state boundaries, and real-time execution flows of the OpenFilmScan suite. Use this as a blueprint when refactoring components, patching bugs, or extending capabilities.

---

## System Component Topology

The application is decoupled into independent, single-responsibility modules to maximize frame processing performance and eliminate thread lockout regressions.

* main.py ➔ Bootstrapper & UX Theme Launcher
* app_controller.py ➔ Window State Orchestrator
* app_handlers.py ➔ Hotkeys & File Scanner
* app_ui_helpers.py ➔ Slider Callback Utilities
* ui.py ➔ Umbrella Hub File 
* ui_views.py ➔ Wizard & Workspace Layout Panels
* ui_widgets.py ➔ Interactive Canvas & Histogram Painter
* engine.py ➔ Dual-Buffer Core Image Processing Engine

---

## Module Responsibilities & System Roles

### 1. The Orchestrator (app_controller.py & main.py)
* Role: Central window lifecycle holder and routing station.
* State Rules: 
  * Holds the master asset file list array (self.file_list) and index tracking integers.
  * Intercepts visual triggers from custom layout panes and maps them directly to backend computing methods.
  * Implements the performance optimization loop: mouse drag gesture inputs change side UI slider markers and redraw local visual highlighting box guides instantly, while the computational image engine pass triggers exclusively after mouse drag actions are released.

### 2. The Keyboard & IO Specialist (app_handlers.py)
* Role: Direct interactive hotkey parser and operating system folder index directory lookup scanner.
* State Rules:
  * Maps the Top Row (Q, W, E, R, T) to increase Red, Green, Blue, Exposure, and Contrast properties sequentially.
  * Maps the Bottom Row (A, S, D, F, G) to subtract values/introduce complementary CMYK balances sequentially.
  * Filters incoming file tracks strictly against camera RAW configurations (.CR2, .NEF, .ARW, .DNG, etc.) to generate clean path tracks.

### 3. The Visual Layouts Hub (ui.py, ui_views.py, ui_widgets.py)
* Role: User interfaces and custom canvas rendering logic.
* State Rules:
  * WizardView dictates initial device setup modes (disabled DSLR vs. active folder target picking).
  * InteractiveCanvas implements custom tracking methods, switching cursor shapes dynamically when mouse vectors land inside the four edge trim handle zone margins.
  * HistogramWidget bypasses expensive graphing dependencies, calculating Red, Green, and Blue frequency distributions via NumPy and utilizing a dedicated QPainter layout loop to draw clean paths.

### 4. The Computational Image Core (engine.py)
* Role: Matrix computations, dynamic ranges transformations, and data serialization.
* State Rules:
  * Dual-Buffer Architecture: On file ingestion, creates an active preview cache downsampled to a maximum bounding threshold constraint of 1280 pixels. Real-time sliders adjustments and live histogram distributions execute instantly on this lightweight buffer matrix to ensure lag-free performance.
  * Production Master: The full-resolution master RAW image grid stays pristine in memory. Heavy color/contrast transformation pipelines run on the full-scale matrix only at the moment export_full_resolution is triggered by a file save.
  * Memory Safety Pass: Sliced arrays (Region of Interest crops) generate non-contiguous views in memory. This core must explicitly flatten arrays using .tobytes() or continuous allocations before mapping to QImage formats to prevent system execution crashes.

---

## Planned State Pipeline Extensions

### Phase A: Asynchronous Hardware Control (QThread)
* A background hardware agent running on a decoupled thread away from PyQt's main loop.
* Uses gphoto2 bindings to safely query USB ports, wake camera shutter operations asynchronously, and stream incoming raw files directly into the active folder track array.

### Phase B: C-41 Matrix Calibration Auto-Gains
* A sub-pipeline algorithm executing post-inversion to normalize color negative dye layer shifts.
* Scans individual channel highlights to establish targeted white point modifiers before global adjustments occur.