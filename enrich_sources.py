#!/usr/bin/env python3
"""Enrich platform_sources: add model citations for medical platforms + fix gaps.

Adds GR00T-H and Cosmos-H-Surgical-Simulator model citations to all medical
surgical robot platforms (since both models are trained on Open-H-Embodiment,
which covers all of them). Also adds sources for Asimov (0-source platform).

Idempotent: uses ON CONFLICT DO NOTHING.

Usage:
  python3 ~/tm-seeds/enrich_sources.py --dry-run
  python3 ~/tm-seeds/enrich_sources.py
"""
import json, os, subprocess, sys

DRY = '--dry-run' in sys.argv
HOME = os.path.expanduser("~")

# ── Source entries to add ──────────────────────────────────────────────────
# Each entry: (slug, source_type, source_name, source_url, license, description)
ENTRIES = [
    # Model citations for all medical surgical robots (GR00T-H + Cosmos-H trained on Open-H)
    ("virtual-incision-mira", "model", "GR00T-H",
     "https://huggingface.co/nvidia/GR00T-H",
     "NVIDIA Open",
     "3B VLA foundation model for surgical robotics, trained on Open-H-Embodiment"),
    ("virtual-incision-mira", "model", "Cosmos-H-Surgical-Simulator",
     "https://huggingface.co/nvidia/Cosmos-H-Surgical-Simulator",
     "NVIDIA Open",
     "Action-conditioned surgical world foundation model for policy evaluation"),
    ("moon-surgical-maestro", "model", "GR00T-H",
     "https://huggingface.co/nvidia/GR00T-H",
     "NVIDIA Open",
     "3B VLA foundation model for surgical robotics"),
    ("moon-surgical-maestro", "model", "Cosmos-H-Surgical-Simulator",
     "https://huggingface.co/nvidia/Cosmos-H-Surgical-Simulator",
     "NVIDIA Open",
     "Action-conditioned surgical world foundation model"),
    ("rob-surgical-bitrack", "model", "GR00T-H",
     "https://huggingface.co/nvidia/GR00T-H",
     "NVIDIA Open",
     "3B VLA foundation model for surgical robotics"),
    ("rob-surgical-bitrack", "model", "Cosmos-H-Surgical-Simulator",
     "https://huggingface.co/nvidia/Cosmos-H-Surgical-Simulator",
     "NVIDIA Open",
     "Action-conditioned surgical world foundation model"),
    ("torin-surgical", "model", "GR00T-H",
     "https://huggingface.co/nvidia/GR00T-H",
     "NVIDIA Open",
     "3B VLA foundation model for surgical robotics"),
    ("torin-surgical", "model", "Cosmos-H-Surgical-Simulator",
     "https://huggingface.co/nvidia/Cosmos-H-Surgical-Simulator",
     "NVIDIA Open",
     "Action-conditioned surgical world foundation model"),
    ("asensus-senhance", "model", "GR00T-H",
     "https://huggingface.co/nvidia/GR00T-H",
     "NVIDIA Open",
     "3B VLA foundation model for surgical robotics"),
    ("cmr-versius", "model", "GR00T-H",
     "https://huggingface.co/nvidia/GR00T-H",
     "NVIDIA Open",
     "3B VLA foundation model for surgical robotics"),
    ("jnj-ottava", "model", "GR00T-H",
     "https://huggingface.co/nvidia/GR00T-H",
     "NVIDIA Open",
     "3B VLA foundation model for surgical robotics"),
    ("medtronic-hugo", "model", "GR00T-H",
     "https://huggingface.co/nvidia/GR00T-H",
     "NVIDIA Open",
     "3B VLA foundation model for surgical robotics"),

    # Asimov is intentionally a fictional internal prototype — skip
]


def q(sql):
    out = subprocess.run(
        ["supabase", "db", "query", "--linked", sql],
        capture_output=True, text=True, cwd=HOME
    )
    return out.stdout


def run_sql(sql):
    r = subprocess.run(
        ["supabase", "db", "query", "--linked", sql],
        capture_output=True, text=True, cwd=HOME
    )
    if r.returncode != 0:
        raise RuntimeError(f"SQL failed: {(r.stderr or r.stdout)[:300]}")
    return r.stdout


def main():
    # Preload platforms
    plats = {r["slug"]: r["id"] for r in json.loads(
        q("SELECT id, slug FROM platforms;")
    ).get("rows", [])}

    inserted = 0
    for slug, stype, sname, surl, lic, desc in ENTRIES:
        pid = plats.get(slug)
        if not pid:
            print(f"!! {slug}: no platform row"); continue

        # Check if source already exists
        existing = q(
            f"SELECT id FROM platform_sources "
            f"WHERE platform_id='{pid}' AND source_url='{surl}';"
        )
        if '"rows": [{"id":' in existing or '"rows": [{"id"' in existing:
            print(f"  {slug}/{sname}: already exists, skip")
            continue

        lic_val = f"'{lic}'" if lic else "NULL"
        desc_val = f"'{desc}'" if desc else "NULL"
        sql = (
            f"INSERT INTO platform_sources "
            f"(platform_id, source_type, source_name, source_url, license, description) "
            f"VALUES ('{pid}', '{stype}', '{sname}', '{surl}', {lic_val}, {desc_val}) "
            f"ON CONFLICT DO NOTHING;"
        )
        print(f"  {slug}: ADD {stype}/{sname}")
        if not DRY:
            run_sql(sql)
            inserted += 1

    print(f"\ndone {'(dry-run)' if DRY else ''} | inserted={inserted}")


if __name__ == "__main__":
    main()
