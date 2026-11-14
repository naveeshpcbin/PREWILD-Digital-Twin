import urllib.request
import re

url = "https://kenney.nl/assets/nature-kit"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        links = [m for m in re.findall(r'href=[\'"]([^\'"]+)[\'"]', html) if "download" in m or ".zip" in m]
        print("Kenney links:", links)
except Exception as e:
    print("Error:", e)

