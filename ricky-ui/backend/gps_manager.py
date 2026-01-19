"""
GPS Manager - Handles GPS data acquisition and processing
Enhanced: Immediate Simulation Start & Missing Methods Restored
"""

import threading
import time
import math
import random
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

class GPSManager(QObject):
    # Signals
    location_updated = pyqtSignal(float, float)  # latitude, longitude
    speed_updated = pyqtSignal(float)  # speed in km/h
    distance_updated = pyqtSignal(float)  # total distance traveled
    
    def __init__(self, port="/dev/serial0", baudrate=9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.thread = None
        
        # Current state
        self.current_location = (19.0760, 72.8777)  # Mumbai default
        self.previous_location = None
        self.current_speed = 0.0
        self.total_distance_traveled = 0.0
        self.trip_start_time = None
        self.simulation_mode = not SERIAL_AVAILABLE
        
        # GPS tracking
        self.gps_fix = False
        self.satellites_count = 0
        self.altitude = 0.0
        self.heading = 0.0
        
        # Simulation
        self.sim_last_update = time.time()

    def start(self):
        """Start GPS monitoring"""
        self.running = True
        self.trip_start_time = datetime.now()
        
        # Emit initial location IMMEDIATELY
        self.location_updated.emit(*self.current_location)
        self.speed_updated.emit(0.0)
        
        if not self.simulation_mode:
            try:
                self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
                print(f"📡 GPS initialized on {self.port}")
            except Exception as e:
                print(f"⚠️ GPS serial failed, switching to simulation: {e}")
                self.simulation_mode = True
        
        self.thread = threading.Thread(target=self._gps_loop, daemon=True)
        self.thread.start()
        print("📡 GPS manager started")

    def _gps_loop(self):
        """Main GPS processing loop"""
        if self.simulation_mode:
            self._enhanced_simulation_loop()
        else:
            self._serial_loop()

    def _enhanced_simulation_loop(self):
        """Enhanced GPS simulation with realistic movement patterns"""
        # Simulate different route patterns
        route_points = [
            (19.0760, 72.8777),  # Starting point
            (19.0800, 72.8800),  # Point 1
            (19.0850, 72.8750),  # Point 2
            (19.0820, 72.8720),  # Point 3
            (19.0790, 72.8760),  # Back towards start
        ]
        
        current_idx = 0
        progress = 0.0
        
        while self.running:
            try:
                current_time = time.time()
                time_delta = current_time - self.sim_last_update
                self.sim_last_update = current_time
                
                # Move between points
                p1 = route_points[current_idx]
                p2 = route_points[(current_idx + 1) % len(route_points)]
                
                # Simulation speed factor
                progress += 0.02
                if progress >= 1.0:
                    progress = 0.0
                    current_idx = (current_idx + 1) % len(route_points)
                
                # Interpolate position
                lat = p1[0] + (p2[0] - p1[0]) * progress
                lon = p1[1] + (p2[1] - p1[1]) * progress
                
                # Add noise
                lat += random.uniform(-0.00005, 0.00005)
                lon += random.uniform(-0.00005, 0.00005)
                
                # Calculate distance if we moved
                if self.previous_location:
                    distance_moved = self.calculate_distance(
                        self.previous_location[0], self.previous_location[1], lat, lon
                    )
                    self.total_distance_traveled += distance_moved
                    self.distance_updated.emit(self.total_distance_traveled)
                
                self.previous_location = self.current_location
                self.current_location = (lat, lon)
                self.current_speed = random.uniform(20, 45) # Simulate speed
                
                # Update status
                self.gps_fix = True
                self.satellites_count = 8
                
                # Emit updates
                self.location_updated.emit(lat, lon)
                self.speed_updated.emit(self.current_speed)
                
                time.sleep(0.5) # Update every 500ms
                
            except Exception as e:
                print(f"GPS Sim Error: {e}")
                time.sleep(1)

    def _serial_loop(self):
        """Read from actual GPS module"""
        while self.running:
            try:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode("ascii", errors="replace").strip()
                    if line.startswith("$GPGGA"):
                        # Basic parsing logic would go here
                        pass 
                time.sleep(0.1)
            except:
                time.sleep(1)

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in km"""
        if not all([lat1, lon1, lat2, lon2]):
            return 0.0
        try:
            R = 6371.0 # Earth radius in km
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            return R * c
        except:
            return 0.0

    def get_location(self):
        return self.current_location

    def get_speed(self):
        return self.current_speed

    def get_total_distance(self):
        return self.total_distance_traveled

    def get_trip_duration(self):
        if self.trip_start_time:
            return (datetime.now() - self.trip_start_time).total_seconds() / 60
        return 0

    def get_gps_status(self):
        return {
            'fix': self.gps_fix,
            'satellites': self.satellites_count,
            'altitude': self.altitude,
            'speed': self.current_speed,
            'heading': self.heading
        }

    def reset_trip(self):
        self.total_distance_traveled = 0.0
        self.trip_start_time = datetime.now()
        self.previous_location = None

    def stop(self):
        self.running = False
        if hasattr(self, 'serial'):
            try: self.serial.close()
            except: pass
        if self.thread:
            self.thread.join(timeout=1)
