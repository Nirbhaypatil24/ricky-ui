"""
Ads Display - Animated Transitions
"""

import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QStackedWidget, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
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
        self.setFixedHeight(180)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        container = QFrame()
        container.setStyleSheet("background-color: #1C1C1E; border-radius: 10px; border: 1px solid #333;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0,0,0,0)
        
        self.stack = QStackedWidget()
        self.ad1 = self.create_ad("🍔 HUNGRY?", "Order via Zomato", "#D32F2F")
        self.ad2 = self.create_ad("⚡ FAST TRAVEL", "Book next ride on Uber", "#1976D2")
        
        self.stack.addWidget(self.ad1)
        self.stack.addWidget(self.map_widget)
        self.stack.addWidget(self.ad2)
        
        c_layout.addWidget(self.stack)
        layout.addWidget(container)
        self.setLayout(layout)
    
    def create_ad(self, t, s, c):
        f = QFrame()
        f.setStyleSheet(f"background-color: {c}; border-radius: 10px;")
        l = QVBoxLayout()
        l.setAlignment(Qt.AlignCenter)
        lt = QLabel(t)
        lt.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        ls = QLabel(s)
        ls.setStyleSheet("color: white; font-size: 16px;")
        l.addWidget(lt)
        l.addWidget(ls)
        f.setLayout(l)
        return f

    def load_content(self):
        self.items = [
            {"type": "ad", "dur": self.ad_duration},
            {"type": "map", "dur": self.map_duration},
            {"type": "ad", "dur": self.ad_duration}
        ]

    def rotate_content(self):
        """Cross-fade to next item"""
        next_idx = (self.current_index + 1) % len(self.items)
        
        # Simple crossfade logic
        next_widget = self.stack.widget(next_idx)
        effect = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(effect)
        
        self.anim = QPropertyAnimation(effect, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.stack.setCurrentIndex(next_idx)
        self.anim.start()
        
        self.current_index = next_idx
        self.rotation_timer.setInterval(self.items[self.current_index]["dur"])

    def start_rotation(self):
        self.rotation_timer.start(self.items[0]["dur"])
        
    def stop_rotation(self):
        self.rotation_timer.stop()