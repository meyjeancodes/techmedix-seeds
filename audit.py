#!/usr/bin/env python3
"""
audit.py — audit TechMedix platform/failure-mode coverage against the LIVE
Supabase DB (via `supabase db query --linked`, no .env.local required).

Usage:
  python3 audit.py                 # full per-platform table
  python3 audit.py --gaps          # only rows with a missing FM/spec/image
"""
import sys, json, subprocess
from collections import defaultdict

def q(sql):
    out = subprocess.run(["supabase", "db", "query", "--linked", sql],
                         capture_output=True, text=True, cwd=os.path.expanduser("~"))
    raw = out.stdout
    start = raw.find("{")
    if start == -1:
        return []
    try:
        return json.loads(raw[start:]).get("rows", [])
    except Exception:
        import re
        m = re.search(r'"rows"\s*:\s*(\[.*\])\s*}', raw, re.S)
        return json.loads(m.group(1)) if m else []

import os

GAPS_ONLY = "--gaps" in sys.argv

plats = q("SELECT id, slug, type, techmedix_status, specs_json, notes, image_url FROM platforms ORDER BY slug;")
fm = defaultdict(int)
for r in q("SELECT platform_id FROM failure_modes;"):
    if r.get("platform_id"):
        fm[r["platform_id"]] += 1

rp = defaultdict(int)
for r in q("SELECT failure_mode_id FROM repair_protocols;"):
    if r.get("failure_mode_id"):
        rp[r["failure_mode_id"]] += 1

fm_by_id = {r["id"]: r for r in q("SELECT id, severity FROM failure_modes;")}
crit_no_rp = q("""SELECT count(*) AS n FROM failure_modes fm
                  WHERE fm.severity='critical'
                  AND NOT EXISTS (SELECT 1 FROM repair_protocols rp WHERE rp.failure_mode_id=fm.id);""")

print(f"{len(plats)} platforms")
miss = 0
for p in plats:
    pid = p["id"]
    fmcount = fm[pid]
    specs = "Y" if p.get("specs_json") else "-"
    notes = "Y" if p.get("notes") else "-"
    img = "Y" if p.get("image_url") else "-"
    row_fm = fmcount
    bad = (row_fm == 0) or (specs == "-") or (img == "-")
    if bad:
        miss += 1
    if GAPS_ONLY and not bad:
        continue
    flag = "  <-- GAP" if bad else ""
    print(f"{p['slug']:34} {str(p.get('type'))[:20]:20} {p.get('techmedix_status'):14} FM={row_fm:2} specs={specs} notes={notes} img={img}{flag}")

print()
print(f"Platforms with a coverage gap: {miss}/{len(plats)}")
print(f"Critical failure modes WITHOUT a repair protocol: {crit_no_rp[0]['n'] if crit_no_rp else '?'}")

# Blueprint coverage (repo-side): count platforms that have a CHASSIS_REGISTRY hit
print()
print("Blueprint coverage (CHASSIS_REGISTRY) is computed by the dashboard at render time;")
print("run `npm run build` in TechMedix-standalone to confirm zero 'falling back to mock'.")
