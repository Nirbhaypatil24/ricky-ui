"""
Lightweight Map Display Widget for Raspberry Pi - FIXED VERSION
Updated: Full width/height responsiveness for split screen
"""

import os
import time
import math
import requests
import threading
# ADDED QFrame to imports below
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QThread, QMutex, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont

class TileDownloader(QThread):
    """Fixed background thread for downloading map tiles"""
    tile_downloaded = pyqtSignal(int, int, int, bytes)
    download_progress = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.download_queue = []
        self.running = True
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RickyAutometer/1.0',
            'Connection': 'keep-alive'
        })
        self.mutex = QMutex()
    
    def add_download(self, x, y, zoom):
        self.mutex.lock()
        if (x, y, zoom) not in self.download_queue:
            self.download_queue.append((x, y, zoom))
        self.mutex.unlock()
    
    def run(self):
        while self.running:
            try:
                self.mutex.lock()
                if self.download_queue:
                    x, y, z = self.download_queue.pop(0)
                    self.mutex.unlock()
                    self.download_tile(x, y, z)
                    time.sleep(0.1)
                else:
                    self.mutex.unlock()
                    time.sleep(0.1)
            except:
                if self.mutex: self.mutex.unlock()
    
    def download_tile(self, x, y, z):
        try:
            url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                self.tile_downloaded.emit(x, y, z, response.content)
        except: pass
    
    def stop(self):
        self.running = False

