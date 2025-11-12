"""
Webcam Control Application with Effects
Real-time camera preview with v4l2 controls and OpenCV effects
"""

import sys
import subprocess
import re
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QSlider, QLabel, QComboBox, QPushButton,
                              QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap


class VideoThread(QThread):
    """Thread for capturing and processing video frames"""
    change_pixmap = pyqtSignal(QImage)
    
    def __init__(self):
        super().__init__()
        self.device = None
        self.running = False
        self.mirror = False
        self.flip = False
        self.rotate = 0  # 0, 90, 180, 270
        self.effect = 'none'
        
    def set_device(self, device):
        """Set video device"""
        device_num = int(device.replace('/dev/video', ''))
        self.device = device_num
        
    def run(self):
        """Capture and process video frames"""
        if self.device is None:
            return
            
        cap = cv2.VideoCapture(self.device)
        if not cap.isOpened():
            print(f"Failed to open camera {self.device}")
            return
            
        self.running = True
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue
                
            # Apply transformations
            if self.mirror:
                frame = cv2.flip(frame, 1)
            if self.flip:
                frame = cv2.flip(frame, 0)
                
            # Apply rotation
            if self.rotate == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif self.rotate == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif self.rotate == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            # Apply effects
            frame = self.apply_effect(frame)
            
            # Convert to QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.change_pixmap.emit(qt_image.copy())
            
        cap.release()
        
    def apply_effect(self, frame):
        """Apply selected effect to frame"""
        if self.effect == 'none':
            return frame
            
        elif self.effect == 'blur':
            return cv2.GaussianBlur(frame, (15, 15), 0)
            
        elif self.effect == 'edge':
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
        elif self.effect == 'cartoon':
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.medianBlur(gray, 5)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                         cv2.THRESH_BINARY, 9, 9)
            color = cv2.bilateralFilter(frame, 9, 300, 300)
            return cv2.bitwise_and(color, color, mask=edges)
            
        elif self.effect == 'sepia':
            kernel = np.array([[0.272, 0.534, 0.131],
                              [0.349, 0.686, 0.168],
                              [0.393, 0.769, 0.189]])
            return cv2.transform(frame, kernel)
            
        elif self.effect == 'negative':
            return cv2.bitwise_not(frame)
            
        elif self.effect == 'grayscale':
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
        elif self.effect == 'emboss':
            kernel = np.array([[0, -1, -1],
                              [1, 0, -1],
                              [1, 1, 0]])
            return cv2.filter2D(frame, -1, kernel) + 128
            
        elif self.effect == 'sharpen':
            kernel = np.array([[0, -1, 0],
                              [-1, 5, -1],
                              [0, -1, 0]])
            return cv2.filter2D(frame, -1, kernel)
            
        return frame
        
    def stop(self):
        """Stop video capture"""
        self.running = False
        self.wait()


