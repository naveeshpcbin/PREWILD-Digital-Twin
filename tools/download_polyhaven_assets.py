import os
import urllib.request
import json

DOWNLOAD_DIR = r"D:\Simulation For DT\prw-wild-digital-twin\assets\downloads\polyhaven"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

models = ['quiver_tree_01', 'wild_rooibos_bush', 'shrub_02', 'shrub_03', 'shrub_04']

def download_file(url, target_path):
    if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
        print(f"Already exists: {target_path} ({os.path.getsize(target_path)/1024:.1f} KB)")
        return True
    print(f"Downloading: {url} -> {target_path}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp, open(target_path, 'wb') as out:
            data = resp.read()
            out.write(data)
            print(f"Saved: {target_path} ({len(data)/1024:.1f} KB)")
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

for m in models:
    api_url = f"https://api.polyhaven.com/files/{m}"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        # Download 1k FBX if available
        fbx_info = data.get('fbx', {}).get('1k', {}).get('fbx')
        if fbx_info and 'url' in fbx_info:
            target_fbx = os.path.join(DOWNLOAD_DIR, f"{m}_1k.fbx")
            download_file(fbx_info['url'], target_fbx)
            
        # Download Diffuse, Normal, Roughness textures
        for tex_type in ['Diffuse', 'nor_gl', 'Rough', 'branch_diff', 'branch_nor_gl', 'leaves_diff', 'leaves_nor_gl', 'leaves_alpha']:
            tex_info = data.get(tex_type, {}).get('1k', {})
            # format could be jpg or png
            for fmt in ['jpg', 'png']:
                finfo = tex_info.get(fmt)
                if finfo and 'url' in finfo:
                    tex_file = os.path.join(DOWNLOAD_DIR, f"{m}_{tex_type}_1k.{fmt}")
                    download_file(finfo['url'], tex_file)
                    break
    except Exception as e:
        print(f"Error processing {m}: {e}")

print("Download complete! Files in directory:")
for f in os.listdir(DOWNLOAD_DIR):
    fp = os.path.join(DOWNLOAD_DIR, f)
    print(f"  {f} ({os.path.getsize(fp)/1024:.1f} KB)")