class LightweightMapWidget(QWidget):
    """Map widget that automatically fills available space"""
    
    def __init__(self):
        super().__init__()
        self.current_location = (19.0760, 72.8777)
        self.zoom_level = 15
        self.tile_size = 256
        
        # Init with default but allow resize
        self.map_width = 400
        self.map_height = 400
        
        self.tile_cache = {}
        self.pending_tiles = set()
        self.last_download_time = 0
        
        self.tile_downloader = TileDownloader()
        self.tile_downloader.tile_downloaded.connect(self.on_tile_downloaded)
        self.tile_downloader.start()
        
        self.setup_ui()
        
        # Install event filter to detect resize
        self.map_label.installEventFilter(self)
        
        QTimer.singleShot(1000, self.update_map)

    def setup_ui(self):
        # Allow widget to expand
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Map Display Area
        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.map_label.setStyleSheet("background-color: #EBF5FF;")
        self.map_label.setMinimumSize(100, 100) # prevent collapse
        
        # Overlay Controls (Zoom)
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 0, 10, 10)
        
        self.coords_label = QLabel("Loading...")
        self.coords_label.setStyleSheet("background: rgba(255,255,255,0.7); padding: 4px; border-radius: 4px; font-size: 10px; color: black;")
        
        zoom_out = QPushButton("-")
        zoom_out.setFixedSize(30, 30)
        zoom_out.clicked.connect(self.zoom_out)
        zoom_out.setStyleSheet("background: white; border: 1px solid #ccc; border-radius: 4px; font-weight: bold; color: black;")
        
        zoom_in = QPushButton("+")
        zoom_in.setFixedSize(30, 30)
        zoom_in.clicked.connect(self.zoom_in)
        zoom_in.setStyleSheet("background: white; border: 1px solid #ccc; border-radius: 4px; font-weight: bold; color: black;")
        
        controls_layout.addWidget(self.coords_label)
        controls_layout.addStretch()
        controls_layout.addWidget(zoom_out)
        controls_layout.addWidget(zoom_in)
        
        layout.addWidget(self.map_label)
        
        # Info bar at bottom
        info_bar = QFrame()
        info_bar.setFixedHeight(40)
        info_bar.setStyleSheet("background: #F0F8FF; border-top: 1px solid #ccc;")
        ib_layout = QHBoxLayout(info_bar)
        ib_layout.setContentsMargins(10, 0, 10, 0)
        ib_layout.addWidget(self.coords_label)
        ib_layout.addStretch()
        ib_layout.addWidget(zoom_out)
        ib_layout.addWidget(zoom_in)
        
        layout.addWidget(info_bar)
        self.setLayout(layout)

    def eventFilter(self, source, event):
        if source == self.map_label and event.type() == QEvent.Resize:
            # Update map dimensions when the label resizes
            self.map_width = self.map_label.width()
            self.map_height = self.map_label.height()
            self.render_map()
        return super().eventFilter(source, event)

    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x = int((lon_deg + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (x, y)

    def update_map(self):
        try:
            # Refresh dimensions just in case
            if self.map_label.width() > 10:
                self.map_width = self.map_label.width()
                self.map_height = self.map_label.height()

            lat, lon = self.current_location
            center_x, center_y = self.deg2num(lat, lon, self.zoom_level)
            
            # Calculate how many tiles we need based on size
            cols = math.ceil(self.map_width / self.tile_size) + 1
            rows = math.ceil(self.map_height / self.tile_size) + 1
            
            start_x = center_x - (cols // 2)
            start_y = center_y - (rows // 2)
            
            tiles_needed = []
            for dx in range(cols):
                for dy in range(rows):
                    tiles_needed.append((start_x + dx, start_y + dy))
            
            for tx, ty in tiles_needed:
                key = f"{self.zoom_level}_{tx}_{ty}"
                if key not in self.tile_cache and key not in self.pending_tiles:
                    self.pending_tiles.add(key)
                    self.tile_downloader.add_download(tx, ty, self.zoom_level)
            
            self.render_map()
            
        except Exception as e:
            print(f"Map update error: {e}")

    def render_map(self):
        try:
            if self.map_width <= 0 or self.map_height <= 0: return

            lat, lon = self.current_location
            center_x, center_y = self.deg2num(lat, lon, self.zoom_level)
            
            pixmap = QPixmap(self.map_width, self.map_height)
            pixmap.fill(QColor("#E8F4FD"))
            painter = QPainter(pixmap)
            
            # Draw tiles
            cols = math.ceil(self.map_width / self.tile_size) + 2
            rows = math.ceil(self.map_height / self.tile_size) + 2
            
            for dx in range(-(cols//2), (cols//2) + 1):
                for dy in range(-(rows//2), (rows//2) + 1):
                    tx, ty = center_x + dx, center_y + dy
                    key = f"{self.zoom_level}_{tx}_{ty}"
                    
                    if key in self.tile_cache:
                        px = (self.map_width // 2) + (dx * self.tile_size) - (self.tile_size // 2)
                        py = (self.map_height // 2) + (dy * self.tile_size) - (self.tile_size // 2)
                        painter.drawPixmap(px, py, self.tile_cache[key])

            # Marker
            cx, cy = self.map_width // 2, self.map_height // 2
            painter.setBrush(QBrush(QColor("#E74C3C")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx - 8, cy - 8, 16, 16)
            painter.setBrush(QBrush(Qt.white))
            painter.drawEllipse(cx - 3, cy - 3, 6, 6)
            
            painter.end()
            self.map_label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"Render error: {e}")

    @pyqtSlot(int, int, int, bytes)
    def on_tile_downloaded(self, x, y, zoom, data):
        if zoom == self.zoom_level:
            pix = QPixmap()
            if pix.loadFromData(data):
                self.tile_cache[f"{zoom}_{x}_{y}"] = pix
                # Cleanup cache if too big
                if len(self.tile_cache) > 50:
                    del self.tile_cache[list(self.tile_cache.keys())[0]]
                self.render_map()
                self.pending_tiles.discard(f"{zoom}_{x}_{y}")

    @pyqtSlot(float, float)
    def update_gps_location(self, lat, lon):
        self.current_location = (lat, lon)
        self.coords_label.setText(f"{lat:.4f}, {lon:.4f}")
        self.update_map()

    def update_gps_status(self, status):
        pass

    def zoom_in(self):
        if self.zoom_level < 18:
            self.zoom_level += 1
            self.tile_cache.clear()
            self.pending_tiles.clear()
            self.update_map()

    def zoom_out(self):
        if self.zoom_level > 8:
            self.zoom_level -= 1
            self.tile_cache.clear()
            self.pending_tiles.clear()
            self.update_map()

    def cleanup(self):
        self.tile_downloader.stop()
        self.tile_downloader.wait()

class MapDisplayWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.map_widget = LightweightMapWidget()
        layout.addWidget(self.map_widget)
        self.setLayout(layout)
        # Expansion policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    @pyqtSlot(float, float)
    def update_gps_location(self, lat, lon): self.map_widget.update_gps_location(lat, lon)
    def update_gps_status(self, status): self.map_widget.update_gps_status(status)
    def cleanup(self): self.map_widget.cleanup()
