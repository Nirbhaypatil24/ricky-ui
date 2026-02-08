#!/usr/bin/env python3
"""
Ricky Smart Autometer System
Main entry point for the application
Updated: Added Intro Animation (intro.mp4)
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

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt, QUrl, pyqtSignal

# Import Multimedia for Intro Video
try:
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    from PyQt5.QtMultimediaWidgets import QVideoWidget
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    print("⚠️ PyQt5.QtMultimedia not found. Install 'python3-pyqt5.qtmultimedia' for intro video.")
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
        # Frameless and Fullscreen
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video Player Setup
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)
        
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.video_widget)
        
        # Load Media
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        self.player.mediaStatusChanged.connect(self._check_status)
        self.player.error.connect(self._handle_error)
        
    def start(self):
        print("🎬 Playing intro animation...")
        self.player.play()
        
    def _check_status(self, status):
        # When video finishes, emit finished signal
        if status == QMediaPlayer.EndOfMedia:
            print("🎬 Intro finished.")
            self.finished.emit()
            
    def _handle_error(self):
        print(f"❌ Intro playback error: {self.player.errorString()}")
        self.finished.emit() # Skip to main app on error

class RickyAutometer:
    def __init__(self):
        try:
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Ricky Autometer")
            print("✅ Qt Application created successfully")
        except Exception as e:
            print(f"⚠️ Qt display issue, trying alternative: {e}")
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Ricky Autometer")
        
        # Initialize backend systems
        self.gpio_manager = GPIOManager()
        self.gps_manager = GPSManager()
        self.fare_calculator = FareCalculator(self.gps_manager)
        self.mode_controller = ModeController(self.gpio_manager)
        
        # Pass GPS manager to SOS system for location tagging
        self.sos_system = SOSSystem(self.gpio_manager, self.gps_manager)
        
        # Initialize frontend
        self.ui = RickyUI(
            fare_calculator=self.fare_calculator,
            mode_controller=self.mode_controller,
            sos_system=self.sos_system
        )
        
        self.setup_connections()
        signal.signal(signal.SIGINT, self.signal_handler)
        print("🚗 Ricky Autometer System Initialized")

    def setup_connections(self):
        """Connect backend signals to frontend updates"""
        self.mode_controller.mode_changed.connect(self.ui.update_mode)
        self.gpio_manager.passenger_changed.connect(self.ui.update_passenger)
        self.gpio_manager.passenger_changed.connect(self.fare_calculator.handle_passenger_change)
        self.sos_system.sos_status_changed.connect(self.ui.update_sos_status)
        self.fare_calculator.fare_updated.connect(self.ui.update_fares)
        print("✅ Signal connections established")

    def run(self):
        """Start the application with Intro"""
        try:
            # Start all backend services immediately
            self.gpio_manager.start()
            self.gps_manager.start()
            self.fare_calculator.start()
            self.mode_controller.start()
            self.sos_system.start()
            
            # Check for Intro Video
            intro_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'intro.mp4')
            
            if MULTIMEDIA_AVAILABLE and os.path.exists(intro_path):
                # Show Intro First
                self.intro = IntroWindow(intro_path)
                self.intro.finished.connect(self.show_main_ui)
                self.intro.start()
            else:
                # Skip intro if file missing or module missing
                if not os.path.exists(intro_path):
                    print("ℹ️ 'intro.mp4' not found in assets. Starting main UI directly.")
                self.show_main_ui()
            
            return self.app.exec_()
            
        except Exception as e:
            print(f"❌ Error starting application: {e}")
            return 1

    def show_main_ui(self):
        """Close intro and show main UI"""
        if hasattr(self, 'intro'):
            self.intro.close()
        
        print("🚀 Showing Main GUI")
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
            print("🧹 Clean shutdown completed")
        except Exception as e:
            print(f"⚠️ Shutdown warning: {e}")

def main():
    print("=" * 50)
    print("🚗 RICKY SMART AUTOMETER SYSTEM")
    print("=" * 50)
    
    try:
        autometer = RickyAutometer()
        return autometer.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
