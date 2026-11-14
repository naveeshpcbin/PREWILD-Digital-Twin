import os

server_py_path = r'D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\server.py'
with open(server_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '    def __init__(self, *args, **kwargs):\n        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)'
if target not in content:
    target = '    def __init__(self, *args, **kwargs):\r\n        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)'

assert target in content, "Could not find init in server.py"

replacement = target + '''

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()'''.replace('\n', '\r\n' if '\r\n' in target else '\n')

content = content.replace(target, replacement, 1)

with open(server_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated server.py with no-cache headers!")

