"""
Sharing Mode UI - Fit to Length
Seats expand to fill vertical space
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSlot

# Theme Constants
CARD_BG = "#1C1C1E"
CARD_ACTIVE = "#142615"
TEXT_WHITE = "#FFFFFF"
ACCENT_GOLD = "#FFD700"
TEXT_SUB = "#8E8E93"

class PassengerSlimCard(QFrame):
    def __init__(self, passenger_id):
        super().__init__()
        self.passenger_id = passenger_id
        self.setup_ui()
    
    def setup_ui(self):
        # Vital: Policy Expanding ensures it grabs vertical space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(10)
        
        # 1. Seat ID
        self.id_lbl = QLabel(f"{self.passenger_id}")
        self.id_lbl.setFixedSize(50, 50)
        self.id_lbl.setAlignment(Qt.AlignCenter)
        self.id_lbl.setStyleSheet(f"background: #333; color: white; border-radius: 25px; font-weight: bold; font-size: 20px;")
        
        # 2. Fare & Info
        mid_layout = QVBoxLayout()
        mid_layout.setSpacing(0)
        mid_layout.setAlignment(Qt.AlignVCenter)
        
        self.fare_lbl = QLabel("₹0")
        self.fare_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 36px; font-weight: bold; background: transparent;")
        
        self.dist_lbl = QLabel("0.0 km")
        self.dist_lbl.setStyleSheet(f"color: {TEXT_SUB}; font-size: 16px; background: transparent;")
        
        mid_layout.addWidget(self.fare_lbl)
        mid_layout.addWidget(self.dist_lbl)
        
        # 3. Status
        self.status_lbl = QLabel("EMPTY")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setFixedSize(100, 36)
        self.status_lbl.setStyleSheet("background: #3A3A3C; color: #AAA; border-radius: 18px; font-weight: bold; font-size: 14px;")
        
        layout.addWidget(self.id_lbl)
        layout.addSpacing(15)
        layout.addLayout(mid_layout)
        layout.addStretch()
        layout.addWidget(self.status_lbl)
        
        self.setLayout(layout)
        self.set_style(False)
        
    def set_style(self, active):
        if active:
            self.setStyleSheet(f"QFrame {{ background-color: {CARD_ACTIVE}; border: 2px solid #34C759; border-radius: 15px; }}")
            self.id_lbl.setStyleSheet("background: #34C759; color: white; border-radius: 25px; font-weight: bold; font-size: 20px;")
            self.fare_lbl.setStyleSheet(f"color: {ACCENT_GOLD}; font-size: 36px; font-weight: bold; background: transparent;")
            self.status_lbl.setText("ONBOARD")
            self.status_lbl.setStyleSheet("background: #34C759; color: white; border-radius: 18px; font-weight: bold;")
        else:
            self.setStyleSheet(f"QFrame {{ background-color: {CARD_BG}; border: 1px solid #333; border-radius: 15px; }}")
            self.id_lbl.setStyleSheet("background: #333; color: white; border-radius: 25px; font-weight: bold; font-size: 20px;")
            self.fare_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 36px; font-weight: bold; background: transparent;")
            self.status_lbl.setText("EMPTY")
            self.status_lbl.setStyleSheet("background: #3A3A3C; color: #AAA; border-radius: 18px; font-weight: bold;")

    def update_data(self, fare, onboard):
        self.fare_lbl.setText(f"₹{fare:.0f}")
        self.set_style(onboard)

    def update_live_info(self, distance):
        self.dist_lbl.setText(f"{distance:.1f} km")

class SharingModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.setup_ui()
    
    def setup_ui(self):
        # Vertical Layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add cards with Stretch Factor 1 to expand equally
        for i in range(3):
            card = PassengerSlimCard(i + 1)
            self.cards.append(card)
            layout.addWidget(card, 1) # '1' ensures equal vertical stretching
        
        # Info Footer (Minimal height)
        self.info_lbl = QLabel("TRIP: 0.0 km")
        self.info_lbl.setFixedHeight(20)
        self.info_lbl.setStyleSheet("color: #666; font-weight: bold; font-size: 12px;")
        self.info_lbl.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.info_lbl, 0)
        self.setLayout(layout)

    def update_passenger(self, pid, onboard):
        if 0 <= pid < 3:
            try: f = float(self.cards[pid].fare_lbl.text().replace('₹',''))
            except: f = 0.0
            self.cards[pid].update_data(f, onboard)

    def update_fare(self, pid, fare):
        if 0 <= pid < 3: self.cards[pid].update_data(fare, True)

    def update_total_info(self, t, w):
        self.info_lbl.setText(f"TOTAL: {t:.1f} km • WAIT: {w} min")

    def update_card_live_data(self, pid, d):
        if 0 <= pid < 3: self.cards[pid].update_live_info(d)