"""
UI Manager - Ricky Theme + Animations
Includes SOS Pulse & Smooth Page Transitions
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QStackedWidget, QLabel, QFrame, 
                           QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PyQt5.QtGui import QFont, QPixmap, QColor

from .sharing_mode import SharingModeWidget
from .private_mode import PrivateModeWidget
from .ads_display import AdsDisplayWidget

# --- THEME CONSTANTS ---
THEME_BG = "#000000"
THEME_ACCENT = "#FFD700"
THEME_CARD_BG = "#1C1C1E"

class FadingStackedWidget(QStackedWidget):
    """Custom Stacked Widget with Cross-Fade Animation"""
    def __init__(self):
        super().__init__()
        self.fade_anim = None

    def setCurrentIndex(self, index):
        self.fade_transition(index)

    def fade_transition(self, index):
        if index == self.currentIndex():
            return

        current_widget = self.currentWidget()
        next_widget = self.widget(index)
        
        if not current_widget or not next_widget:
            super().setCurrentIndex(index)
            return

        # Setup fade effect
        self.effect = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0)
        
        super().setCurrentIndex(index)
        
        # Animate opacity
        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(300)  # 300ms fade
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.start(QAbstractAnimation.DeleteWhenStopped)

class SOSStatusWidget(QFrame):
    """Animated SOS Status Bar"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_status = "Normal"
        
        # Animation Timer
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate_alarm)
        self.flash_state = False
    
    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME_CARD_BG};
                border-radius: 10px;
                margin: 5px;
            }}
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 8, 15, 8)
        
        self.status_icon = QLabel("🛡️")
        self.status_icon.setFont(QFont("Arial", 20))
        
        self.status_label = QLabel("SYSTEM MONITORING ACTIVE")
        self.status_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.status_label.setStyleSheet("color: #34C759; border: none;") # Green
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_label, 1)
        self.setLayout(layout)
    
    def update_status(self, status):
        self.current_status = status
        status_upper = status.upper()
        
        if "SOS" in status_upper and ("COUNTDOWN" in status_upper or "ACTIVATED" in status_upper):
            if not self.anim_timer.isActive():
                self.anim_timer.start(500) # Flash every 500ms
            
            self.status_label.setText(f"🚨 {status_upper} 🚨")
            self.status_icon.setText("⚠️")
        else:
            self.anim_timer.stop()
            self.setStyleSheet(f"background-color: {THEME_CARD_BG}; border-radius: 10px;")
            self.status_label.setText("SYSTEM MONITORING ACTIVE")
            self.status_label.setStyleSheet("color: #34C759; border: none;")
            self.status_icon.setText("🛡️")

    def animate_alarm(self):
        """Toggles background between Red and Dark Red"""
        if self.flash_state:
            bg_color = "#FF3B30" # Bright Red
            text_color = "white"
        else:
            bg_color = "#590000" # Dark Red
            text_color = "#FFD700" # Gold
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                margin: 5px;
                border: 2px solid #FF0000;
            }}
        """)
        self.status_label.setStyleSheet(f"color: {text_color}; border: none;")
        self.flash_state = not self.flash_state

class RickyUI(QMainWindow):
    """Main UI Manager with Animations"""
    
    def __init__(self, fare_calculator, mode_controller, sos_system):
        super().__init__()
        self.fare_calculator = fare_calculator
        self.mode_controller = mode_controller
        self.sos_system = sos_system
        self.gps_manager = fare_calculator.gps_manager
        self.current_mode = "For Hire"
        
        self.setup_ui()
        self.setup_timers()
        self.setup_gps_connections()
        print("🖥️ Ricky UI (Animated) initialized")

    def setup_ui(self):
        self.setWindowTitle("Ricky Smart Autometer")
        self.setGeometry(0, 0, 800, 480)
        self.setStyleSheet(f"QMainWindow {{ background-color: {THEME_BG}; font-family: 'Arial'; }}")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- HEADER (Static) ---
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"background-color: {THEME_BG}; border-bottom: 2px solid #333;")
        header_layout = QHBoxLayout(header)
        
        # Logo with Fade-In Animation
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'Ricky Logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaledToHeight(50, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            
            # Simple fade in for logo
            self.logo_effect = QGraphicsOpacityEffect(logo_label)
            logo_label.setGraphicsEffect(self.logo_effect)
            self.logo_anim = QPropertyAnimation(self.logo_effect, b"opacity")
            self.logo_anim.setDuration(1500)
            self.logo_anim.setStartValue(0)
            self.logo_anim.setEndValue(1)
            self.logo_anim.start()
        else:
            logo_label.setText("Ricky")
            logo_label.setStyleSheet("color: white; font-size: 30px; font-weight: bold;")
        
        self.mode_label = QLabel("FOR HIRE")
        self.mode_label.setStyleSheet(f"color: {THEME_ACCENT}; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.mode_label)
        
        # --- BODY (Animated Stack) ---
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(10, 10, 10, 10)
        
        self.mode_stack = FadingStackedWidget() # Uses custom class
        
        self.sharing_widget = SharingModeWidget()
        self.private_widget = PrivateModeWidget()
        self.for_hire_widget = self.create_placeholder("🚕 FOR HIRE", "Ready for passengers", "#34C759")
        self.waiting_widget = self.create_placeholder("⏸️ WAITING", "Driver on break", "#8E8E93")
        
        self.mode_stack.addWidget(self.sharing_widget)
        self.mode_stack.addWidget(self.private_widget)
        self.mode_stack.addWidget(self.for_hire_widget)
        self.mode_stack.addWidget(self.waiting_widget)
        
        self.sos_widget = SOSStatusWidget() # Animated
        self.ads_widget = AdsDisplayWidget() # Animated
        
        body_layout.addWidget(self.mode_stack, stretch=3)
        body_layout.addWidget(self.sos_widget, stretch=0)
        body_layout.addWidget(self.ads_widget, stretch=2)
        
        main_layout.addWidget(header)
        main_layout.addLayout(body_layout)
        central_widget.setLayout(main_layout)
        
        self.update_mode("For Hire")

    def create_placeholder(self, title, sub, color):
        w = QWidget()
        l = QVBoxLayout()
        l.setAlignment(Qt.AlignCenter)
        t = QLabel(title)
        t.setStyleSheet(f"color: {color}; font-size: 40px; font-weight: bold;")
        s = QLabel(sub)
        s.setStyleSheet("color: #8E8E93; font-size: 18px;")
        
        if "HIRE" in title: self.for_hire_subtitle = s
        elif "WAITING" in title: self.waiting_subtitle = s
            
        l.addWidget(t)
        l.addWidget(s)
        w.setLayout(l)
        return w

    def setup_gps_connections(self):
        self.gps_manager.speed_updated.connect(self._on_gps_speed_update)
        self.gps_manager.distance_updated.connect(self._on_gps_distance_update)
        self.fare_calculator.distance_updated.connect(self._on_distance_update)
        self.fare_calculator.duration_updated.connect(self._on_duration_update)

    def setup_timers(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.realtime_gps_update)
        self.update_timer.start(2000)
        self.fast_update_timer = QTimer()
        self.fast_update_timer.timeout.connect(self.fast_update)
        self.fast_update_timer.start(1000)

    # --- Slots & Logic (Unchanged Backend Integration) ---
    @pyqtSlot(float)
    def _on_gps_speed_update(self, s): self.current_speed = s
    @pyqtSlot(float)
    def _on_gps_distance_update(self, d): self.current_distance = d
    @pyqtSlot(float)
    def _on_distance_update(self, d): 
        if self.current_mode == "Private": self.private_widget.update_distance(d)
    @pyqtSlot(int)
    def _on_duration_update(self, m): 
        if self.current_mode == "Private": self.private_widget.update_duration(m)

    @pyqtSlot(str)
    def update_mode(self, mode):
        self.current_mode = mode
        self.mode_label.setText(mode.upper())
        mapping = {"Sharing": 0, "Private": 1, "For Hire": 2, "Waiting": 3}
        if mode in mapping:
            self.mode_stack.setCurrentIndex(mapping[mode])
            if mode == "Private": self.fare_calculator.start_private_mode()
            elif self.current_mode == "Private" and mode != "Private": self.fare_calculator.stop_private_mode()

    @pyqtSlot(int, bool)
    def update_passenger(self, pid, onboard):
        if self.current_mode == "Sharing": self.sharing_widget.update_passenger(pid, onboard)

    @pyqtSlot(int, float)
    def update_fares(self, pid, fare):
        if self.current_mode == "Sharing": self.sharing_widget.update_fare(pid, fare)
        elif self.current_mode == "Private": self.private_widget.update_fare(fare)

    @pyqtSlot(str)
    def update_sos_status(self, status): self.sos_widget.update_status(status)

    def realtime_gps_update(self):
        try:
            stats = self.fare_calculator.get_real_time_stats()
            if self.current_mode == "Sharing":
                dist = stats['total_distance']
                wait = max(0, int(stats['trip_duration'] - (dist / max(stats['current_speed'], 1) * 60)))
                self.sharing_widget.update_total_info(dist, wait)
            elif self.current_mode == "For Hire":
                self.for_hire_subtitle.setText(f"GPS: {'Locked' if stats['gps_fix'] else 'Searching'} • {stats['current_speed']:.1f} km/h")
        except: pass

    def fast_update(self):
        if self.current_mode == "Sharing":
            for pid in range(3):
                p = self.fare_calculator.passengers[pid]
                if p['onboard']:
                    self.sharing_widget.update_card_live_data(pid, p['total_distance'], p['start_time'])