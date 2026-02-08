#!/usr/bin/env python3
"""
Ricky Smart Autometer System
Main entry point for the application
Updated: Intro Animation with Debugging
"""

import sys
import os
import signal

# Fix display issues BEFORE importing PyQt5
def setup_display():
    """Setup display environment for Raspberry Pi"""
    if 'SSH_CONNECTION' in os.environ and 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':10.0'
    elif 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    
    if 'QT_QPA_PLATFORM' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'xcb'

setup_display()

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt, QUrl, pyqtSignal

# Import Multimedia for Intro Video
try:
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    from PyQt5.QtMultimediaWidgets import QVideoWidget
    MULTIMEDIA_AVAILABLE = True
    print("✅ PyQt5 Multimedia module loaded.")
except ImportError as e:
    print(f"⚠️ PyQt5.QtMultimedia import failed: {e}")
    print("   -> Try installing: sudo apt-get install python3-pyqt5.qtmultimedia libqt5multimedia5-plugins")
    MULTIMEDIA_AVAILABLE = False

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.ui_manager import RickyUI
from backend.gpio_manager import GPIOManager
from backend.gps_manager import GPSManager
from backend.fare_calculator import FareCalculator
from backend.mode_controller import ModeController
from backend.sos_system import SOSSystem

class IntroWindow(QWidget):
    """Fullscreen Intro Animation Window"""
    finished = pyqtSignal()

    def __init__(self, video_path):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)
        
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.video_widget)
        
        # Connect signals
        self.player.mediaStatusChanged.connect(self._check_status)
        self.player.error.connect(self._handle_error)
        
        # Load Content
        if os.path.exists(video_path):
            print(f"🎬 Loading intro video from: {video_path}")
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        else:
            print(f"❌ Video file NOT found at: {video_path}")
            # Emit finished immediately to not block app
            QTimer.singleShot(100, self.finished.emit)

    def start(self):
        print("🎬 Starting playback...")
        self.player.play()
        
    def _check_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            print("🎬 Intro video finished.")
            self.finished.emit()
        elif status == QMediaPlayer.InvalidMedia:
            print("⚠️ Invalid media format.")
            self.finished.emit()
            
    def _handle_error(self):
        err_msg = self.player.errorString()
        print(f"❌ Intro playback error: {err_msg}")
        self.finished.emit() 

class RickyAutometer:
    def __init__(self):
        try:
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Ricky Autometer")
        except Exception as e:
            print(f"⚠️ Qt display issue, trying offscreen: {e}")
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            self.app = QApplication(sys.argv)
        
        # Initialize Backend
        self.gpio_manager = GPIOManager()
        self.gps_manager = GPSManager()
        self.fare_calculator = FareCalculator(self.gps_manager)
        self.mode_controller = ModeController(self.gpio_manager)
        self.sos_system = SOSSystem(self.gpio_manager, self.gps_manager)
        
        # Initialize Frontend
        self.ui = RickyUI(
            fare_calculator=self.fare_calculator,
            mode_controller=self.mode_controller,
            sos_system=self.sos_system
        )
        
        self.setup_connections()
        signal.signal(signal.SIGINT, self.signal_handler)

    def setup_connections(self):
        self.mode_controller.mode_changed.connect(self.ui.update_mode)
        self.gpio_manager.passenger_changed.connect(self.ui.update_passenger)
        self.gpio_manager.passenger_changed.connect(self.fare_calculator.handle_passenger_change)
        self.sos_system.sos_status_changed.connect(self.ui.update_sos_status)
        self.fare_calculator.fare_updated.connect(self.ui.update_fares)

    def run(self):
        """Start the application logic"""
        # Start backend threads
        self.gpio_manager.start()
        self.gps_manager.start()
        self.fare_calculator.start()
        self.mode_controller.start()
        self.sos_system.start()
        
        # --- INTRO VIDEO LOGIC ---
        base_path = os.path.dirname(os.path.abspath(__file__))
        intro_path = os.path.join(base_path, 'assets', 'intro.mp4')
        
        print(f"🔍 Checking for intro video at: {intro_path}")
        
        if MULTIMEDIA_AVAILABLE and os.path.exists(intro_path):
            print("✅ Video found & Multimedia available. Launching Intro...")
            self.intro = IntroWindow(intro_path)
            self.intro.finished.connect(self.show_main_ui)
            self.intro.start()
        else:
            if not MULTIMEDIA_AVAILABLE:
                print("⚠️ Skipping intro: Multimedia module missing.")
            if not os.path.exists(intro_path):
                print("⚠️ Skipping intro: File 'assets/intro.mp4' not found.")
            
            self.show_main_ui()
            
        return self.app.exec_()

    def show_main_ui(self):
        """Transition to main UI"""
        if hasattr(self, 'intro'):
            self.intro.close()
            self.intro.deleteLater() # Cleanup
        
        print("🚀 Launching Main GUI")
        self.ui.showFullScreen()

    def signal_handler(self, signum, frame):
        print("\n🛑 Shutdown signal received...")
        self.shutdown()
        sys.exit(0)

    def shutdown(self):
        try:
            self.fare_calculator.stop()
            self.gps_manager.stop()
            self.sos_system.stop()
            self.mode_controller.stop()
            self.gpio_manager.cleanup()
        except: pass

def main():
    print("=" * 50)
    print("🚗 RICKY SMART AUTOMETER SYSTEM")
    print("=" * 50)
    autometer = RickyAutometer()
    return autometer.run()

if __name__ == "__main__":
    sys.exit(main())