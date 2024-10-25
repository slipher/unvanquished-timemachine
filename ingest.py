#!/usr/bin/env python3

import hashlib
import os
import sys
import zipfile

if len(sys.argv) != 3:
    print("Usage: ingest.py <release version> <path to zip>", file=sys.stderr)
    print("Unpack and deduplicate files needed for x86 Windows game", file=sys.stderr)
    sys.exit(1)

_, version, path = sys.argv

z = zipfile.ZipFile(path)
names = [info.filename for info in z.infolist() if not info.is_dir()]
winx86zips = []

def bad_single(basename):
    if "." not in basename and basename != "md5sums":
        return True
    for ext in (".so", ".zip", ".xz", ".bz2"):
        if basename.endswith(ext):
            return True
    return False

i = 0
while i < len(names):
    name = names[i]
    for bad in ("/lib64/", "/Unvanquished.app/", "__MACOSX/"):
        start = name.find(bad)
        if ~start:
            old_n = len(names)
            names = [s for s in names if s[start:start+len(bad)] != bad]
            print("Ignoring %s (%s files)" % (name[:start+len(bad)], old_n - len(names)))
            break
    else:
        basename = name.split("/")[-1]
        if basename in ("win32.zip", "win.zip", "windows-i686.zip"):
            print("Extracting " + name)
            winx86zips.append(name)
            names.pop(i)
        elif bad_single(basename):
            print("Ignoring " + name)
            names.pop(i)
        elif name.lower() in map(str.lower, names[:i]):
            print("Ignoring " + name + " because another file has the same name!")
            names.pop(i)
        else:
            i += 1
            print("Adding " + name)

prefix = names[0][:names[0].index("/") + 1]
assert all(name.startswith(prefix) for name in names)
assert len(winx86zips) < 2

root = os.path.join("unv", version)
os.mkdir(root)

def put_file(name, f):
    content = f.read()
    sha = hashlib.sha256(content).hexdigest()
    store = os.path.join("data", sha)
    if os.path.isfile(store):
        assert os.stat(store).st_size == len(content)
    else:
        with open(store, "wb") as out:
            out.write(content)
    link = os.path.join(root, name)
    os.makedirs(os.path.dirname(link), exist_ok=True)
    target = os.path.relpath(store, os.path.dirname(link))
    os.symlink(target, link)

for name in names:
    with z.open(name) as f:
        put_file(name[len(prefix):], f)
for wz in winx86zips:
    wz = zipfile.ZipFile(z.open(wz))
    for info in wz.infolist():
        if not info.is_dir():
            with wz.open(info) as f:
                put_file(info.filename, f)
