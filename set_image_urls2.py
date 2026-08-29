#!/usr/bin/env python3
import re, json, subprocess, os
ENVFILE = '/Users/megan/blackcatrobotics-repo/TechMedix-standalone/.env.local'
IMGDIR = '/Users/megan/blackcatrobotics-repo/TechMedix-standalone/public/images/platforms'
env = {}
for l in open(ENVFILE):
    m = re.match(r'([^=#]+)=(.*)', l.strip())
    if m: env[m.group(1).strip()] = m.group(2).strip().strip('"\'')
URL = env['NEXT_PUBLIC_SUPABASE_URL']; KEY = env['SUPABASE_SERVICE_ROLE_KEY']
def patch(slug, url):
    out = subprocess.run(['curl','-s','-X','PATCH',f"{URL}/rest/v1/platforms?slug=eq.{slug}",
        '-H',f'apikey: {KEY}','-H',f'Authorization: Bearer {KEY}',
        '-H','Content-Type: application/json','-H','Prefer: return=representation',
        '-d', json.dumps({"image_url": url})], capture_output=True, text=True)
    try:
        r = json.loads(out.stdout)
        return len(r) if isinstance(r, list) else str(r)[:80]
    except Exception: return out.stdout[:80]
MAP = {
 'intuitive-davinci': 'intuitive_davinci.jpg',
 'jnj-ottava': 'jnj_ottava.jpg',
 'medtronic-hugo': 'medtronic_hugo.jpg',
 'cmr-versius': 'cmr_versius.jpg',
 'asensus-senhance': 'asensus_senhance.jpg',
 'stryker-mako': 'stryker_mako.png',
 'ekso-eksonr': 'ekso_eksonr.jpg',
 'dji-agras-t60': 'dji_agras_t60.jpg',
 'dewalt-dale': 'dewalt_dale.jpg',
 'lely-discovery-collector': 'lely_discovery_collector.jpg',
 'veo-s1': 'veo_s1.jpg',
}
for slug, fn in MAP.items():
    assert os.path.exists(os.path.join(IMGDIR, fn)), fn
    print(slug, '->', patch(slug, f"/images/platforms/{fn}"))
