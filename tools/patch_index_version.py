path = r'D:\Simulation For DT\prw-wild-digital-twin\src\prw_wild\web\static\index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
target = '<script src="app.js?v=20261016"></script>'
assert target in c, f"Target {target} not found"
c = c.replace(target, '<script src="app.js?v=20261103_locomotion_fix"></script>')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated index.html app.js version tag!')

