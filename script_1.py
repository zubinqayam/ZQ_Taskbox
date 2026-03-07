
import zipfile
import os

zip_path = "output/innm-taskbox-v2-repo.zip"
base = "output/innm-taskbox"

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(base):
        for f in files:
            fp = os.path.join(root, f)
            arcname = os.path.relpath(fp, "output")
            zf.write(fp, arcname)

print(f"ZIP created: {zip_path}")
print(f"Size: {os.path.getsize(zip_path)} bytes")

# List contents
with zipfile.ZipFile(zip_path, 'r') as zf:
    for info in zf.infolist():
        print(f"  {info.filename}  ({info.file_size} bytes)")
