#!/usr/bin/env python3
"""Download candidates and dump one probe frame each, for eyeball review.

Usage:
    media-fetch.py <outdir> <url> [<url> ...] [--cap-mb 80] [--at 3]

Writes <outdir>/<n>.<ext> and <outdir>/probe-<n>.jpg. Review the probes at full size
before building anything - HUDs, title cards and people only show up visually.
"""
import argparse, os, subprocess, sys, urllib.request

UA = {"User-Agent": "shine-themis-sourcing/1.0"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--cap-mb", type=int, default=80)
    ap.add_argument("--at", type=float, default=3.0)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    for i, url in enumerate(a.urls, 1):
        ext = ".jpg" if url.lower().split("?")[0].endswith((".jpg", ".jpeg")) else ".mp4"
        path = os.path.join(a.outdir, "%02d%s" % (i, ext))
        cap = a.cap_mb * 1024 * 1024
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r, open(path, "wb") as f:
                n = 0
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    n += len(chunk)
                    if n > cap:
                        break
        except Exception as e:
            print("download failed %s: %s" % (url, e), file=sys.stderr)
            continue
        probe = os.path.join(a.outdir, "probe-%02d.jpg" % i)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(a.at), "-i", path,
                        "-frames:v", "1", "-vf", "scale=1600:-2", "-q:v", "4", probe], check=False)
        print("%s  %s  probe=%s" % (path, os.path.getsize(path) // 1024, probe))


if __name__ == "__main__":
    main()
