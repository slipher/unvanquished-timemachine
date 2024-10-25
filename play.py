#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys

if len(sys.argv) < 2 or not os.path.isdir(os.path.join("unv", sys.argv[1])):
    print("Usage: play.py <version> [daemon args...]", file=sys.stderr)
    print("Starts Unvanquished with the homepath 'tmphome', which is cleared before starting.", file=sys.stderr)
    exit(1)

home = os.path.abspath("tmphome")
if os.path.isdir(home) and not os.path.islink(home):
    print("Wiping homepath:", home)
    shutil.rmtree(home)

# 0.17 (for example) looks for paks relative to the PWD instead of the binary path...
os.chdir(os.path.abspath(os.path.join("unv", sys.argv[1])))

subprocess.Popen([
    "daemon",
    "-homepath", home, # Set homepath for recent versions
    "+set", "fs_homepath", home, # Set homepath for old versions
    *sys.argv[2:]])
