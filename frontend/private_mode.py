"""
Private Mode UI - Ricky Theme
Large digital dashboard style
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont

# Theme Colors
BG_COLOR = "#000000"
CARD_BG = "#1C1C1E"
ACCENT_COLOR = "#FFD700"  # Gold
TEXT_MAIN = "#FFFFFF"
TEXT_SUB = "#8E8E93"

class PrivateModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # --- Top Row: Stats ---
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Distance Card
        self.dist_card = self.create_stat_card("DISTANCE", "0.0 km")
        # Time Card
        self.time_card = self.create_stat_card("DURATION", "0 min")
        
        stats_layout.addWidget(self.dist_card)
        stats_layout.addWidget(self.time_card)
        
        # --- Main Fare Display ---
        self.fare_frame = QFrame()
        self.fare_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 2px solid {ACCENT_COLOR};
                border-radius: 20px;
                padding: 20px;
            }}
        """)
        fare_layout = QVBoxLayout(self.fare_frame)
        
        fare_title = QLabel("TOTAL FARE")
        fare_title.setStyleSheet(f"color: {ACCENT_COLOR}; font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        fare_title.setAlignment(Qt.AlignCenter)
        
        self.fare_amount = QLabel("₹0.00")
        self.fare_amount.setAlignment(Qt.AlignCenter)
        self.fare_amount.setStyleSheet(f"""
            color: {TEXT_MAIN};
            font-size: 64px;
            font-weight: bold;
        """)
        
        fare_layout.addWidget(fare_title)
        fare_layout.addWidget(self.fare_amount)
        
        layout.addLayout(stats_layout)
        layout.addWidget(self.fare_frame)
        self.setLayout(layout)

    def create_stat_card(self, title, initial_value):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {CARD_BG}; border-radius: 15px; padding: 10px;")
        vbox = QVBoxLayout(frame)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {TEXT_SUB}; font-size: 12px; font-weight: bold;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        lbl_value = QLabel(initial_value)
        lbl_value.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 24px; font-weight: bold;")
        lbl_value.setAlignment(Qt.AlignCenter)
        
        vbox.addWidget(lbl_value)
        vbox.addWidget(lbl_title)
        
        # Store reference to update later
        if title == "DISTANCE": self.lbl_dist_val = lbl_value
        if title == "DURATION": self.lbl_time_val = lbl_value
            
        return frame

    @pyqtSlot(float)
    def update_fare(self, fare):
        self.fare_amount.setText(f"₹{fare:.2f}")
    
    def update_distance(self, distance_km):
        self.lbl_dist_val.setText(f"{distance_km:.1f} km")
    
    def update_duration(self, duration_minutes):
        if duration_minutes >= 60:
            h = int(duration_minutes // 60)
            m = int(duration_minutes % 60)
            self.lbl_time_val.setText(f"{h}h {m}m")
        else:
            self.lbl_time_val.setText(f"{duration_minutes} min")