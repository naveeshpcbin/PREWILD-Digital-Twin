"""Patch control_service.py with fast throttled connection probes to prevent TCP timeout blocks."""
from pathlib import Path

fp = Path(r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\hardware\control_service.py")
content = fp.read_text(encoding="utf-8")

# 1. Patch ESP32Layer1Adapter
esp_old = """class ESP32Layer1Adapter(BaseHardwareAdapter):
    \"\"\"Layer 1: Wi-Fi CSI / ESP32-S3-DevKitC-1 v1.1 Actuator Adapter.\"\"\"
    def __init__(self, device_id: str = "ESP32_NODE_01", baud_rate: int = 115200):
        super().__init__(device_id, "ESP32-S3-DevKitC-1 v1.1 (Layer 1 CSI)", layer=1)
        self.baud_rate = baud_rate
        self.serial_handle = None
        self.check_connection()

    def check_connection(self) -> DeviceConnectionStatus:
        with self.lock:"""

esp_new = """class ESP32Layer1Adapter(BaseHardwareAdapter):
    \"\"\"Layer 1: Wi-Fi CSI / ESP32-S3-DevKitC-1 v1.1 Actuator Adapter.\"\"\"
    def __init__(self, device_id: str = "ESP32_NODE_01", baud_rate: int = 115200):
        super().__init__(device_id, "ESP32-S3-DevKitC-1 v1.1 (Layer 1 CSI)", layer=1)
        self.baud_rate = baud_rate
        self.serial_handle = None
        self._last_check_time = 0.0
        self.check_connection()

    def check_connection(self, force: bool = False) -> DeviceConnectionStatus:
        with self.lock:
            now = time.time()
            if not force and (now - self._last_check_time < 3.0):
                return self.connection_status
            self._last_check_time = now"""

assert esp_old in content, "esp_old not found"
content = content.replace(esp_old, esp_new, 1)

# 2. Patch CameraLayer3Adapter
cam_old = """class CameraLayer3Adapter(BaseHardwareAdapter):
    \"\"\"Layer 3: PTZ Surveillance Camera (CAM_01 / ESP32-CAM) Wake & Capture Adapter.\"\"\"
    def __init__(self, device_id: str = "CAM_01", ip_address: str = "192.168.4.1"):
        super().__init__(device_id, "PTZ Surveillance Camera CAM_01 (Layer 3)", layer=3)
        self.ip_address = ip_address
        self.port_or_endpoint = f"http://{ip_address}/"
        self.check_connection()

    def check_connection(self) -> DeviceConnectionStatus:
        with self.lock:
            # Test ping/HTTP to ESP32-CAM node
            try:
                import urllib.request
                req = urllib.request.Request(f"http://{self.ip_address}/status", headers={"User-Agent": "PRW-Wild"})
                with urllib.request.urlopen(req, timeout=0.3) as resp:
                    if resp.status == 200:
                        self.physical_connected = True
                        self.connection_status = DeviceConnectionStatus.CONNECTED
                        self.last_error = None
                        return self.connection_status
            except Exception as e:
                self.physical_connected = False
                self.connection_status = DeviceConnectionStatus.DISCONNECTED
                self.last_error = f"Camera endpoint unreachable: {e}"
            return self.connection_status"""

cam_new = """class CameraLayer3Adapter(BaseHardwareAdapter):
    \"\"\"Layer 3: PTZ Surveillance Camera (CAM_01 / ESP32-CAM) Wake & Capture Adapter.\"\"\"
    def __init__(self, device_id: str = "CAM_01", ip_address: str = "192.168.4.1"):
        super().__init__(device_id, "PTZ Surveillance Camera CAM_01 (Layer 3)", layer=3)
        self.ip_address = ip_address
        self.port_or_endpoint = f"http://{ip_address}/"
        self._last_check_time = 0.0
        self.check_connection()

    def check_connection(self, force: bool = False) -> DeviceConnectionStatus:
        with self.lock:
            now = time.time()
            if not force and (now - self._last_check_time < 5.0):
                return self.connection_status
            self._last_check_time = now

            # Fast socket probe with 0.08s timeout to avoid blocking if CAM node is offline
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.08)
                s.connect((self.ip_address, 80))
                s.close()
                self.physical_connected = True
                self.connection_status = DeviceConnectionStatus.CONNECTED
                self.last_error = None
            except Exception as e:
                self.physical_connected = False
                self.connection_status = DeviceConnectionStatus.DISCONNECTED
                self.last_error = f"Camera endpoint unreachable ({self.ip_address}:80): {e}"
            return self.connection_status"""

assert cam_old in content, "cam_old not found"
content = content.replace(cam_old, cam_new, 1)

fp.write_text(content, encoding="utf-8")
print("Successfully patched control_service.py with throttled fast probes!")

