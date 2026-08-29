#!/usr/bin/env python3
"""Set platforms.image_url from existing real photos in public/images/platforms/.
Usage: python3 ~/tm-seeds/set_image_urls.py [--dry-run]"""
import re, json, subprocess, sys, os

DRY = '--dry-run' in sys.argv
IMGDIR = '/Users/megan/blackcatrobotics-repo/TechMedix-standalone/public/images/platforms'
ENVFILE = '/Users/megan/blackcatrobotics-repo/TechMedix-standalone/.env.local'
env = {}
for l in open(ENVFILE):
    m = re.match(r'([^=#]+)=(.*)', l.strip())
    if m: env[m.group(1).strip()] = m.group(2).strip().strip('"\'')
URL = env['NEXT_PUBLIC_SUPABASE_URL']; KEY = env['SUPABASE_SERVICE_ROLE_KEY']

def req(method, path, body=None):
    cmd = ['curl','-s','-X',method,f"{URL}/rest/v1/{path}",
        '-H',f'apikey: {KEY}','-H',f'Authorization: Bearer {KEY}',
        '-H','Content-Type: application/json','-H','Prefer: return=representation']
    if body is not None: cmd += ['-d', json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try: return json.loads(out.stdout) if out.stdout.strip() else []
    except Exception: return {"_error": out.stdout[:200]}

# slug -> filename (real photos only, no svg)
MAP = {
 'boston_dynamics_spot': 'bostondynamics_spot.jpg',
 'unitree_g1': 'unitree_g1.jpg',
 'unitree-h1-2': 'unitree_h1_2.png',
 'unitree-b2': 'unitree_b2.png',
 'figure-02': 'figure_02.jpg',
 'tesla-optimus': 'tesla_optimus.jpg',
 'asimov-here-be-dragons': 'asimov_1.jpg',
 'dji_agras_t50': 'dji_agras_t50.jpg',
 'dji_matrice_350': 'dji_matrice350.jpg',
 'skydio_x10': 'skydio_x10.jpg',
 'zipline_p2': 'zipline_p2.png',
 'serve-rs2': 'serve_rs2.jpg',
 'starship_gen3': 'starship_gen3.jpg',
 'amazon_proteus': 'amazon_proteus.jpg',
 'bird_three': 'bird_three.jpg',
 'lime_gen4': 'lime_ebike.jpg',
 'rad_commercial': 'rad_power.png',
}
for slug, fn in MAP.items():
    path = os.path.join(IMGDIR, fn)
    if not os.path.exists(path):
        print(f"!! {slug}: {fn} missing on disk"); continue
    url = f"/images/platforms/{fn}"
    print(f"{slug}: image_url = {url}")
    if not DRY:
        r = req('PATCH', f"platforms?slug=eq.{slug}", {"image_url": url})
        if isinstance(r, dict) or not r: print("   error/no-row:", r)
print("done", "(dry-run)" if DRY else "")
