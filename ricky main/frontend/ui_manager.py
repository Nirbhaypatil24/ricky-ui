"""
UI Manager - Ricky Theme (Split Screen Layout)
Left: Operations | Right: Ads & Maps
Fixed: SOS Indicator (CSS Circle instead of Emoji)
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QStackedWidget, QLabel, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QColor

from .sharing_mode import SharingModeWidget
from .private_mode import PrivateModeWidget
from .ads_display import AdsDisplayWidget

# Theme Constants
THEME_BG = "#000000"
THEME_ACCENT = "#FFD700"
THEME_TEXT = "#FFFFFF"
THEME_DANGER = "#FF3B30"
THEME_SUCCESS = "#34C759"
THEME_CARD_BG = "#1C1C1E"
THEME_ALERT_BG = "#FFFFFF" # White for flashing

class SOSStatusWidget(QFrame):
    """Compact Professional SOS Button with Blinking Animation"""
    def __init__(self):
        super().__init__()
        # Animation State
        self.flash_timer = QTimer()
        self.flash_timer.setInterval(500) # 500ms flash interval
        self.flash_timer.timeout.connect(self._flash_tick)
        self.flash_state = False
        self.current_msg = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedHeight(80)
        self.set_normal_style()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon / LED Indicator (Replaces Emoji)
        self.led = QLabel()
        self.led.setFixedSize(24, 24)
        
        # Text Stack
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.main_lbl = QLabel("SYSTEM NOMINAL")
        self.main_lbl.setFont(QFont("Impact", 16))
        self.main_lbl.setStyleSheet(f"color: {THEME_SUCCESS}; background: transparent; letter-spacing: 1px;")
        
        self.sub_lbl = QLabel("SOS READY")
        self.sub_lbl.setFont(QFont("Arial", 10, QFont.Bold))
        self.sub_lbl.setStyleSheet("color: #666; background: transparent;")
        
        text_layout.addStretch()
        text_layout.addWidget(self.main_lbl)
        text_layout.addWidget(self.sub_lbl)
        text_layout.addStretch()
        
        layout.addWidget(self.led)
        layout.addSpacing(15)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Apply initial LED style
        self.set_led_color(THEME_SUCCESS)

    def set_led_color(self, color, border_color="#333"):
        """Helper to set LED color using CSS"""
        self.led.setStyleSheet(f"""
            background-color: {color};
            border-radius: 12px; /* Half of 24px width */
            border: 2px solid {border_color};
        """)

    def set_normal_style(self):
        """Reset to safe dark style"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME_CARD_BG};
                border-radius: 10px;
                border: 1px solid #333;
            }}
        """)
        if hasattr(self, 'main_lbl'):
            self.main_lbl.setText("SYSTEM NOMINAL")
            self.main_lbl.setStyleSheet(f"color: {THEME_SUCCESS}; background: transparent; letter-spacing: 1px;")
            self.sub_lbl.setText("SOS READY")
            self.sub_lbl.setStyleSheet("color: #666; background: transparent;")
            self.set_led_color(THEME_SUCCESS) # Green LED

    def _flash_tick(self):
        """Toggle colors for flashing effect"""
        self.flash_state = not self.flash_state
        
        if self.flash_state:
            # STATE 1: RED Background, WHITE Text, WHITE LED
            self.setStyleSheet(f"background-color: {THEME_DANGER}; border-radius: 10px; border: 2px solid white;")
            self.main_lbl.setStyleSheet("color: white; background: transparent;")
            self.sub_lbl.setStyleSheet("color: white; background: transparent;")
            self.set_led_color("white", "red")
        else:
            # STATE 2: WHITE Background, RED Text, RED LED
            self.setStyleSheet(f"background-color: {THEME_ALERT_BG}; border-radius: 10px; border: 2px solid {THEME_DANGER};")
            self.main_lbl.setStyleSheet(f"color: {THEME_DANGER}; background: transparent;")
            self.sub_lbl.setStyleSheet(f"color: {THEME_DANGER}; background: transparent;")
            self.set_led_color(THEME_DANGER, "white")
            
        # Ensure text stays updated
        self.main_lbl.setText(self.current_msg)

    def update_status(self, status):
        status_upper = status.upper()
        
        # Check if this is an emergency state
        is_emergency = "SOS" in status_upper and ("COUNTDOWN" in status_upper or "ACTIVATED" in status_upper)
        
        if is_emergency:
            # Start Animation if not running
            if "COUNTDOWN" in status_upper:
                self.current_msg = f"⚠️ {status_upper} ⚠️"
                self.sub_lbl.setText("HOLD TO CANCEL")
            else:
                self.current_msg = "🚨 EMERGENCY ACTIVE"
                self.sub_lbl.setText("SENDING ALERTS...")
            
            if not self.flash_timer.isActive():
                self.flash_timer.start()
                self._flash_tick() # Immediate update
        else:
            # Stop Animation and Reset
            if self.flash_timer.isActive():
                self.flash_timer.stop()
            self.set_normal_style()

class RickyUI(QMainWindow):
    # FIXED: Parameter names match main.py exactly
    def __init__(self, fare_calculator, mode_controller, sos_system):
        super().__init__()
        
        # Backend references
        self.fare_calculator = fare_calculator
        self.mode_controller = mode_controller
        self.sos_system = sos_system
        self.gps_manager = fare_calculator.gps_manager
        
        self.current_mode = "For Hire"
        self.setup_ui()
        self.setup_timers()
        self.setup_connections()

    def setup_ui(self):
        self.setWindowTitle("Ricky Smart Autometer")
        self.setGeometry(0, 0, 1024, 600)
        self.setStyleSheet(f"QMainWindow {{ background-color: {THEME_BG}; }} QWidget {{ font-family: 'Arial'; }} QLabel {{ color: {THEME_TEXT}; }}")
        
        central = QWidget()
        self.setCentralWidget(central)
        
        # MAIN LAYOUT: Vertical (Header + Split Body)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
        
        # --- HEADER (Top) ---
        header = QFrame()
        header.setFixedHeight(100) 
        header.setStyleSheet(f"background-color: {THEME_BG}; border-bottom: 2px solid {THEME_CARD_BG};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 5, 20, 5)
        
        logo_lbl = QLabel("RICKY")
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'Ricky Logo.png')
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path)
            if not pm.isNull():
                logo_lbl.setPixmap(pm.scaledToHeight(80, Qt.SmoothTransformation))
                logo_lbl.setText("")
        
        self.mode_lbl = QLabel("FOR HIRE")
        self.mode_lbl.setStyleSheet(f"color: {THEME_ACCENT}; font-size: 32px; font-weight: bold; letter-spacing: 2px;")
        self.mode_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        h_layout.addWidget(logo_lbl)
        h_layout.addStretch()
        h_layout.addWidget(self.mode_lbl)
        
        # --- SPLIT BODY (Left: Ops, Right: Map) ---
        body_container = QWidget()
        split_layout = QHBoxLayout(body_container)
        split_layout.setContentsMargins(10, 10, 10, 10)
        split_layout.setSpacing(15)
        
        # LEFT PANEL (Modes + SOS) - 55% Width
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0,0,0,0)
        left_layout.setSpacing(10)
        
        self.mode_stack = QStackedWidget()
        self.sharing_widget = SharingModeWidget()
        self.private_widget = PrivateModeWidget()
        self.for_hire_widget = self.create_placeholder("🚕 FOR HIRE", "Ready")
        self.waiting_widget = self.create_placeholder("⏸️ WAITING", "Break")
        
        self.mode_stack.addWidget(self.sharing_widget)
        self.mode_stack.addWidget(self.private_widget)
        self.mode_stack.addWidget(self.for_hire_widget)
        self.mode_stack.addWidget(self.waiting_widget)
        
        self.sos_widget = SOSStatusWidget()
        
        left_layout.addWidget(self.mode_stack, 1) # Takes available space
        left_layout.addWidget(self.sos_widget, 0) # Fixed height at bottom
        
        # RIGHT PANEL (Ads & Map) - 45% Width
        self.ads_widget = AdsDisplayWidget()
        
        split_layout.addWidget(left_panel, 55)
        split_layout.addWidget(self.ads_widget, 45)
        
        main_layout.addWidget(header)
        main_layout.addWidget(body_container)
        
        self.update_mode("For Hire")

    def create_placeholder(self, t, s):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setAlignment(Qt.AlignCenter)
        tl = QLabel(t)
        tl.setStyleSheet("color: #34C759; font-size: 48px; font-weight: bold;")
        sl = QLabel(s)
        sl.setStyleSheet("color: #8E8E93; font-size: 20px;")
        if "HIRE" in t: self.for_hire_subtitle = sl
        elif "WAITING" in t: self.waiting_subtitle = sl
        l.addWidget(tl)
        l.addWidget(sl)
        return w

    def setup_connections(self):
        self.gps_manager.speed_updated.connect(lambda s: setattr(self, 'current_speed', s))
        self.fare_calculator.distance_updated.connect(self._on_dist)
        
    def setup_timers(self):
        self.tmr = QTimer()
        self.tmr.timeout.connect(self.gps_update)
        self.tmr.start(1000)

    @pyqtSlot(str)
    def update_mode(self, mode):
        self.current_mode = mode
        self.mode_lbl.setText(mode.upper())
        m = {"Sharing":0, "Private":1, "For Hire":2, "Waiting":3}
        if mode in m: self.mode_stack.setCurrentIndex(m[mode])
        if mode == "Private": self.fare_calculator.start_private_mode()
        elif self.current_mode == "Private": self.fare_calculator.stop_private_mode()

    @pyqtSlot(float)
    def _on_dist(self, d):
        if self.current_mode=="Private": self.private_widget.update_distance(d)

    @pyqtSlot(int, bool)
    def update_passenger(self, p, o):
        if self.current_mode=="Sharing": self.sharing_widget.update_passenger(p, o)
        
    @pyqtSlot(int, float)
    def update_fares(self, p, f):
        if self.current_mode=="Sharing": self.sharing_widget.update_fare(p, f)
        elif self.current_mode=="Private": self.private_widget.update_fare(f)

    @pyqtSlot(str)
    def update_sos_status(self, s): self.sos_widget.update_status(s)

    def gps_update(self):
        s = self.fare_calculator.get_real_time_stats()
        if self.current_mode=="Sharing":
            self.sharing_widget.update_total_info(s['total_distance'], int(s['trip_duration']))
            for i in range(3):
                if self.fare_calculator.passengers[i]['onboard']:
                    self.sharing_widget.update_card_live_data(i, self.fare_calculator.passengers[i]['total_distance'])
        elif self.current_mode == "For Hire":
            self.for_hire_subtitle.setText(f"GPS Locked • {s['current_speed']:.1f} km/h")