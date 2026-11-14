"""Updates setLabMode and init() with URL search parameters for automated browser test verification."""
from pathlib import Path

app_path = Path("src/prw_wild/web/static/app.js")
text = app_path.read_text(encoding="utf-8")

# 1. Update setLabMode
target_slm = "    } else if (mode === 'counterfactual') {\n      if (cfModal) cfModal.classList.remove('hidden');\n      loadCounterfactualData();\n    }"
repl_slm = """    } else if (mode === 'counterfactual') {
      if (cfModal) cfModal.classList.remove('hidden');
      loadCounterfactualData();
    } else if (mode === 'ecosystem') {
      if (lebBar) lebBar.classList.add('hidden');
      if (flTray) flTray.classList.add('hidden');
      const ecoPanel = document.getElementById('ecosystemPanel');
      if (ecoPanel) ecoPanel.scrollIntoView({ behavior: 'smooth' });
    }"""

if "else if (mode === 'ecosystem')" not in text:
    text = text.replace(target_slm, repl_slm)
    print("Updated setLabMode")

# 2. Update init()
target_init_call = "    runSimulation('approach_crossing', 42);\n  }"
repl_init_call = """    runSimulation('approach_crossing', 42);

    // URL Query Parameter Automation Handler
    const urlParams = new URLSearchParams(window.location.search);
    const modeParam = urlParams.get('mode');
    if (modeParam) {
      setTimeout(() => setLabMode(modeParam), 500);
    }
    const viewParam = urlParams.get('view');
    if (viewParam === '2d') {
      setTimeout(() => document.getElementById('btnView2D')?.click(), 300);
    } else if (viewParam === 'campov') {
      setTimeout(() => {
        const btn = document.querySelector("button[data-view='campov']");
        if (btn) btn.click();
        const win = document.getElementById('camPovFloatingWindow');
        if (win) win.classList.remove('hidden');
      }, 400);
    } else if (viewParam) {
      setTimeout(() => {
        const btn = document.querySelector("button[data-view='" + viewParam + "']");
        if (btn) btn.click();
      }, 400);
    }
    const injectParam = urlParams.get('inject');
    if (injectParam === 'approach') {
      setTimeout(() => document.getElementById('btnInjectApproach')?.click(), 800);
    } else if (injectParam === 'cross') {
      setTimeout(() => document.getElementById('btnInjectCross')?.click(), 800);
    }
  }"""

if "URL Query Parameter Automation Handler" not in text:
    text = text.replace(target_init_call, repl_init_call)
    print("Updated init() with URL params")

app_path.write_text(text, encoding="utf-8")
print("Done patching app.js URL params")

