"""
Private Mode UI - Animated
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QColor

BG_COLOR = "#000000"
CARD_BG = "#1C1C1E"
ACCENT_COLOR = "#FFD700"

class PrivateModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.last_fare = 0.0
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        stats = QHBoxLayout()
        self.dist_card = self.create_card("DISTANCE", "0.0 km")
        self.time_card = self.create_card("DURATION", "0 min")
        stats.addWidget(self.dist_card)
        stats.addWidget(self.time_card)
        
        self.fare_frame = QFrame()
        self.fare_frame.setStyleSheet(f"background-color: {CARD_BG}; border: 2px solid {ACCENT_COLOR}; border-radius: 20px;")
        f_layout = QVBoxLayout(self.fare_frame)
        
        t = QLabel("TOTAL FARE")
        t.setStyleSheet(f"color: {ACCENT_COLOR}; font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        t.setAlignment(Qt.AlignCenter)
        
        self.fare_amount = QLabel("₹0.00")
        self.fare_amount.setAlignment(Qt.AlignCenter)
        self.fare_amount.setStyleSheet("color: white; font-size: 64px; font-weight: bold;")
        
        f_layout.addWidget(t)
        f_layout.addWidget(self.fare_amount)
        
        layout.addLayout(stats)
        layout.addWidget(self.fare_frame)
        self.setLayout(layout)

    def create_card(self, title, val):
        f = QFrame()
        f.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 15px; padding: 10px;")
        l = QVBoxLayout(f)
        v = QLabel(val)
        v.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        v.setAlignment(Qt.AlignCenter)
        t = QLabel(title)
        t.setStyleSheet("color: #8E8E93; font-size: 12px; font-weight: bold;")
        t.setAlignment(Qt.AlignCenter)
        l.addWidget(v)
        l.addWidget(t)
        
        if title == "DISTANCE": self.lbl_dist = v
        if title == "DURATION": self.lbl_time = v
        return f

    @pyqtSlot(float)
    def update_fare(self, fare):
        if fare != self.last_fare:
            self.fare_amount.setText(f"₹{fare:.2f}")
            self.last_fare = fare
            self.animate_fare_change()
    
    def animate_fare_change(self):
        """Simple text color flash animation"""
        self.fare_amount.setStyleSheet("color: #FFE033; font-size: 64px; font-weight: bold;")
        QTimer.singleShot(200, lambda: self.fare_amount.setStyleSheet("color: white; font-size: 64px; font-weight: bold;"))

    def update_distance(self, d): self.lbl_dist.setText(f"{d:.1f} km")
    def update_duration(self, m):
        if m >= 60: self.lbl_time.setText(f"{int(m//60)}h {int(m%60)}m")
        else: self.lbl_time.setText(f"{m} min")