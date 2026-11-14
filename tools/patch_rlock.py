"""Update locks to RLock in control_service.py."""
from pathlib import Path

fp = Path(r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\hardware\control_service.py")
content = fp.read_text(encoding="utf-8")

content = content.replace("self.lock = threading.Lock()", "self.lock = threading.RLock()")
content = content.replace("_lock = threading.Lock()", "_lock = threading.RLock()")
content = content.replace("self.history_lock = threading.Lock()", "self.history_lock = threading.RLock()")

fp.write_text(content, encoding="utf-8")
print("Updated all locks to RLock!")

