"""
UI Manager - Ricky Theme Edition
Coordinates the interface with a Dark Mode / Taxi Theme
"""

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QStackedWidget, QLabel, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QColor, QPalette

from .sharing_mode import SharingModeWidget
from .private_mode import PrivateModeWidget
from .ads_display import AdsDisplayWidget

# --- RICKY THEME CONSTANTS ---
THEME_BG = "#000000"        # Pure Black
THEME_ACCENT = "#FFD700"    # Gold/Yellow (Ricky style)
THEME_TEXT = "#FFFFFF"      # White
THEME_DANGER = "#FF3B30"    # Red
THEME_SUCCESS = "#34C759"   # Green
THEME_CARD_BG = "#1C1C1E"   # Dark Grey for cards

class SOSStatusWidget(QFrame):
    """
    Professional System Monitor Widget
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_status = "Normal"
    
    def setup_ui(self):
        self.setFixedHeight(60)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(20, 5, 20, 5)
        self.setLayout(self.layout)
        
        # 1. Status LED Indicator (Circle)
        self.led_indicator = QLabel()
        self.led_indicator.setFixedSize(16, 16)
        self.led_indicator.setStyleSheet(f"""
            background-color: {THEME_SUCCESS};
            border-radius: 8px;
            border: 2px solid #14401D;
        """)
        
        # 2. Main Status Text
        self.status_label = QLabel("SYSTEM NOMINAL")
        self.status_label.setFont(QFont("Courier New", 14, QFont.Bold)) # Monospace for tech look
        self.status_label.setStyleSheet(f"color: {THEME_SUCCESS}; letter-spacing: 2px;")
        
        # 3. Sub-status / Details
        self.detail_label = QLabel("MONITORING ACTIVE")
        self.detail_label.setFont(QFont("Arial", 10))
        self.detail_label.setStyleSheet("color: #666; font-weight: bold;")
        self.detail_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.layout.addWidget(self.led_indicator)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.status_label)
        self.layout.addStretch()
        self.layout.addWidget(self.detail_label)
        
        # Apply initial "Normal" style
        self.set_normal_style()
    
    def set_normal_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME_CARD_BG};
                border-radius: 8px;
                border: 1px solid #333;
            }}
        """)
        self.led_indicator.setStyleSheet(f"background-color: {THEME_SUCCESS}; border-radius: 8px;")
        self.status_label.setText("SYSTEM NOMINAL")
        self.status_label.setStyleSheet(f"color: {THEME_SUCCESS}; font-family: 'Courier New'; font-weight: bold; letter-spacing: 1px;")
        self.detail_label.setText("MONITORING ACTIVE")
        self.detail_label.setStyleSheet("color: #8E8E93;")

    def set_emergency_style(self, message):
        # Flashy Red Style
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME_DANGER};
                border-radius: 8px;
                border: 2px solid #FFCDD2;
            }}
        """)
        self.led_indicator.setStyleSheet("background-color: white; border-radius: 8px;")
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: white; font-family: 'Arial'; font-weight: 900; letter-spacing: 1px; font-size: 16px;")
        self.detail_label.setText("SENDING ALERTS...")
        self.detail_label.setStyleSheet("color: white; font-weight: bold;")

    def update_status(self, status):
        self.current_status = status
        status_upper = status.upper()
        
        if "SOS" in status_upper and ("COUNTDOWN" in status_upper or "ACTIVATED" in status_upper):
            display_text = "🚨 EMERGENCY SOS ACTIVATED 🚨"
            if "COUNTDOWN" in status_upper:
                display_text = f"⚠️ {status_upper} ⚠️"
            self.set_emergency_style(display_text)
        else:
            self.set_normal_style()

class RickyUI(QMainWindow):
    """Main UI Manager with Ricky Dark Theme"""
    
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
        self.setup_gps_connections()
        
        print("🖥️ Ricky UI (Dark Theme) initialized")

    def setup_ui(self):
        self.setWindowTitle("Ricky Smart Autometer")
        # Updated resolution for 8-inch screens (Standard is often 1024x600)
        self.setGeometry(0, 0, 1024, 600)
        
        # Apply Global Dark Theme
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {THEME_BG}; }}
            QWidget {{ font-family: 'Arial'; }}
            QLabel {{ color: {THEME_TEXT}; }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- HEADER SECTION (Logo + Status) ---
        # UPDATED: Increased Height to 180px (50% larger than 120px)
        header = QFrame()
        header.setFixedHeight(180) 
        header.setStyleSheet(f"background-color: {THEME_BG}; border-bottom: 2px solid {THEME_CARD_BG};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 10, 30, 10)
        
        # Load Logo
        logo_label = QLabel()
        # Look for logo in assets folder relative to main script
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               'assets', 'Ricky Logo.png')
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                # UPDATED: Increased Logo Scale to 150px (50% larger than 100px)
                scaled_pixmap = pixmap.scaledToHeight(150, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                logo_label.setText("RICKY")
                logo_label.setStyleSheet(f"color: {THEME_ACCENT}; font-size: 75px; font-weight: bold;")
        else:
            logo_label.setText("RICKY")
            logo_label.setStyleSheet(f"color: {THEME_ACCENT}; font-size: 75px; font-weight: bold;")
        
        # Mode Title (Dynamic)
        self.mode_label = QLabel("FOR HIRE")
        self.mode_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.mode_label.setStyleSheet(f"color: {THEME_ACCENT}; font-size: 36px; font-weight: bold; letter-spacing: 3px; text-transform: uppercase;")
        
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.mode_label)
        
        # --- BODY SECTION ---
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(15, 15, 15, 15)
        body_layout.setSpacing(15)
        
        # Stacked Widget for Modes
        self.mode_stack = QStackedWidget()
        
        # Initialize Widgets
        self.sharing_widget = SharingModeWidget()
        self.private_widget = PrivateModeWidget()
        self.for_hire_widget = self.create_placeholder_widget("🚕 FOR HIRE", "Ready for passengers", THEME_SUCCESS)
        self.waiting_widget = self.create_placeholder_widget("⏸️ WAITING", "Driver on break", "#8E8E93")
        
        self.mode_stack.addWidget(self.sharing_widget)      # Index 0
        self.mode_stack.addWidget(self.private_widget)      # Index 1
        self.mode_stack.addWidget(self.for_hire_widget)     # Index 2
        self.mode_stack.addWidget(self.waiting_widget)      # Index 3
        
        # SOS Bar (Professional Style)
        self.sos_widget = SOSStatusWidget()
        
        # Ads/Map Widget
        self.ads_widget = AdsDisplayWidget()
        
        # Assemble Body
        body_layout.addWidget(self.mode_stack, stretch=4)
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
        title_lbl.setStyleSheet(f"color: {color}; font-size: 64px; font-weight: bold;")
        title_lbl.setAlignment(Qt.AlignCenter)
        
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("color: #8E8E93; font-size: 28px; margin-top: 15px;")
        sub_lbl.setAlignment(Qt.AlignCenter)
        
        # Store reference to subtitle for GPS updates
        if "HIRE" in title:
            self.for_hire_subtitle = sub_lbl
        elif "WAITING" in title:
            self.waiting_subtitle = sub_lbl
            
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)
        widget.setLayout(layout)
        return widget

    def setup_gps_connections(self):
        """Connect existing backend signals to new UI slots"""
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

    # --- SLOTS & UPDATES ---
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
            
            # Backend hooks
            if mode == "Private":
                self.fare_calculator.start_private_mode()
            elif self.current_mode == "Private" and mode != "Private":
                self.fare_calculator.stop_private_mode()

    @pyqtSlot(int, bool)
    def update_passenger(self, pid, onboard):
        if self.current_mode == "Sharing":
            self.sharing_widget.update_passenger(pid, onboard)

    @pyqtSlot(int, float)
    def update_fares(self, pid, fare):
        if self.current_mode == "Sharing":
            self.sharing_widget.update_fare(pid, fare)
        elif self.current_mode == "Private":
            self.private_widget.update_fare(fare)

    @pyqtSlot(str)
    def update_sos_status(self, status):
        self.sos_widget.update_status(status)

    def realtime_gps_update(self):
        """Poll backend for GPS stats"""
        try:
            stats = self.fare_calculator.get_real_time_stats()
            if self.current_mode == "Sharing":
                total_dist = stats['total_distance']
                wait_time = max(0, int(stats['trip_duration'] - (total_dist / max(stats['current_speed'], 1) * 60)))
                self.sharing_widget.update_total_info(total_dist, wait_time)
            elif self.current_mode == "For Hire":
                status_text = "GPS Locked" if stats['gps_fix'] else "Searching GPS..."
                self.for_hire_subtitle.setText(f"{status_text} • {stats['current_speed']:.1f} km/h")
        except: pass

    def fast_update(self):
        # Update sharing cards dynamically using backend data
        if self.current_mode == "Sharing":
            for pid in range(3):
                p_data = self.fare_calculator.passengers[pid]
                if p_data['onboard']:
                    self.sharing_widget.update_card_live_data(pid, p_data['total_distance'])