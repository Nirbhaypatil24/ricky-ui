"""
Sharing Mode UI - Ricky Theme
Individual seat cards in Dark Mode
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSlot

# Theme Constants
CARD_OFF = "#1C1C1E"
CARD_ON = "#142615"  # Very dark green
TEXT_WHITE = "#FFFFFF"
ACCENT_GOLD = "#FFD700"
TEXT_SUB = "#8E8E93"

class PassengerCard(QFrame):
    def __init__(self, passenger_id):
        super().__init__()
        self.passenger_id = passenger_id
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedSize(200, 180)
        self.set_offboard_style()
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Header (Seat Number)
        self.header_lbl = QLabel(f"SEAT {self.passenger_id}")
        self.header_lbl.setAlignment(Qt.AlignCenter)
        self.header_lbl.setStyleSheet(f"color: {TEXT_SUB}; font-size: 14px; font-weight: bold; background: transparent;")
        
        # Fare Display
        self.fare_lbl = QLabel("₹0")
        self.fare_lbl.setAlignment(Qt.AlignCenter)
        self.fare_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 40px; font-weight: bold; background: transparent;")
        
        # Stats
        self.stats_lbl = QLabel("0.0 km")
        self.stats_lbl.setAlignment(Qt.AlignCenter)
        self.stats_lbl.setStyleSheet(f"color: {TEXT_SUB}; font-size: 16px; background: transparent;")
        
        # Status Badge
        self.status_lbl = QLabel("EMPTY")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setFixedWidth(100)
        self.status_lbl.setFixedHeight(24)
        
        # Center status badge
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
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_OFF};
                border-radius: 15px;
                border: 1px solid #333;
            }}
        """)
        self.status_lbl.setStyleSheet("background-color: #3A3A3C; color: white; border-radius: 12px; font-size: 12px; font-weight: bold;")
        self.status_lbl.setText("EMPTY")
        self.fare_lbl.setStyleSheet(f"color: {TEXT_SUB}; font-size: 40px; font-weight: bold; background: transparent;")

    def set_onboard_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_ON};
                border-radius: 15px;
                border: 2px solid #34C759;
            }}
        """)
        self.status_lbl.setStyleSheet("background-color: #34C759; color: white; border-radius: 12px; font-size: 12px; font-weight: bold;")
        self.status_lbl.setText("OCCUPIED")
        self.fare_lbl.setStyleSheet(f"color: {ACCENT_GOLD}; font-size: 40px; font-weight: bold; background: transparent;")

    def update_data(self, fare, onboard):
        self.fare_lbl.setText(f"₹{fare:.0f}")
        
        if onboard:
            self.set_onboard_style()
        else:
            self.set_offboard_style()

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
        
        # Info footer
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        
        self.info_lbl = QLabel("Multi-Passenger Tracking Active")
        self.info_lbl.setAlignment(Qt.AlignCenter)
        self.info_lbl.setStyleSheet("color: #8E8E93; font-size: 14px; margin-top: 10px;")
        main_layout.addWidget(self.info_lbl)
        
        self.setLayout(main_layout)

    def update_passenger(self, pid, onboard):
        if 0 <= pid < 3:
            # Get current fare from text to persist it
            try:
                curr_fare = float(self.cards[pid].fare_lbl.text().replace('₹',''))
            except:
                curr_fare = 0.0
            self.cards[pid].update_data(curr_fare, onboard)

    def update_fare(self, pid, fare):
        if 0 <= pid < 3:
            # We assume if fare is updating, passenger is onboard
            self.cards[pid].update_data(fare, True)

    def update_total_info(self, total_dist, wait_time):
        self.info_lbl.setText(f"Total Trip Distance: {total_dist:.1f} km • Waiting Time: {wait_time} min")

    def update_card_live_data(self, pid, distance):
        if 0 <= pid < 3:
            self.cards[pid].update_live_info(distance)