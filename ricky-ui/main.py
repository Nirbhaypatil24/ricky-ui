#!/usr/bin/env python3
"""
Ricky Smart Autometer System
Main entry point for the application
Updated: Separate videos for Intro (Startup) and Loading (Mode Switch)
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

# Import Multimedia for Intro/Loading Videos
try:
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    from PyQt5.QtMultimediaWidgets import QVideoWidget
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    print("⚠️ PyQt5.QtMultimedia not found. Install 'python3-pyqt5.qtmultimedia'")
    MULTIMEDIA_AVAILABLE = False

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from frontend.ui_manager import RickyUI
from backend.gpio_manager import GPIOManager
from backend.gps_manager import GPSManager
from backend.fare_calculator import FareCalculator
from backend.mode_controller import ModeController
from backend.sos_system import SOSSystem

class VideoWindow(QWidget):
    """Fullscreen Video Window for Intro or Loading"""
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
        
        self.player.mediaStatusChanged.connect(self._check_status)
        self.player.error.connect(self._handle_error)
        
        if os.path.exists(video_path):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        else:
            print(f"❌ Video file missing: {video_path}")
            QTimer.singleShot(100, self.finished.emit)

    def start(self):
        self.player.play()
        
    def _check_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.finished.emit()
        elif status == QMediaPlayer.InvalidMedia:
            self.finished.emit()
            
    def _handle_error(self):
        print(f"❌ Video error: {self.player.errorString()}")
        self.finished.emit()

class RickyAutometer:
    def __init__(self):
        try:
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Ricky Autometer")
        except Exception as e:
            print(f"⚠️ Qt display error: {e}")
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            self.app = QApplication(sys.argv)
        
        # State flags
        self.boot_complete = False
        
        # Define Paths for Videos
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.intro_path = os.path.join(base_path, 'assets', 'intro.mp4')
        self.loading_path = os.path.join(base_path, 'assets', 'load.mp4')

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
        # 1. Update UI Mode (happens behind the video)
        self.mode_controller.mode_changed.connect(self.ui.update_mode)
        
        # 2. Play Loading Video on Mode Change
        self.mode_controller.mode_changed.connect(self.play_mode_transition)
        
        # Other connections
        self.gpio_manager.passenger_changed.connect(self.ui.update_passenger)
        self.gpio_manager.passenger_changed.connect(self.fare_calculator.handle_passenger_change)
        self.sos_system.sos_status_changed.connect(self.ui.update_sos_status)
        self.fare_calculator.fare_updated.connect(self.ui.update_fares)

    def play_mode_transition(self, mode_name):
        """Plays 'load.mp4' as a loading screen when mode changes"""
        # Only play if boot is done AND we have the loading video
        if self.boot_complete and MULTIMEDIA_AVAILABLE and os.path.exists(self.loading_path):
            print(f"🎬 Switching to {mode_name}: Playing loading animation...")
            
            # Close existing loader if any
            if hasattr(self, 'loading_window') and self.loading_window.isVisible():
                self.loading_window.close()

            # Create and play new loader
            self.loading_window = VideoWindow(self.loading_path)
            self.loading_window.finished.connect(self.loading_window.close)
            self.loading_window.finished.connect(self.loading_window.deleteLater)
            self.loading_window.start()
        else:
            print(f"ℹ️ Mode switched to {mode_name} (No loading video played)")

    def run(self):
        """Start the application"""
        # Start backend
        self.gpio_manager.start()
        self.gps_manager.start()
        self.fare_calculator.start()
        self.mode_controller.start()
        self.sos_system.start()
        
        # --- BOOT ANIMATION (INTRO.MP4) ---
        if MULTIMEDIA_AVAILABLE and os.path.exists(self.intro_path):
            print("🚀 Booting up... Playing Intro.")
            self.boot_window = VideoWindow(self.intro_path)
            self.boot_window.finished.connect(self.finish_boot_sequence)
            self.boot_window.start()
        else:
            print("ℹ️ Intro video skipped (missing file or module).")
            self.finish_boot_sequence()
            
        return self.app.exec_()

    def finish_boot_sequence(self):
        """Called when boot video finishes"""
        if hasattr(self, 'boot_window'):
            self.boot_window.close()
        
        print("✅ Boot complete. Showing Main UI.")
        self.ui.showFullScreen()
        
        # Enable mode-switch videos after a short delay
        # This prevents the "Loading" video from triggering immediately on startup
        QTimer.singleShot(2000, lambda: setattr(self, 'boot_complete', True))

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
