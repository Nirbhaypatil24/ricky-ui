"""
SOS System - Manages emergency alerts and responses
"""

import threading
import time
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

class SOSSystem(QObject):
    # Signals
    sos_status_changed = pyqtSignal(str)  # status message
    sos_activated = pyqtSignal(dict)     # sos_data
    sos_deactivated = pyqtSignal()
    
    def __init__(self, gpio_manager, gps_manager=None):
        """
        gps_manager: optional, injected from main.py
        """
        super().__init__()
        self.gpio_manager = gpio_manager
        self.gps_manager = gps_manager  # <-- Inject GPSManager reference
        self.sos_active = False
        self.countdown_active = False
        self.countdown_thread = None
        self.current_countdown = 0
        
        print("🚨 SOS System initialized")

    def start(self):
        """Start SOS monitoring"""
        self.gpio_manager.sos_button_pressed.connect(self.handle_sos_button_press)
        self.gpio_manager.sos_button_released.connect(self.handle_sos_button_release)
        print("🚨 SOS System started")

    def handle_sos_button_press(self):
        if not self.countdown_active and not self.sos_active:
            self.countdown_active = True
            self.countdown_thread = threading.Thread(
                target=self._countdown_loop, daemon=True
            )
            self.countdown_thread.start()
            print("🚨 SOS button pressed - starting countdown")

    def handle_sos_button_release(self):
        if self.countdown_active:
            self.countdown_active = False
            self.sos_status_changed.emit("SOS Cancelled - Normal")
            print("✅ SOS cancelled - button released early")
        elif self.sos_active:
            self.deactivate_sos()

    def _countdown_loop(self):
        for i in range(5, 0, -1):
            if not self.countdown_active:
                return
            self.current_countdown = i
            msg = f"SOS COUNTDOWN: {i} seconds"
            self.sos_status_changed.emit(msg)
            print(f"🚨 {msg}")
            time.sleep(1)
        if self.countdown_active:
            self.activate_sos()
            self.countdown_active = False

    def activate_sos(self):
        """Activate SOS emergency state"""
        self.sos_active = True
        activation_time = datetime.now()
        
        # ✅ Backend-compatible SOS type
        sos_data = {
            'activation_time': activation_time,
            'timestamp': activation_time.isoformat(),
            'location': None,  # Will be filled by GPS if available
            'status': 'ACTIVE',
            'type': 'SOS_BUTTON'  # <-- Must match backend
        }
        
        # Attach GPS location if available
        try:
            if self.gps_manager:
                location = self.gps_manager.get_location()
                sos_data['location'] = location
        except Exception:
            pass
        
        self.sos_status_changed.emit("🚨 SOS ACTIVATED! 🚨")
        self.sos_activated.emit(sos_data)
        
        print("🚨" + "="*50)
        print("🚨 EMERGENCY SOS ACTIVATED!")
        print(f"🚨 Time: {activation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if sos_data['location']:
            lat, lon = sos_data['location']
            print(f"🚨 Location: {lat:.6f}, {lon:.6f}")
        print("🚨" + "="*50)

    def deactivate_sos(self):
        if self.sos_active:
            self.sos_active = False
            deactivation_time = datetime.now()
            self.sos_status_changed.emit("✅ SOS Deactivated - Normal")
            self.sos_deactivated.emit()
            print("✅ SOS DEACTIVATED")
            print(f"✅ Time: {deactivation_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def get_sos_status(self):
        if self.sos_active:
            return "SOS_ACTIVE"
        elif self.countdown_active:
            return f"SOS_COUNTDOWN_{self.current_countdown}"
        else:
            return "NORMAL"

    def is_sos_active(self):
        return self.sos_active

    def is_countdown_active(self):
        return self.countdown_active

    def manual_sos_test(self):
        print("🧪 Manual SOS test triggered")
        self.activate_sos()

    def stop(self):
        self.countdown_active = False
        self.deactivate_sos()
        print("🚨 SOS System stopped")
