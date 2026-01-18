"""
Lightweight Map Display Widget for Raspberry Pi - FIXED VERSION
Uses static OpenStreetMap tiles with proper User-Agent and error handling
Updated: Adjusted size to fit Split Screen Layout (Right Panel)
"""

import os
import json
import time
import math
import requests
import threading
from io import BytesIO
from datetime import datetime

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QPushButton, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QThread, QMutex
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

class TileDownloader(QThread):
    """Fixed background thread for downloading map tiles"""
    
    tile_downloaded = pyqtSignal(int, int, int, bytes)  # x, y, zoom, image_data
    download_progress = pyqtSignal(str)  # status message
    
    def __init__(self):
        super().__init__()
        self.download_queue = []
        self.running = True
        self.session = None
        self.mutex = QMutex()
        self.setup_session()
    
    def setup_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RickyAutometer/1.0 (Raspberry Pi GPS Autometer)',
            'Accept': 'image/png,image/*,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        })
    
    def add_download(self, x, y, zoom):
        self.mutex.lock()
        tile_tuple = (x, y, zoom)
        if tile_tuple not in self.download_queue:
            self.download_queue.append(tile_tuple)
        self.mutex.unlock()
    
    def run(self):
        while self.running:
            try:
                self.mutex.lock()
                if self.download_queue:
                    x, y, z = self.download_queue.pop(0)
                    self.mutex.unlock()
                    self.download_progress.emit(f"Downloading tile {x},{y},{z}...")
                    self.download_tile(x, y, z)
                    time.sleep(0.5)
                else:
                    self.mutex.unlock()
                    time.sleep(0.1)
            except Exception as e:
                self.mutex.unlock()
                print(f"❌ Tile downloader error: {e}")
                time.sleep(1)
    
    def download_tile(self, x, y, z):
        try:
            url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            response = self.session.get(url, timeout=15, stream=True)
            if response.status_code == 200:
                image_data = response.content
                if len(image_data) > 100:
                    self.tile_downloaded.emit(x, y, z, image_data)
                    return True
        except Exception as e:
            print(f"❌ Download error: {e}")
        return False
    
    def clear_queue(self):
        self.mutex.lock()
        self.download_queue.clear()
        self.mutex.unlock()
    
    def stop(self):
        self.running = False
        if self.session: self.session.close()

