#!/usr/bin/env python3
import urllib.request, json, os

out = "/Users/megan/blackcatrobotics-repo/TechMedix-standalone/public/images/platforms/virtual_incision_mira.jpg"

# NASA images API
req = urllib.request.Request("https://images-api.nasa.gov/search?q=MIRA+Virtual+Incision&media_type=image")
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read())

items = data.get("collection", {}).get("items", [])
for item in items[:5]:
    print("item links:", [l.get("href") for l in item.get("links", [])][:3])

# Try to get the image from the first item's metadata
if items:
    # Get the asset JSON
    asset_url = items[0].get("href")
    req2 = urllib.request.Request(asset_url)
    with urllib.request.urlopen(req2, timeout=15) as r2:
        asset = json.loads(r2.read())
    print("asset type:", type(asset))
    if isinstance(asset, list):
        print("first entries:", asset[:3])
    elif isinstance(asset, dict):
        print("keys:", list(asset.keys())[:5])
