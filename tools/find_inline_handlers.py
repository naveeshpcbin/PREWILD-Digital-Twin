import re

with open(r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\index.html", "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'on\w+=["\'][^"\']+["\']', text)
print(f"Total inline handlers: {len(matches)}")
for m in sorted(set(matches)):
    print("  ", m)

