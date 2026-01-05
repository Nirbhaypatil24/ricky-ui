"""
Ads/Map Display - Ricky Theme
Dark container for rotating content
"""

import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from .map_display import MapDisplayWidget

class AdsDisplayWidget(QWidget):
    content_changed = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.current_index = 0
        self.ad_duration = 15000
        self.map_duration = 30000
        self.map_widget = MapDisplayWidget()
        
        self.setup_ui()
        self.load_content()
        
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_content)
        self.start_rotation()
    
    def setup_ui(self):
        self.setFixedHeight(180) # Slightly shorter to fit header
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
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
        
        # Ads (Restyled for dark mode)
        self.ad1 = self.create_ad("🍔 HUNGRY?", "Order via Zomato", "#D32F2F")
        self.ad2 = self.create_ad("⚡ FAST TRAVEL", "Book next ride on Uber", "#1976D2")
        
        self.display_stack.addWidget(self.ad1)
        self.display_stack.addWidget(self.map_widget)
        self.display_stack.addWidget(self.ad2)
        
        container_layout.addWidget(self.display_stack)
        layout.addWidget(container)
        self.setLayout(layout)
    
    def create_ad(self, title, subtitle, color):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {color}; border-radius: 10px;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        lbl_t.setAlignment(Qt.AlignCenter)
        
        lbl_s = QLabel(subtitle)
        lbl_s.setStyleSheet("color: white; font-size: 16px;")
        lbl_s.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(lbl_t)
        layout.addWidget(lbl_s)
        frame.setLayout(layout)
        return frame

    def load_content(self):
        self.content_items = [
            {"type": "ad", "dur": self.ad_duration},
            {"type": "map", "dur": self.map_duration},
            {"type": "ad", "dur": self.ad_duration}
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