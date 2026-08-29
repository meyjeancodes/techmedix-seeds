#!/usr/bin/env python3
"""Apply /Users/megan/tm-seeds/pending/*.json failure modes to Supabase (LIVE).

Uses `supabase db query --linked` (no .env.local required). Idempotent: skips
platforms that already have failure_modes, and skips individual failure_modes
whose (platform, component, symptom) already exists.

Usage:
  python3 ~/tm-seeds/apply_fms.py --dry-run
  python3 ~/tm-seeds/apply_fms.py
"""
import re, json, subprocess, sys, glob, os

DRY = '--dry-run' in sys.argv
HOME = os.path.expanduser("~")

SEVOK = {'low', 'medium', 'high', 'critical'}

def q(sql):
    out = subprocess.run(["supabase", "db", "query", "--linked", sql],
                         capture_output=True, text=True, cwd=HOME)
    raw = out.stdout
    start = raw.find("{")
    if start == -1:
        return []
    try:
        return json.loads(raw[start:]).get("rows", [])
    except Exception:
        m = re.search(r'"rows"\s*:\s*(\[.*\])\s*}', raw, re.S)
        return json.loads(m.group(1)) if m else []

def run(sql):
    r = subprocess.run(["supabase", "db", "query", "--linked", sql],
                       capture_output=True, text=True, cwd=HOME)
    if r.returncode != 0:
        raise RuntimeError(f"SQL failed: {(r.stderr or r.stdout)[:300]}")
    # PostgREST requires a body for inserts; --linked prints a boundary blob.
    return r.stdout

# Preload platforms
plats = {r["slug"]: r["id"] for r in q("SELECT id, slug FROM platforms;")}

inserted = 0
skipped = 0
for fn in sorted(glob.glob(os.path.join(HOME, 'tm-seeds/pending/*.json'))):
    seed = json.load(open(fn))
    slug = seed['slug']
    pid = plats.get(slug)
    if not pid:
        print(f"!! {slug}: no platform row in DB"); continue
    existing = q(f"SELECT id, component, symptom FROM failure_modes WHERE platform_id='{pid}';")
    if existing:
        print(f"{slug}: already {len(existing)} FMs, skip platform")
        skipped += 1
        continue
    rows = []
    for f in seed.get('failure_modes', []):
        sev = str(f.get('severity', 'medium')).lower()
        if sev not in SEVOK: sev = 'medium'
        sym = f.get('symptoms') or f.get('name') or 'not specified'
        if isinstance(sym, list): sym = '; '.join(map(str, sym))
        root = f.get('name', '')
        if f.get('mitigation'): root += f"; mitigation: {f['mitigation']}"
        rows.append(
            f"('{pid}','{str(f.get('component') or 'general').replace(chr(39),'')}',"
            f"'{sev}',{f.get('mtbf_hours_est') or 'NULL'},"
            f"'{str(sym).replace(chr(39),'')}',"
            f"'{str(root).replace(chr(39),'')}','medium',"
            f"ARRAY['{slug}'],ARRAY['fmea-engineering-estimate'])"
        )
    print(f"{slug}: INSERT {len(rows)}")
    if rows and not DRY:
        vals = ",".join(rows)
        run("INSERT INTO failure_modes "
            "(platform_id, component, severity, mtbf_hours, symptom, root_cause, confidence, tags, source_urls) "
            f"VALUES {vals} ON CONFLICT DO NOTHING;")
        inserted += len(rows)

print("done", "(dry-run)" if DRY else "", f"| inserted={inserted} skipped_platforms={skipped}")
