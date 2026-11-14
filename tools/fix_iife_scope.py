app_path = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"
with open(app_path, "r", encoding="utf-8") as f:
    text = f.read()

target = """  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();"""

replacement = """  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }"""

assert target in text, "Target not found"
text = text.replace(target, replacement, 1)

# Append })(); to the very end
text = text.rstrip() + "\n\n})();\n"

with open(app_path, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: Moved })(); to end of app.js")

