#!/usr/bin/env python3
"""Search the theme-media channels for licence-clean candidates.

Usage:
    media-search.py "<query>" [--channel wikimedia|pixabay|pexels|unsplash]...
                            [--min-width 2560] [--limit 12]

Keys are read from the environment (.env in the firstmate home):
PIXABAY_API_KEY, PEXELS_API_KEY, UNSPLASH_ACCESS_KEY. Wikimedia needs none.
Prints one candidate per line: channel | size | licence | author | id/url | tags.
"""
import argparse, json, os, sys, urllib.parse, urllib.request

UA = {"User-Agent": "shine-themis-sourcing/1.0"}
DENY = ("CC BY-SA", "CC-BY-SA", "ShareAlike")


def get(url, headers=None, timeout=60):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def wikimedia(q, limit):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": q, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "size|mime|extmetadata|url"})
    out = []
    for p in (get(url).get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata") or {}
        lic = (em.get("LicenseShortName") or {}).get("value", "?")
        out.append({"channel": "wikimedia", "title": p["title"][5:],
                    "width": ii.get("width"), "height": ii.get("height"),
                    "license": lic, "author": (em.get("Artist") or {}).get("value", "?"),
                    "url": ii.get("url"), "tags": ii.get("mime", "")})
    return out


def pixabay(q, limit):
    key = os.environ.get("PIXABAY_API_KEY") or die("PIXABAY_API_KEY")
    out = []
    for kind in ("videos", "images"):
        url = "https://pixabay.com/api/%s/?" % kind + urllib.parse.urlencode({
            "key": key, "q": q, "per_page": str(min(limit, 20)), "safesearch": "true"})
        for h in get(url).get("hits", []):
            if kind == "videos":
                v = h["videos"].get("large") or {}
                out.append({"channel": "pixabay", "title": str(h["id"]),
                            "width": v.get("width"), "height": v.get("height"),
                            "license": "Pixabay Content License",
                            "author": h.get("user", "?"), "url": v.get("url"),
                            "tags": h.get("tags", "")})
            else:
                out.append({"channel": "pixabay", "title": str(h["id"]),
                            "width": h.get("imageWidth"), "height": h.get("imageHeight"),
                            "license": "Pixabay Content License",
                            "author": h.get("user", "?"), "url": h.get("largeImageURL"),
                            "tags": h.get("tags", "")})
    return out


def pexels(q, limit):
    key = os.environ.get("PEXELS_API_KEY") or die("PEXELS_API_KEY")
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode({
        "query": q, "per_page": str(min(limit, 20)), "orientation": "landscape"})
    out = []
    for v in get(url, {"Authorization": key}).get("videos", []):
        f = max(v.get("video_files", []), key=lambda x: x.get("width") or 0)
        out.append({"channel": "pexels", "title": str(v["id"]),
                    "width": f.get("width"), "height": f.get("height"),
                    "license": "Pexels License", "author": v.get("user", {}).get("name", "?"),
                    "url": f.get("link"), "tags": "%ss %s" % (v.get("duration"), v.get("url", ""))})
    return out


def unsplash(q, limit):
    key = os.environ.get("UNSPLASH_ACCESS_KEY") or die("UNSPLASH_ACCESS_KEY")
    url = "https://api.unsplash.com/search/photos?" + urllib.parse.urlencode({
        "query": q, "per_page": str(min(limit, 20)), "orientation": "landscape"})
    out = []
    for p in get(url, {"Authorization": "Client-ID " + key}).get("results", []):
        out.append({"channel": "unsplash", "title": p["id"], "width": p["width"],
                    "height": p["height"], "license": "Unsplash License (credit required)",
                    "author": p["user"]["name"], "url": p["urls"]["raw"],
                    "tags": p.get("alt_description") or ""})
    return out


def die(name):
    sys.exit("missing environment variable %s (see the skill's section 1)" % name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--channel", action="append",
                    choices=["wikimedia", "pixabay", "pexels", "unsplash"])
    ap.add_argument("--min-width", type=int, default=2560)
    ap.add_argument("--limit", type=int, default=12)
    a = ap.parse_args()
    rows = []
    for ch in (a.channel or ["wikimedia", "pixabay", "pexels", "unsplash"]):
        try:
            rows += {"wikimedia": wikimedia, "pixabay": pixabay,
                     "pexels": pexels, "unsplash": unsplash}[ch](a.query, a.limit)
        except SystemExit:
            print("skip %s: %s" % (ch, sys.exc_info()[1]), file=sys.stderr)
        except Exception as e:
            print("skip %s: %s" % (ch, e), file=sys.stderr)
    keep = [r for r in rows if (r.get("width") or 0) >= a.min_width
            and not any(d in r["license"] for d in DENY)]
    keep.sort(key=lambda r: -(r.get("width") or 0))
    for r in keep[:a.limit * 2]:
        print("%-10s %sx%-6s %-30s %-22s %s | %s" % (
            r["channel"], r["width"], r["height"], r["license"][:30],
            str(r["author"])[:22], r["title"], str(r["tags"])[:60]))
    print("# %d usable of %d inspected" % (len(keep), len(rows)), file=sys.stderr)


if __name__ == "__main__":
    main()
