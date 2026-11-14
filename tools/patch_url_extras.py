import os

APP_JS = r"D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js"
with open(APP_JS, "r", encoding="utf-8") as f:
    code = f.read()

target = """    const injectParam = urlParams.get('inject');
    if (injectParam === 'approach') {
      setTimeout(() => document.getElementById('btnInjectApproach')?.click(), 800);
    } else if (injectParam === 'cross') {
      setTimeout(() => document.getElementById('btnInjectCross')?.click(), 800);
    }"""

replacement = """    const injectParam = urlParams.get('inject');
    if (injectParam === 'approach') {
      setTimeout(() => document.getElementById('btnInjectApproach')?.click(), 800);
    } else if (injectParam === 'turnaway') {
      setTimeout(() => document.getElementById('btnInjectTurnAway')?.click(), 800);
    } else if (injectParam === 'cross') {
      setTimeout(() => document.getElementById('btnInjectCross')?.click(), 800);
    }
    const fsParam = urlParams.get('fullscreen');
    if (fsParam) {
      setTimeout(() => toggleTwinFullscreen(), 700);
    }"""

if target in code:
    code = code.replace(target, replacement, 1)
    with open(APP_JS, "w", encoding="utf-8") as f:
        f.write(code)
    print("Patched app.js with turnaway and fullscreen parameter handlers.")
else:
    print("Target not found in app.js")