class LightweightMapWidget(QWidget):
    """Fixed lightweight map widget with proper tile loading"""
    
    def __init__(self):
        super().__init__()
        self.current_location = (19.0760, 72.8777)  # Mumbai default
        self.zoom_level = 15
        
        # FIXED: Adjusted sizes to fit right panel (approx 45% of 1024px width)
        self.tile_size = 256
        self.map_width = 440  # Fits within 460px column
        self.map_height = 420 # Fits within available vertical space
        
        self.tile_cache = {}
        self.max_cache_size = 30
        self.pending_tiles = set()
        self.route_points = []
        self.gps_status = {'fix': False, 'satellites': 0}
        self.tiles_downloading = False
        self.last_download_time = 0
        
        self.tile_downloader = TileDownloader()
        self.tile_downloader.tile_downloaded.connect(self.on_tile_downloaded)
        self.tile_downloader.download_progress.connect(self.on_download_progress)
        self.tile_downloader.start()
        
        self.setup_ui()
        QTimer.singleShot(2000, self.update_map)
        print("🗺️ Fixed Map Widget initialized with corrected size")

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_layout = QHBoxLayout()
        self.location_label = QLabel("📍 Initializing...")
        self.location_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #2C3E50;")
        self.status_label = QLabel("🔄 Starting...")
        self.status_label.setStyleSheet("font-size: 11px; color: #3498DB;")
        header_layout.addWidget(self.location_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        layout.addLayout(header_layout)
        
        # Map Label - REMOVED Maximum Size constraint
        self.map_label = QLabel()
        self.map_label.setFixedSize(self.map_width, self.map_height)
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setStyleSheet("""
            QLabel {
                background-color: #F0F8FF;
                border: 2px solid #3498DB;
                border-radius: 10px;
            }
        """)
        self.create_loading_map()
        layout.addWidget(self.map_label)
        
        # Footer
        controls_layout = QHBoxLayout()
        self.gps_status_label = QLabel("🛰️ GPS: Init...")
        self.coords_label = QLabel("Loading...")
        
        zoom_out = QPushButton("➖")
        zoom_out.setFixedSize(30, 30)
        zoom_out.clicked.connect(self.zoom_out)
        
        zoom_in = QPushButton("➕")
        zoom_in.setFixedSize(30, 30)
        zoom_in.clicked.connect(self.zoom_in)
        
        controls_layout.addWidget(self.gps_status_label)
        controls_layout.addStretch()
        controls_layout.addWidget(self.coords_label)
        controls_layout.addWidget(zoom_out)
        controls_layout.addWidget(zoom_in)
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)

    def create_loading_map(self):
        pixmap = QPixmap(self.map_width, self.map_height)
        pixmap.fill(QColor("#EBF5FF"))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Grid
        painter.setPen(QPen(QColor("#D1E7FF"), 1))
        for i in range(0, self.map_width, 20): painter.drawLine(i, 0, i, self.map_height)
        for i in range(0, self.map_height, 20): painter.drawLine(0, i, self.map_width, i)
        
        # Text
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor("#2C3E50")))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "🗺️ Loading Map...")
        
        painter.end()
        self.map_label.setPixmap(pixmap)

    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x = int((lon_deg + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (x, y)

    def update_map(self):
        try:
            current_time = time.time()
            if current_time - self.last_download_time < 3.0: return
            self.last_download_time = current_time
            
            lat, lon = self.current_location
            center_x, center_y = self.deg2num(lat, lon, self.zoom_level)
            
            tiles_needed = []
            # 3x3 Grid for better coverage
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    tiles_needed.append((center_x + dx, center_y + dy))
            
            tiles_to_download = []
            for tx, ty in tiles_needed:
                key = f"{self.zoom_level}_{tx}_{ty}"
                if key not in self.tile_cache and (tx, ty, self.zoom_level) not in self.pending_tiles:
                    tiles_to_download.append((tx, ty))
                    self.pending_tiles.add((tx, ty, self.zoom_level))
            
            if tiles_to_download:
                self.tiles_downloading = True
                self.status_label.setText(f"📥 Loading {len(tiles_to_download)} tiles...")
                for tx, ty in tiles_to_download:
                    self.tile_downloader.add_download(tx, ty, self.zoom_level)
            else:
                self.tiles_downloading = False
                self.status_label.setText("✅ Map ready")
            
            self.render_map()
            
        except Exception as e:
            print(f"❌ Map update error: {e}")

    def render_map(self):
        try:
            lat, lon = self.current_location
            center_x, center_y = self.deg2num(lat, lon, self.zoom_level)
            
            map_pixmap = QPixmap(self.map_width, self.map_height)
            map_pixmap.fill(QColor("#E8F4FD"))
            painter = QPainter(map_pixmap)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    tx, ty = center_x + dx, center_y + dy
                    key = f"{self.zoom_level}_{tx}_{ty}"
                    
                    if key in self.tile_cache:
                        pixel_x = self.map_width // 2 + dx * self.tile_size
                        pixel_y = self.map_height // 2 + dy * self.tile_size
                        painter.drawPixmap(pixel_x - self.tile_size // 2, pixel_y - self.tile_size // 2, self.tile_size, self.tile_size, self.tile_cache[key])
            
            # Marker
            cx, cy = self.map_width // 2, self.map_height // 2
            painter.setBrush(QBrush(QColor("#E74C3C")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx - 8, cy - 8, 16, 16)
            painter.setBrush(QBrush(Qt.white))
            painter.drawEllipse(cx - 3, cy - 3, 6, 6)
            
            painter.end()
            self.map_label.setPixmap(map_pixmap)
            
        except Exception as e:
            print(f"Render error: {e}")

    @pyqtSlot(int, int, int, bytes)
    def on_tile_downloaded(self, x, y, zoom, data):
        if zoom == self.zoom_level:
            pix = QPixmap()
            if pix.loadFromData(data):
                self.tile_cache[f"{zoom}_{x}_{y}"] = pix
                self.pending_tiles.discard((x, y, zoom))
                if len(self.tile_cache) > self.max_cache_size:
                    del self.tile_cache[list(self.tile_cache.keys())[0]]
                self.render_map()

    @pyqtSlot(str)
    def on_download_progress(self, msg): self.status_label.setText(msg)

    @pyqtSlot(float, float)
    def update_gps_location(self, lat, lon):
        self.current_location = (lat, lon)
        self.coords_label.setText(f"{lat:.4f}, {lon:.4f}")
        self.update_map()

    def update_gps_status(self, status):
        sats = status.get('satellites', 0)
        self.gps_status_label.setText(f"🛰️ {sats} Sats")

    def zoom_in(self):
        if self.zoom_level < 18:
            self.zoom_level += 1
            self.tile_cache.clear()
            self.update_map()

    def zoom_out(self):
        if self.zoom_level > 8:
            self.zoom_level -= 1
            self.tile_cache.clear()
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
    
    @pyqtSlot(float, float)
    def update_gps_location(self, lat, lon): self.map_widget.update_gps_location(lat, lon)
    def update_gps_status(self, status): self.map_widget.update_gps_status(status)
    def cleanup(self): self.map_widget.cleanup()