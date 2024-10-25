#!/usr/bin/env python3

import hashlib
import sys
import urllib.request

if len(sys.argv) != 2 or not sys.argv[1].endswith(".zip"):
    print("Usage: download.py <filename relative to dl.unvanquished.net/release/>", file=sys.stderr)
    print("Download a release zip to zips/ and verify hash", file=sys.stderr)
    sys.exit(1)

name = sys.argv[1]

with urllib.request.urlopen("https://dl.unvanquished.net/release/" + name[:-3] + "sha512sum") as r:
    sha_expect = r.read().decode("utf8").split()[0]
assert len(sha_expect) == 128

urllib.request.urlretrieve("http://dl.unvanquished.net/release/" + name, "zips/" + name)

sha_actual = hashlib.sha512(open("zips/" + name, "rb").read()).hexdigest()
if sha_actual != sha_expect:
    print("ERROR: SHA512 sum of", name, "does not match", file=sys.stderr)
    print("Expected:", sha_expect, file=sys.stderr)
    print("Actual:", sha_actual, file=sys.stderr)
    exit(1)
