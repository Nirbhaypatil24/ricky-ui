"""
Sharing Mode UI - Animated Passenger Cards
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QFrame, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor

CARD_OFF = "#1C1C1E"
CARD_ON = "#0A2A12"
ACCENT_GOLD = "#FFD700"
TEXT_WHITE = "#FFFFFF"

class AnimatedPassengerCard(QFrame):
    def __init__(self, passenger_id):
        super().__init__()
        self.passenger_id = passenger_id
        self.setup_ui()
        self.current_state = False
        
    def setup_ui(self):
        self.setFixedSize(200, 180)
        self.setStyleSheet(f"background-color: {CARD_OFF}; border-radius: 15px; border: 1px solid #333;")
        
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
        self.status_lbl.setStyleSheet("background-color: #3A3A3C; color: white; border-radius: 4px; padding: 4px;")
        self.status_lbl.setFixedWidth(80)
        
        box = QHBoxLayout()
        box.addStretch()
        box.addWidget(self.status_lbl)
        box.addStretch()
        
        layout.addWidget(self.header_lbl)
        layout.addStretch()
        layout.addWidget(self.fare_lbl)
        layout.addWidget(self.stats_lbl)
        layout.addStretch()
        layout.addLayout(box)
        self.setLayout(layout)

    def trigger_board_animation(self, onboard):
        """Animates card background color"""
        if onboard:
            start_col, end_col = QColor(CARD_OFF), QColor(CARD_ON)
            border_col = "#34C759"
        else:
            start_col, end_col = QColor(CARD_ON), QColor(CARD_OFF)
            border_col = "#333"

        # Note: We simulate color animation by setting stylesheet directly 
        # as QPropertyAnimation on stylesheet is complex in PyQT5
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {end_col.name()};
                border-radius: 15px;
                border: 2px solid {border_col};
            }}
        """)
        
        # Flash Effect
        self.flash_anim = QPropertyAnimation(self, b"windowOpacity") # dummy property
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        
        anim = QPropertyAnimation(self.effect, b"opacity")
        anim.setDuration(300)
        anim.setStartValue(0.5)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()

    def update_data(self, fare, status_text, is_active):
        if is_active != self.current_state:
            self.trigger_board_animation(is_active)
            self.current_state = is_active
            
        self.fare_lbl.setText(f"₹{fare:.0f}")
        self.status_lbl.setText(status_text)
        
        if is_active:
            self.status_lbl.setStyleSheet("background-color: #34C759; color: white; border-radius: 4px;")
            self.fare_lbl.setStyleSheet(f"color: {ACCENT_GOLD}; font-size: 36px; font-weight: bold;")
        else:
            self.status_lbl.setStyleSheet("background-color: #3A3A3C; color: white; border-radius: 4px;")
            self.fare_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 36px; font-weight: bold;")

    def update_live_info(self, distance):
        self.stats_lbl.setText(f"{distance:.1f} km")

class SharingModeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        card_layout = QHBoxLayout()
        card_layout.setSpacing(15)
        card_layout.setAlignment(Qt.AlignCenter)
        
        for i in range(3):
            card = AnimatedPassengerCard(i + 1)
            self.cards.append(card)
            card_layout.addWidget(card)
            
        self.info_lbl = QLabel("Multi-Passenger Tracking Active")
        self.info_lbl.setAlignment(Qt.AlignCenter)
        self.info_lbl.setStyleSheet("color: #8E8E93; font-size: 12px; margin-top: 10px;")
        
        layout.addLayout(card_layout)
        layout.addWidget(self.info_lbl)
        self.setLayout(layout)

    def update_passenger(self, pid, onboard):
        if 0 <= pid < 3:
            curr_fare = float(self.cards[pid].fare_lbl.text().replace('₹',''))
            self.cards[pid].update_data(curr_fare, "OCCUPIED" if onboard else "EMPTY", onboard)

    def update_fare(self, pid, fare):
        if 0 <= pid < 3:
            self.cards[pid].update_data(fare, "OCCUPIED", True)

    def update_total_info(self, dist, time):
        self.info_lbl.setText(f"Trip Distance: {dist:.1f} km • Waiting: {time} min")

    def update_card_live_data(self, pid, dist, start_time):
        if 0 <= pid < 3:
            self.cards[pid].update_live_info(dist)