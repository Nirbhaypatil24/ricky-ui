"""
Ads/Map Display - Ricky Theme
Dark container for rotating content
Updated: Added ad_3 and ad_4 to rotation (10s each)
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QStackedWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QMovie, QPixmap, QPainter, QBrush, QColor

# NOTE: Do NOT import MapDisplayWidget here to avoid circular loop

class DriverInfoWidget(QFrame):
    """Widget to display driver details and photo nicely"""
    def __init__(self, name, number, photo_path):
        super().__init__()
        self.setFixedHeight(140) 
        self.setStyleSheet("""
            QFrame {
                background-color: #2C2C2E;
                border-radius: 10px;
                margin-bottom: 5px;
            }
        """)
        self.setup_ui(name, number, photo_path)

    def setup_ui(self, name, number, photo_path):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)

        # 1. Circular Photo
        photo_size = 110
        photo_label = QLabel()
        photo_label.setFixedSize(photo_size, photo_size)
        
        pixmap = QPixmap(photo_path)
        if pixmap.isNull():
            # Fallback if photo missing
            pixmap = QPixmap(photo_size, photo_size)
            pixmap.fill(QColor("#555555"))
        
        # Create circular mask for photo
        circular_pixmap = QPixmap(photo_size, photo_size)
        circular_pixmap.fill(Qt.transparent)
        painter = QPainter(circular_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(pixmap.scaled(photo_size, photo_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, photo_size, photo_size)
        painter.end()
        
        photo_label.setPixmap(circular_pixmap)
        layout.addWidget(photo_label)

        # 2. Text Details
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        text_layout.setAlignment(Qt.AlignVCenter)
        
        lbl_driver_title = QLabel("YOUR DRIVER")
        lbl_driver_title.setStyleSheet("color: #8E8E93; font-size: 16px; font-weight: bold; letter-spacing: 1px;")
        
        lbl_name = QLabel(name.upper())
        lbl_name.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        
        lbl_number = QLabel(f"ph : {number}")
        lbl_number.setStyleSheet("color: #34C759; font-size: 28px; font-weight: 500;")
        
        text_layout.addWidget(lbl_driver_title)
        text_layout.addWidget(lbl_name)
        text_layout.addWidget(lbl_number)
        
        layout.addLayout(text_layout)
        layout.addStretch()

class AdsDisplayWidget(QWidget):
    content_changed = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.current_index = 0
        self.ad_duration = 10000   # 10 seconds per ad
        self.map_duration = 30000  # 30 seconds for map/driver info
        
        # Define assets path
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_path = os.path.join(self.base_path, 'assets')
        
        # FIX: Import MapDisplayWidget HERE to avoid circular import
        from .map_display import MapDisplayWidget
        self.map_widget = MapDisplayWidget()
        
        self.setup_ui()
        self.load_content()
        
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_content)
        self.start_rotation()
    
    def setup_ui(self):
        # Set size policy to expand
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 0, 5, 5)
        
        # Main Container Frame
        main_container = QFrame()
        main_container.setStyleSheet("""
            QFrame {
                background-color: #1C1C1E;
                border-radius: 10px;
                border: 1px solid #333;
            }
        """)
        main_container_layout = QVBoxLayout(main_container)
        main_container_layout.setContentsMargins(5, 5, 5, 5)
        
        self.display_stack = QStackedWidget()
        
        # --- Load Assets ---
        gif_path_1 = os.path.join(self.assets_path, 'ad_1.gif')
        gif_path_2 = os.path.join(self.assets_path, 'ad_2.gif')
        gif_path_3 = os.path.join(self.assets_path, 'ad_3.gif')
        gif_path_4 = os.path.join(self.assets_path, 'ad_4.gif')
        driver_photo_path = os.path.join(self.assets_path, 'driver_pic.avif')

        # --- Create Stack Views ---
        
        # View 1: First GIF Ad (ad_1.gif)
        self.ad_gif_1 = self.create_image_ad(gif_path_1)
        
        # View 2: Driver Info + Map Combined View
        map_view_container = QWidget()
        map_view_layout = QVBoxLayout(map_view_container)
        map_view_layout.setContentsMargins(0, 0, 0, 0)
        map_view_layout.setSpacing(0)
        
        # Create driver info header widget
        self.driver_header = DriverInfoWidget(
            name="CHANDU",
            number="1234567890",
            photo_path=driver_photo_path
        )
        
        map_view_layout.addWidget(self.driver_header)
        # Add map widget with stretch factor to fill remaining space
        map_view_layout.addWidget(self.map_widget, 1)
        
        # View 3: Second GIF Ad (ad_2.gif)
        self.ad_gif_2 = self.create_image_ad(gif_path_2)

        # View 4: Third GIF Ad (ad_3.gif)
        self.ad_gif_3 = self.create_image_ad(gif_path_3)

        # View 5: Fourth GIF Ad (ad_4.gif)
        self.ad_gif_4 = self.create_image_ad(gif_path_4)
        
        # Add views to stack (Order must match load_content)
        self.display_stack.addWidget(self.ad_gif_1)       # Index 0
        self.display_stack.addWidget(map_view_container)  # Index 1 (Driver + Map)
        self.display_stack.addWidget(self.ad_gif_2)       # Index 2
        self.display_stack.addWidget(self.ad_gif_3)       # Index 3
        self.display_stack.addWidget(self.ad_gif_4)       # Index 4
        
        main_container_layout.addWidget(self.display_stack)
        layout.addWidget(main_container)
        self.setLayout(layout)

    def create_image_ad(self, image_path):
        """Create an ad from an image or GIF"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #000000; border-radius: 10px;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel()
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        if os.path.exists(image_path):
            if image_path.lower().endswith('.gif'):
                movie = QMovie(image_path)
                lbl.setMovie(movie)
                movie.start()
                lbl.setScaledContents(True) 
            else:
                pixmap = QPixmap(image_path)
                lbl.setPixmap(pixmap)
                lbl.setScaledContents(True)
        else:
            lbl.setText(f"Ad Missing:\n{os.path.basename(image_path)}")
            lbl.setStyleSheet("color: #8E8E93; font-size: 18px; font-weight: bold;")
        
        layout.addWidget(lbl)
        return frame

    def load_content(self):
        """Define the rotation sequence and duration"""
        self.content_items = [
            {"type": "ad_1",          "dur": self.ad_duration},    # 0: ad_1.gif
            {"type": "driver_map",    "dur": self.map_duration},   # 1: Driver Info + Map
            {"type": "ad_2",          "dur": self.ad_duration},    # 2: ad_2.gif
            {"type": "ad_3",          "dur": self.ad_duration},    # 3: ad_3.gif
            {"type": "ad_4",          "dur": self.ad_duration}     # 4: ad_4.gif
        ]

    def rotate_content(self):
        self.current_index = (self.current_index + 1) % len(self.content_items)
        self.display_stack.setCurrentIndex(self.current_index)
        
        duration = self.content_items[self.current_index]["dur"]
        self.rotation_timer.setInterval(duration)

    def start_rotation(self):
        self.rotation_timer.start(self.content_items[0]["dur"])
        
    def stop_rotation(self):
        self.rotation_timer.stop()
