"""
Sharing Mode UI - Ricky Theme (Animated)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QPropertyAnimation
from PyQt5.QtGui import QColor

# Theme Constants
CARD_OFF = "#1C1C1E"
CARD_ON_BASE = "#0A2A12"
CARD_ON_GLOW = "#145224"
TEXT_WHITE = "#FFFFFF"
ACCENT_GOLD = "#FFD700"

class PassengerCard(QFrame):
    def __init__(self, passenger_id):
        super().__init__()
        self.passenger_id = passenger_id
        self.is_active = False
        self.glow_state = False
        self.setup_ui()
        
        # Breathing Animation Timer
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._animate_glow)
    
    def setup_ui(self):
        self.setFixedSize(200, 180)
        self.set_offboard_style()
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        self.header_lbl = QLabel(f"SEAT {self.passenger_id}")
        self.header_lbl.setAlignment(Qt.AlignCenter)
        self.header_lbl.setStyleSheet("color: #8E8E93; font-size: 14px; font-weight: bold;")
        
        self.fare_lbl = QLabel("₹0")
        self.fare_lbl.setAlignment(Qt.AlignCenter)
        self.fare_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 36px; font-weight: bold;")
        
        self.stats_lbl = QLabel("0.0 km")
        self.stats_lbl.setAlignment(Qt.AlignCenter)
        self.stats_lbl.setStyleSheet("color: #8E8E93; font-size: 14px;")
        
        self.status_lbl = QLabel("EMPTY")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setFixedWidth(80)
        
        status_container = QHBoxLayout()
        status_container.addStretch()
        status_container.addWidget(self.status_lbl)
        status_container.addStretch()
        
        layout.addWidget(self.header_lbl)
        layout.addStretch()
        layout.addWidget(self.fare_lbl)
        layout.addWidget(self.stats_lbl)
        layout.addStretch()
        layout.addLayout(status_container)
        self.setLayout(layout)
    
    def set_offboard_style(self):
        self.anim_timer.stop()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_OFF};
                border-radius: 15px;
                border: 1px solid #3A3A3C;
            }}
        """)
        self.status_lbl.setStyleSheet("background-color: #3A3A3C; color: white; border-radius: 4px; padding: 4px; font-size: 12px;")
        
    def set_onboard_style(self):
        if not self.anim_timer.isActive():
            self.anim_timer.start(1000) # Breath every 1 second
        self.status_lbl.setStyleSheet("background-color: #34C759; color: white; border-radius: 4px; padding: 4px; font-size: 12px;")

    def _animate_glow(self):
        # Simple toggle animation for breathing effect
        self.glow_state = not self.glow_state
        bg = CARD_ON_GLOW if self.glow_state else CARD_ON_BASE
        border = ACCENT_GOLD if self.glow_state else "#34C759"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 15px;
                border: 2px solid {border};
            }}
        """)

    def update_data(self, fare, status_text, is_active):
        self.fare_lbl.setText(f"₹{fare:.0f}")
        self.status_lbl.setText(status_text)
        
        if is_active != self.is_active:
            self.is_active = is_active
            if is_active:
                self.set_onboard_style()
                self.fare_lbl.setStyleSheet(f"color: {ACCENT_GOLD}; font-size: 36px; font-weight: bold;")
            else:
                self.set_offboard_style()
                self.fare_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 36px; font-weight: bold;")

    def update_live_info(self, distance):
        self.stats_lbl.setText(f"{distance:.1f} km")

class SharingModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)
        for i in range(3):
            card = PassengerCard(i + 1)
            self.cards.append(card)
            layout.addWidget(card)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        self.info_lbl = QLabel("Multi-Passenger Tracking Active")
        self.info_lbl.setAlignment(Qt.AlignCenter)
        self.info_lbl.setStyleSheet("color: #8E8E93; font-size: 12px; margin-top: 5px;")
        main_layout.addWidget(self.info_lbl)
        self.setLayout(main_layout)

    def update_passenger(self, pid, onboard):
        if 0 <= pid < 3:
            status = "OCCUPIED" if onboard else "EMPTY"
            curr_fare = float(self.cards[pid].fare_lbl.text().replace('₹',''))
            self.cards[pid].update_data(curr_fare, status, onboard)

    def update_fare(self, pid, fare):
        if 0 <= pid < 3: self.cards[pid].update_data(fare, "OCCUPIED", True)
    
    def update_total_info(self, total_dist, wait_time):
        self.info_lbl.setText(f"Total Trip Distance: {total_dist:.1f} km • Waiting: {wait_time} min")

    def update_card_live_data(self, pid, distance, start_time):
        if 0 <= pid < 3: self.cards[pid].update_live_info(distance)