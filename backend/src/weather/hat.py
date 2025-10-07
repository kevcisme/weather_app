import random

class MockSenseHat:
    """Mock SenseHat for local development without emulator"""
    def get_temperature(self) -> float:
        # Return a realistic temperature around 20-25°C
        return 20.0 + random.random() * 5.0
    
    def get_humidity(self) -> float:
        # Return realistic humidity 40-60%
        return 40.0 + random.random() * 20.0
    
    def get_pressure(self) -> float:
        # Return realistic pressure around 1013 hPa
        return 1000.0 + random.random() * 26.0

def get_sense():
    try:
        # on the Pi
        from sense_hat import SenseHat
        return SenseHat()
    except Exception:
        try:
            # local emulator (requires sense_emu_gui running)
            from sense_emu import SenseHat
            return SenseHat()
        except Exception:
            # fallback to mock for development
            print("Using mock SenseHat for development")
            return MockSenseHat()
