"""
Ads/Map Display - Ricky Theme
Dark container for rotating content
Updated: Support for multiple GIF Ads (ad_1.gif, ad_2.gif)
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QStackedWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QMovie, QPixmap
from .map_display import MapDisplayWidget

class AdsDisplayWidget(QWidget):
    content_changed = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.current_index = 0
        self.ad_duration = 10000   # 10 seconds per ad
        self.map_duration = 20000  # 20 seconds for map
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
        
        # Container Frame
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1C1C1E;
                border-radius: 10px;
                border: 1px solid #333;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0,0,0,0)
        
        self.display_stack = QStackedWidget()
        
        # Define assets path
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_path = os.path.join(base_path, 'assets')
        
        # 1. First GIF Ad (ad_1.gif) - Akshay Kumar
        gif_path_1 = os.path.join(assets_path, 'ad_1.gif')
        self.ad_gif_1 = self.create_image_ad(gif_path_1)
        
        # 2. Second GIF Ad (ad_2.gif) - Amul
        gif_path_2 = os.path.join(assets_path, 'ad_2.gif')
        self.ad_gif_2 = self.create_image_ad(gif_path_2)
        
        # Add widgets to stack (Order must match load_content)
        self.display_stack.addWidget(self.ad_gif_1)   # Index 0
        self.display_stack.addWidget(self.map_widget) # Index 1
        self.display_stack.addWidget(self.ad_gif_2)   # Index 2
        
        container_layout.addWidget(self.display_stack)
        layout.addWidget(container)
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
                lbl.setScaledContents(True) # Ensure GIF fits the frame
            else:
                pixmap = QPixmap(image_path)
                lbl.setPixmap(pixmap)
                lbl.setScaledContents(True)
        else:
            # Fallback if file not found
            lbl.setText(f"Ad Missing:\n{os.path.basename(image_path)}")
            lbl.setStyleSheet("color: #8E8E93; font-size: 18px; font-weight: bold;")
        
        layout.addWidget(lbl)
        return frame

    def load_content(self):
        """Define the rotation sequence and duration"""
        self.content_items = [
            {"type": "ad_1",    "dur": self.ad_duration},    # 0: ad_1.gif
            {"type": "map",     "dur": self.map_duration},   # 1: Map
            {"type": "ad_2",    "dur": self.ad_duration}     # 2: ad_2.gif
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
