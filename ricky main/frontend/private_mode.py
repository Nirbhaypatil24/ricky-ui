"""
Private Mode UI - Vertical Layout for Left Panel
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSlot

THEME_TEXT = "#FFFFFF"
THEME_ACCENT = "#FFD700"
CARD_BG = "#1C1C1E"

class PrivateModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 1. Main Fare Display (Big)
        self.fare_frame = QFrame()
        self.fare_frame.setStyleSheet(f"background: {CARD_BG}; border: 2px solid {THEME_ACCENT}; border-radius: 15px;")
        f_layout = QVBoxLayout(self.fare_frame)
        
        lbl_title = QLabel("TOTAL FARE")
        lbl_title.setStyleSheet(f"color: {THEME_ACCENT}; font-size: 16px; font-weight: bold; letter-spacing: 2px; background: transparent;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        self.fare_val = QLabel("₹0.00")
        self.fare_val.setStyleSheet(f"color: {THEME_TEXT}; font-size: 64px; font-weight: bold; background: transparent;")
        self.fare_val.setAlignment(Qt.AlignCenter)
        
        f_layout.addWidget(lbl_title)
        f_layout.addWidget(self.fare_val)
        
        # 2. Stats Row
        stats_layout = QHBoxLayout()
        self.dist_card = self.create_stat("DISTANCE", "0.0 km")
        self.time_card = self.create_stat("TIME", "0 min")
        
        stats_layout.addWidget(self.dist_card)
        stats_layout.addWidget(self.time_card)
        
        layout.addWidget(self.fare_frame, 2)
        layout.addLayout(stats_layout, 1)
        self.setLayout(layout)

    def create_stat(self, t, v):
        f = QFrame()
        f.setStyleSheet(f"background: {CARD_BG}; border-radius: 10px; border: 1px solid #333;")
        l = QVBoxLayout(f)
        
        val = QLabel(v)
        val.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: transparent;")
        val.setAlignment(Qt.AlignCenter)
        
        ttl = QLabel(t)
        ttl.setStyleSheet("color: #888; font-size: 10px; font-weight: bold; background: transparent;")
        ttl.setAlignment(Qt.AlignCenter)
        
        l.addWidget(val)
        l.addWidget(ttl)
        
        if t == "DISTANCE": self.d_lbl = val
        if t == "TIME": self.t_lbl = val
        return f

    @pyqtSlot(float)
    def update_fare(self, f): self.fare_val.setText(f"₹{f:.2f}")
    
    def update_distance(self, d): self.d_lbl.setText(f"{d:.1f} km")
    
    def update_duration(self, m): 
        if m>=60: self.t_lbl.setText(f"{m//60}h {m%60}m")
        else: self.t_lbl.setText(f"{m} min")