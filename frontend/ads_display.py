"""
Ads/Map Display - Ricky Theme (Animated)
"""

import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QStackedWidget, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from .map_display import MapDisplayWidget

class FadeStack(QStackedWidget):
    """Simple Fade Stack for Ads"""
    def setCurrentIndex(self, index):
        curr = self.currentWidget()
        next_w = self.widget(index)
        if not curr or curr == next_w:
            super().setCurrentIndex(index)
            return

        self.effect_out = QGraphicsOpacityEffect(curr)
        self.effect_in = QGraphicsOpacityEffect(next_w)
        curr.setGraphicsEffect(self.effect_out)
        next_w.setGraphicsEffect(self.effect_in)
        
        super().setCurrentIndex(index)
        curr.show()
        
        self.anim = QParallelAnimationGroup()
        a1 = QPropertyAnimation(self.effect_out, b"opacity")
        a1.setStartValue(1.0); a1.setEndValue(0.0); a1.setDuration(500)
        a2 = QPropertyAnimation(self.effect_in, b"opacity")
        a2.setStartValue(0.0); a2.setEndValue(1.0); a2.setDuration(500)
        self.anim.addAnimation(a1); self.anim.addAnimation(a2)
        self.anim.finished.connect(lambda: self._clean(curr, next_w))
        self.anim.start()
        
    def _clean(self, o, n):
        o.hide(); o.setGraphicsEffect(None); n.setGraphicsEffect(None)

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
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0,0,0,0)
        
        self.display_stack = FadeStack() # Use FadeStack
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
        l1 = QLabel(title)
        l1.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        l1.setAlignment(Qt.AlignCenter)
        l2 = QLabel(subtitle)
        l2.setStyleSheet("color: white; font-size: 16px;")
        l2.setAlignment(Qt.AlignCenter)
        layout.addWidget(l1); layout.addWidget(l2)
        frame.setLayout(layout)
        return frame

    def load_content(self):
        self.content_items = [{"type": "ad", "dur": self.ad_duration}, {"type": "map", "dur": self.map_duration}, {"type": "ad", "dur": self.ad_duration}]

    def rotate_content(self):
        self.current_index = (self.current_index + 1) % len(self.content_items)
        self.display_stack.setCurrentIndex(self.current_index)
        duration = self.content_items[self.current_index]["dur"]
        self.rotation_timer.setInterval(duration)

    def start_rotation(self):
        self.rotation_timer.start(self.content_items[0]["dur"])
        
    def stop_rotation(self):
        self.rotation_timer.stop()