import os

app_js_path = r'D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

export_block = '''  window.updateSimulationStateAtTime = updateSimulationStateAtTime;
  window.syncThreeScene = syncThreeScene;
  window.getGroundTruthAtTime = getGroundTruthAtTime;
  window.setCameraView = setCameraView;
'''

if 'window.updateSimulationStateAtTime =' not in content:
    content = content.replace('})();', export_block + '\n})();')
    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Exported window helpers successfully!")
else:
    print("Already exported.")

