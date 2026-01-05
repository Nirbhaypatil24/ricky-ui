"""
UI Manager - Ricky Theme (Animated Edition)
Includes smooth transitions and SOS pulse effects
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QStackedWidget, QLabel, QFrame, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PyQt5.QtGui import QFont, QPixmap, QColor, QPalette

from .sharing_mode import SharingModeWidget
from .private_mode import PrivateModeWidget
from .ads_display import AdsDisplayWidget

# --- RICKY THEME CONSTANTS ---
THEME_BG = "#000000"
THEME_ACCENT = "#FFD700"
THEME_TEXT = "#FFFFFF"
THEME_DANGER = "#FF3B30"
THEME_SUCCESS = "#34C759"
THEME_CARD_BG = "#1C1C1E"

class FadeStackedWidget(QStackedWidget):
    """Custom StackedWidget with Fade Transition"""
    def __init__(self):
        super().__init__()
        self.fade_anim = None

    def setCurrentIndex(self, index):
        self.fade_transition(index)

    def fade_transition(self, index):
        current_widget = self.currentWidget()
        next_widget = self.widget(index)
        
        if not current_widget or current_widget == next_widget:
            super().setCurrentIndex(index)
            return

        # Setup effects
        self.effect_out = QGraphicsOpacityEffect(current_widget)
        self.effect_in = QGraphicsOpacityEffect(next_widget)
        current_widget.setGraphicsEffect(self.effect_out)
        next_widget.setGraphicsEffect(self.effect_in)
        
        # Ensure next widget is visible for animation
        super().setCurrentIndex(index)
        current_widget.show() # Keep previous visible during crossfade
        
        # Create animations
        self.anim_out = QPropertyAnimation(self.effect_out, b"opacity")
        self.anim_out.setDuration(300)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.OutQuad)
        
        self.anim_in = QPropertyAnimation(self.effect_in, b"opacity")
        self.anim_in.setDuration(300)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.InQuad)
        
        # Group
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.anim_out)
        self.anim_group.addAnimation(self.anim_in)
        self.anim_group.finished.connect(lambda: self._cleanup(current_widget, next_widget))
        self.anim_group.start()

    def _cleanup(self, old_w, new_w):
        old_w.hide()
        old_w.setGraphicsEffect(None)
        new_w.setGraphicsEffect(None)

class SOSStatusWidget(QFrame):
    """Animated SOS Widget with Flashing Effect"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_status = "Normal"
        
        # Animation Timer for Flashing
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self._toggle_flash)
        self.flash_state = False
    
    def setup_ui(self):
        self.setStyleSheet(f"background-color: {THEME_CARD_BG}; border-radius: 10px; margin: 5px;")
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_icon = QLabel("🛡️")
        self.status_icon.setFont(QFont("Arial", 20))
        
        self.status_label = QLabel("SYSTEM NORMAL")
        self.status_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.status_label.setStyleSheet(f"color: {THEME_SUCCESS}; border: none;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_label, 1)
        self.setLayout(layout)
    
    def update_status(self, status):
        self.current_status = status
        status_upper = status.upper()
        
        if "SOS" in status_upper and ("COUNTDOWN" in status_upper or "ACTIVATED" in status_upper):
            self.status_label.setText(f"🚨 {status_upper} 🚨")
            if not self.flash_timer.isActive():
                self.flash_timer.start(500) # Flash every 500ms
        else:
            self.flash_timer.stop()
            self.setStyleSheet(f"background-color: {THEME_CARD_BG}; border-radius: 10px; margin: 5px;")
            self.status_label.setText("SYSTEM ACTIVE")
            self.status_label.setStyleSheet(f"color: {THEME_SUCCESS}; border: none;")
            self.status_icon.setText("🛡️")

    def _toggle_flash(self):
        self.flash_state = not self.flash_state
        if self.flash_state:
            self.setStyleSheet(f"background-color: {THEME_DANGER}; border-radius: 10px; margin: 5px; border: 2px solid white;")
            self.status_label.setStyleSheet("color: white; border: none;")
        else:
            self.setStyleSheet(f"background-color: #8B0000; border-radius: 10px; margin: 5px;") # Dark Red
            self.status_label.setStyleSheet("color: #FFCCCC; border: none;")

class RickyUI(QMainWindow):
    """Main UI with Animations"""
    
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
        self.setStyleSheet(f"QMainWindow {{ background-color: {THEME_BG}; }} QWidget {{ font-family: 'Arial'; }}")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- HEADER ---
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"background-color: {THEME_BG}; border-bottom: 2px solid {THEME_CARD_BG};")
        header_layout = QHBoxLayout(header)
        
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'Ricky Logo.png')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaledToHeight(50, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("Ricky")
            logo_label.setStyleSheet("color: white; font-size: 30px; font-weight: bold;")
        
        self.mode_label = QLabel("FOR HIRE")
        self.mode_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.mode_label.setStyleSheet(f"color: {THEME_ACCENT}; font-size: 24px; font-weight: bold; letter-spacing: 2px;")
        
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.mode_label)
        
        # --- BODY ---
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(10, 10, 10, 10)
        
        # Use Custom Fade Stack
        self.mode_stack = FadeStackedWidget()
        
        self.sharing_widget = SharingModeWidget()
        self.private_widget = PrivateModeWidget()
        self.for_hire_widget = self.create_placeholder_widget("🚕 FOR HIRE", "Ready for passengers", THEME_SUCCESS)
        self.waiting_widget = self.create_placeholder_widget("⏸️ WAITING", "Driver on break", "#8E8E93")
        
        self.mode_stack.addWidget(self.sharing_widget)
        self.mode_stack.addWidget(self.private_widget)
        self.mode_stack.addWidget(self.for_hire_widget)
        self.mode_stack.addWidget(self.waiting_widget)
        
        self.sos_widget = SOSStatusWidget()
        self.ads_widget = AdsDisplayWidget()
        
        body_layout.addWidget(self.mode_stack, stretch=3)
        body_layout.addWidget(self.sos_widget, stretch=0)
        body_layout.addWidget(self.ads_widget, stretch=2)
        
        main_layout.addWidget(header)
        main_layout.addLayout(body_layout)
        central_widget.setLayout(main_layout)
        self.update_mode("For Hire")

    def create_placeholder_widget(self, title, subtitle, color):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {color}; font-size: 40px; font-weight: bold;")
        title_lbl.setAlignment(Qt.AlignCenter)
        
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("color: #8E8E93; font-size: 18px;")
        sub_lbl.setAlignment(Qt.AlignCenter)
        
        if "HIRE" in title: self.for_hire_subtitle = sub_lbl
        elif "WAITING" in title: self.waiting_subtitle = sub_lbl
            
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)
        widget.setLayout(layout)
        return widget

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

    @pyqtSlot(float)
    def _on_gps_speed_update(self, speed): self.current_speed = speed
    @pyqtSlot(float)
    def _on_gps_distance_update(self, dist): self.current_distance = dist
    @pyqtSlot(float)
    def _on_distance_update(self, dist): 
        if self.current_mode == "Private": self.private_widget.update_distance(dist)
    @pyqtSlot(int)
    def _on_duration_update(self, mins): 
        if self.current_mode == "Private": self.private_widget.update_duration(mins)

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
    def update_sos_status(self, status):
        self.sos_widget.update_status(status)

    def realtime_gps_update(self):
        try:
            stats = self.fare_calculator.get_real_time_stats()
            if self.current_mode == "Sharing":
                total_dist = stats['total_distance']
                wait_time = max(0, int(stats['trip_duration'] - (total_dist / max(stats['current_speed'], 1) * 60)))
                self.sharing_widget.update_total_info(total_dist, wait_time)
            elif self.current_mode == "For Hire":
                self.for_hire_subtitle.setText(f"GPS: {'Locked' if stats['gps_fix'] else 'Searching'} • {stats['current_speed']:.1f} km/h")
        except: pass

    def fast_update(self):
        if self.current_mode == "Sharing":
            for pid in range(3):
                p_data = self.fare_calculator.passengers[pid]
                if p_data['onboard']:
                    self.sharing_widget.update_card_live_data(pid, p_data['total_distance'], p_data['start_time'])