class WebcamController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_device = None
        self.controls = {}
        self.video_thread = VideoThread()
        self.video_thread.change_pixmap.connect(self.update_frame)
        self.init_ui()
        self.detect_cameras()
        
    def init_ui(self):
        self.setWindowTitle("Webcam Controller with Effects")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #212121;")
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left panel - Controls
        control_panel = QWidget()
        control_panel.setStyleSheet("""
            QWidget {
                background-color: #303030;
                border-radius: 15px;
            }
        """)
        control_panel.setMinimumWidth(280)
        control_panel.setMaximumWidth(320)
        
        control_main_layout = QVBoxLayout(control_panel)
        control_main_layout.setContentsMargins(15, 15, 15, 15)
        control_main_layout.setSpacing(10)
        
        # Camera selection
        camera_label = QLabel("Camera Source")
        camera_label.setStyleSheet("""
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI';
            padding: 5px 0px;
        """)
        
        self.camera_combo = QComboBox()
        self.camera_combo.setStyleSheet("""
            QComboBox {
                background-color: #303030;
                color: #ffffff;
                padding: 8px 10px;
                border: 1px solid #444444;
                border-radius: 5px;
                font-size: 13px;
                font-family: 'Segoe UI';
            }
            QComboBox:hover {
                border: 1px solid #3992d1;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #303030;
                color: #ffffff;
                border: 1px solid #444444;
                selection-background-color: #3992d1;
                selection-color: #ffffff;
            }
        """)
        self.camera_combo.currentTextChanged.connect(self.change_camera)
        
        control_main_layout.addWidget(camera_label)
        control_main_layout.addWidget(self.camera_combo)
        control_main_layout.addSpacing(10)
        
        # Video Effects
        effects_label = QLabel("Video Effects")
        effects_label.setStyleSheet("""
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI';
            padding: 5px 0px;
        """)
        
        self.effects_combo = QComboBox()
        self.effects_combo.addItems(['None', 'Blur', 'Edge Detection', 'Cartoon', 
                                     'Sepia', 'Negative', 'Grayscale', 'Emboss', 'Sharpen'])
        self.effects_combo.setStyleSheet(self.camera_combo.styleSheet())
        self.effects_combo.currentTextChanged.connect(self.change_effect)
        
        control_main_layout.addWidget(effects_label)
        control_main_layout.addWidget(self.effects_combo)
        control_main_layout.addSpacing(10)
        
        # Transform controls
        transform_label = QLabel("Video Transform")
        transform_label.setStyleSheet("""
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI';
            padding: 5px 0px;
        """)
        
        transform_container = QWidget()
        transform_container.setStyleSheet("background-color: transparent;")
        transform_layout = QVBoxLayout(transform_container)
        transform_layout.setSpacing(8)
        transform_layout.setContentsMargins(0, 0, 0, 0)
        
        # Row 1: Mirror and Flip
        row1 = QWidget()
        row1.setStyleSheet("background-color: transparent;")
        row1_layout = QHBoxLayout(row1)
        row1_layout.setSpacing(5)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        
        self.mirror_btn = QPushButton("↔ Mirror")
        self.flip_btn = QPushButton("↕ Flip")
        
        # Row 2: Rotate
        row2 = QWidget()
        row2.setStyleSheet("background-color: transparent;")
        row2_layout = QHBoxLayout(row2)
        row2_layout.setSpacing(5)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        
        self.rotate_btn = QPushButton("↻ Rotate 90°")
        
        button_style = """
            QPushButton {
                background-color: #505050;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:checked {
                background-color: #3992d1;
            }
        """
        
        self.mirror_btn.setCheckable(True)
        self.flip_btn.setCheckable(True)
        
        for btn in [self.mirror_btn, self.flip_btn, self.rotate_btn]:
            btn.setStyleSheet(button_style)
            
        self.mirror_btn.clicked.connect(self.toggle_mirror)
        self.flip_btn.clicked.connect(self.toggle_flip)
        self.rotate_btn.clicked.connect(self.rotate_video)
        
        row1_layout.addWidget(self.mirror_btn)
        row1_layout.addWidget(self.flip_btn)
        row2_layout.addWidget(self.rotate_btn)
        
        transform_layout.addWidget(row1)
        transform_layout.addWidget(row2)
        
        control_main_layout.addWidget(transform_label)
        control_main_layout.addWidget(transform_container)
        control_main_layout.addSpacing(10)
        
        # Scroll area for v4l2 controls
        scroll_label = QLabel("Camera Controls")
        scroll_label.setStyleSheet("""
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI';
            padding: 5px 0px;
        """)
        control_main_layout.addWidget(scroll_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #252525;
                width: 10px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3992d1;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2f80c0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Controls container
        self.controls_container = QWidget()
        self.controls_container.setStyleSheet("background-color: transparent;")
        self.controls_layout = QVBoxLayout(self.controls_container)
        self.controls_layout.setSpacing(15)
        self.controls_layout.setContentsMargins(0, 0, 5, 0)
        
        scroll_area.setWidget(self.controls_container)
        control_main_layout.addWidget(scroll_area)
        
        # Right panel - Video preview
        video_container = QWidget()
        video_container.setStyleSheet("""
            QWidget {
                background-color: #303030;
                border-radius: 15px;
            }
        """)
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(20, 20, 20, 20)
        
        self.video_label = QLabel()
        self.video_label.setStyleSheet("""
            background-color: #252525;
            border-radius: 10px;
        """)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setScaledContents(True)
        video_layout.addWidget(self.video_label)
        
        # Add to main layout
        main_layout.addWidget(control_panel)
        main_layout.addWidget(video_container, stretch=1)
        
    def detect_cameras(self):
        """Detect available cameras with capture capability"""
        try:
            result = subprocess.run(
                ['bash', '-c', 
                 'for device in /dev/video*; do udevadm info "$device" 2>/dev/null | '
                 '{ grep -q "CAPABILITIES=.*:capture:" && echo "$device" ;}; done'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            devices = [d.strip() for d in result.stdout.split('\n') if d.strip()]
            
            if devices:
                for device in devices:
                    device_name = self.get_device_name(device)
                    self.camera_combo.addItem(f"{device} ({device_name})", device)
            else:
                self.camera_combo.addItem("No cameras detected", None)
                
        except Exception as e:
            print(f"Error detecting cameras: {e}")
            self.camera_combo.addItem("Error detecting cameras", None)
    
    def get_device_name(self, device):
        """Get friendly name for video device"""
        try:
            result = subprocess.run(
                ['v4l2-ctl', '-d', device, '--info'],
                capture_output=True,
                text=True,
                timeout=2
            )
            for line in result.stdout.split('\n'):
                if 'Card type' in line:
                    return line.split(':', 1)[1].strip()
        except:
            pass
        return "Unknown"
    
    def change_camera(self, selection):
        """Change active camera"""
        device = self.camera_combo.currentData()
        if not device or device == self.current_device:
            return
            
        self.current_device = device
        self.load_controls()
        self.start_camera()
    
    def start_camera(self):
        """Start camera preview with OpenCV"""
        if self.video_thread.running:
            self.video_thread.stop()
            
        self.video_thread.set_device(self.current_device)
        self.video_thread.start()
    
    def update_frame(self, image):
        """Update video frame in label"""
        self.video_label.setPixmap(QPixmap.fromImage(image))
    
    def change_effect(self, effect_name):
        """Change video effect"""
        effect_map = {
            'None': 'none',
            'Blur': 'blur',
            'Edge Detection': 'edge',
            'Cartoon': 'cartoon',
            'Sepia': 'sepia',
            'Negative': 'negative',
            'Grayscale': 'grayscale',
            'Emboss': 'emboss',
            'Sharpen': 'sharpen'
        }
        self.video_thread.effect = effect_map.get(effect_name, 'none')
    
    def toggle_mirror(self):
        """Toggle horizontal mirror"""
        self.video_thread.mirror = self.mirror_btn.isChecked()
    
    def toggle_flip(self):
        """Toggle vertical flip"""
        self.video_thread.flip = self.flip_btn.isChecked()
    
    def rotate_video(self):
        """Rotate video by 90 degrees"""
        self.video_thread.rotate = (self.video_thread.rotate + 90) % 360
        rotation_text = f"↻ Rotate 90°"
        if self.video_thread.rotate != 0:
            rotation_text += f" ({self.video_thread.rotate}°)"
        self.rotate_btn.setText(rotation_text)
    
    def load_controls(self):
        """Load v4l2 controls for current device"""
        # Clear existing controls
        while self.controls_layout.count():
            child = self.controls_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.controls.clear()
        
        try:
            result = subprocess.run(
                ['v4l2-ctl', '-d', self.current_device, '--list-ctrls'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            self.parse_and_create_controls(result.stdout)
            
        except Exception as e:
            error_label = QLabel(f"Error loading controls: {e}")
            error_label.setStyleSheet("""
                color: #ff6b6b;
                font-size: 13px;
                font-family: 'Segoe UI';
                padding: 10px;
            """)
            self.controls_layout.addWidget(error_label)
    
    def parse_and_create_controls(self, output):
        """Parse v4l2-ctl output and create control widgets"""
        lines = output.split('\n')
        
        for line in lines:
            if not line.strip() or 'User Controls' in line or 'Camera Controls' in line:
                continue
                
            # Parse control line
            match = re.match(r'\s*(\w+)\s+0x\w+\s+\((\w+)\)\s*:\s*min=(-?\d+)\s+max=(-?\d+).*default=(-?\d+)\s+value=(-?\d+)', line)
            
            if match:
                name, ctrl_type, min_val, max_val, default_val, current_val = match.groups()
                
                if ctrl_type == 'int' and 'inactive' not in line and 'flags=has-payload' not in line:
                    self.create_slider_control(
                        name, 
                        int(min_val), 
                        int(max_val), 
                        int(current_val),
                        int(default_val)
                    )
            
            # Parse boolean controls
            elif '(bool)' in line and 'inactive' not in line:
                match = re.match(r'\s*(\w+)\s+0x\w+\s+\(bool\)\s*:\s*default=(\d+)\s+value=(\d+)', line)
                if match:
                    name, default_val, current_val = match.groups()
                    self.create_slider_control(name, 0, 1, int(current_val), int(default_val))
        
        # Add stretch at the end
        self.controls_layout.addStretch()
    
    def create_slider_control(self, name, min_val, max_val, current_val, default_val):
        """Create a slider control for a camera parameter"""
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Top row with label and reset button
        top_row = QWidget()
        top_row.setStyleSheet("background-color: transparent;")
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(5)
        
        # Label with current value
        label = QLabel(f"{name.replace('_', ' ').title()}: {current_val}")
        label.setStyleSheet("""
            color: #ffffff;
            font-size: 13px;
            font-family: 'Segoe UI';
            font-weight: normal;
        """)
        
        # Reset button
        reset_btn = QPushButton("↺")
        reset_btn.setFixedSize(28, 28)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #505050;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #3992d1;
            }
        """)
        
        top_layout.addWidget(label)
        top_layout.addStretch()
        top_layout.addWidget(reset_btn)
        
        # Slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(current_val)
        slider.setMinimumHeight(30)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #252525;
                height: 6px;
                border-radius: 3px;
                border: 1px solid #444444;
            }
            QSlider::handle:horizontal {
                background: #3992d1;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
                border: 2px solid #2f80c0;
            }
            QSlider::handle:horizontal:hover {
                background: #2f80c0;
                border: 2px solid #1f6fa0;
            }
            QSlider::sub-page:horizontal {
                background: #3992d1;
                border-radius: 3px;
            }
        """)
        
        # Connect slider to v4l2 control
        slider.valueChanged.connect(
            lambda value, n=name, l=label: self.update_control(n, value, l)
        )
        
        reset_btn.clicked.connect(lambda _, s=slider, d=default_val: s.setValue(d))
        
        layout.addWidget(top_row)
        layout.addWidget(slider)
        
        self.controls_layout.addWidget(container)
        self.controls[name] = {'slider': slider, 'label': label, 'default': default_val}
    
    def update_control(self, control_name, value, label):
        """Update v4l2 control in real-time"""
        if not self.current_device:
            return
            
        label.setText(f"{control_name.replace('_', ' ').title()}: {value}")
        
        # Use subprocess for fastest execution
        try:
            subprocess.run(
                ['v4l2-ctl', '-d', self.current_device, '--set-ctrl', f'{control_name}={value}'],
                capture_output=True,
                timeout=0.1
            )
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            print(f"Error setting {control_name}: {e}")
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.video_thread.running:
            self.video_thread.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = WebcamController()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
