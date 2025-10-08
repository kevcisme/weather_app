import random
import os

class MockSenseHat:
    """Mock SenseHat for local development without emulator"""
    def get_temperature(self) -> float:
        # Return a realistic temperature around 20-25°C
        return 20.0 + random.random() * 5.0
    
    def get_temperature_from_humidity(self) -> float:
        return self.get_temperature()
    
    def get_temperature_from_pressure(self) -> float:
        # Pressure sensor typically reads slightly lower
        return self.get_temperature() - 1.0
    
    def get_humidity(self) -> float:
        # Return realistic humidity 40-60%
        return 40.0 + random.random() * 20.0
    
    def get_pressure(self) -> float:
        # Return realistic pressure around 1013 hPa
        return 1000.0 + random.random() * 26.0

def get_cpu_temp() -> float | None:
    """
    Get Raspberry Pi CPU temperature in Celsius.
    Returns None if not on a Pi or unable to read.
    """
    try:
        # On Raspberry Pi, CPU temp is in /sys/class/thermal/thermal_zone0/temp
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_milli = int(f.read().strip())
            return temp_milli / 1000.0
    except (FileNotFoundError, ValueError, PermissionError):
        return None

def get_sense():
    try:
        # on the Pi
        from sense_hat import SenseHat
        print("Successfully imported sense_hat, initializing hardware...")
        return SenseHat()
    except Exception as e:
        print(f"Failed to use real sense_hat: {e}")
        try:
            # local emulator (requires sense_emu_gui running)
            from sense_emu import SenseHat
            print("Using sense_emu emulator")
            return SenseHat()
        except Exception as e2:
            # fallback to mock for development
            print(f"Failed to use emulator: {e2}")
            print("Using mock SenseHat for development")
            return MockSenseHat()
