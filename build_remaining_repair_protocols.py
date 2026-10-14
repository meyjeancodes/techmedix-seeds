#!/usr/bin/env python3
"""
Author repair_protocols for the remaining 55 non-critical failure modes
(29 high / 24 medium / 2 low) across manipulators, surgical robots, humanoids,
construction robots, ag-robots, and delivery drones.

Each protocol operationalizes the FM's DOCUMENTED mitigation (parsed out of
`root_cause`) into a real, ordered field procedure. This keeps every protocol
traceable to a source already in the DB rather than inventing new claims.

Idempotent: skips FM ids that already have a protocol.
Usage: python3 build_remaining_repair_protocols.py [--dry-run]
"""
import json, re, subprocess, sys, os

DRY = "--dry-run" in sys.argv
HOME = os.path.expanduser("~")

# Platforms whose FMs are prototype/placeholder — excluded, matching the
# existing seed scripts' convention.
SKIP_PLATFORMS = ("asimov-here-be-dragons",)


def q(sql):
    out = subprocess.run(["supabase", "db", "query", "--linked", "-f", "/dev/stdin"],
                         capture_output=True, text=True, cwd=HOME, input=sql)
    raw = out.stdout
    s = raw.find("{")
    if s == -1:
        return []
    try:
        return json.loads(raw[s:]).get("rows", [])
    except Exception:
        return []


def run(sql):
    r = subprocess.run(["supabase", "db", "query", "--linked", "-f", "/dev/stdin"],
                       capture_output=True, text=True, cwd=HOME, input=sql)
    if r.returncode != 0:
        raise RuntimeError(f"SQL failed: {(r.stderr or r.stdout)[:400]}")
    return r.stdout


GAP_SQL = """
SELECT fm.id, p.slug, p.name, fm.component, fm.severity, fm.symptom,
       fm.root_cause, fm.mtbf_hours
FROM failure_modes fm
JOIN platforms p ON p.id = fm.platform_id
WHERE NOT EXISTS (SELECT 1 FROM repair_protocols rp WHERE rp.failure_mode_id = fm.id)
ORDER BY p.slug, fm.severity DESC;
"""


def parse_mitigations(root_cause: str) -> list[str]:
    """Pull the documented mitigation list out of root_cause.

    Two shapes exist in the data:
      "...; mitigation: a; b; c"          (semicolon list)
      "Root cause prose. Mitigation: a, b, and c."  (prose)
    """
    if not root_cause:
        return []
    m = re.search(r"mitigation:\s*(.+)$", root_cause, re.I | re.S)
    if not m:
        return []
    tail = m.group(1).strip().rstrip(".")
    # Prose form uses commas + "and"; list form uses semicolons.
    if ";" in tail:
        parts = [p.strip() for p in tail.split(";") if p.strip()]
    else:
        tail = re.sub(r",?\s+and\s+", ", ", tail)
        parts = [p.strip() for p in tail.split(",") if p.strip()]
    return [p for p in parts if len(p) > 3]


SKILL_BY_SEVERITY = {"high": "intermediate", "medium": "intermediate", "low": "basic"}
LABOR_BY_SEVERITY = {"high": 45, "medium": 35, "low": 25}


def esc(s: str) -> str:
    return s.replace("'", "''")


def build_protocol(fm: dict) -> dict:
    sev = fm["severity"]
    mits = parse_mitigations(fm["root_cause"]) or [
        "Confirm the fault with the platform's diagnostic readout",
        "Apply the documented service action for this component",
        "Verify full function before return to service",
    ]
    plat = fm["name"] or fm["slug"]
    comp = fm["component"] or "component"
    symptom = fm["symptom"] or "reported fault"

    steps = []
    # Step 1 — always confirm the fault against the documented symptom.
    steps.append({
        "step": 1,
        "action": (
            f"Reproduce and confirm the reported symptom ({symptom}) on the "
            f"{comp} using the platform diagnostic readout before any disassembly."
        ),
        "tool": "Platform diagnostic readout / service software",
        "warning": (
            "Working on an unconfirmed fault = replacing good parts — always confirm "
            "the symptom against the documented failure mode first."
        ),
    })
    # Steps 2..N — one per documented mitigation, in order.
    for i, mit in enumerate(mits, start=2):
        steps.append({
            "step": i,
            "action": mit[0].upper() + mit[1:] + ".",
            "tool": f"{comp} service tooling (per platform manual)",
            "warning": (
                f"Skipping this documented mitigation leaves the documented root cause "
                f"({fm['root_cause'].split('mitigation')[0].strip().rstrip(';').strip()}) "
                f"unaddressed and the fault will recur."
            ),
        })
    # Final step — always verify before return to service.
    steps.append({
        "step": len(mits) + 2,
        "action": (
            "Verify full function before return to service: confirm the original symptom "
            "is gone, the component reports healthy, and run one duty cycle under load."
        ),
        "tool": "Platform functional test / duty cycle",
        "warning": (
            "A component serviced but not function-tested = an unverified repair — "
            "always prove the fault is gone before returning the unit to the fleet."
        ),
    })

    parts = [{
        "part_name": f"{comp} — service/replacement parts (per platform manual)",
        "part_number": None,
        "qty": 1,
        "supplier": "OEM / per platform manual",
        "unit_cost_usd": None,
    }]

    return {
        "failure_mode_id": fm["id"],
        "title": (
            f"{plat} — {comp}: {mits[0][0].upper() + mits[0][1:]}"
            + (f", then {mits[1]}" if len(mits) > 1 else "")
        )[:180],
        "skill_level": SKILL_BY_SEVERITY.get(sev, "intermediate"),
        "labor_minutes": LABOR_BY_SEVERITY.get(sev, 35),
        "tools_required": sorted({
            "Platform diagnostic readout / service software",
            f"{comp} service tooling (per platform manual)",
            "Platform functional test / duty cycle",
        }),
        "parts": parts,
        "steps": steps,
    }


def main():
    rows = q(GAP_SQL)
    rows = [r for r in rows if r["slug"] not in SKIP_PLATFORMS]
    print(f"Failure modes with no repair protocol (excl. placeholder platforms): {len(rows)}")

    existing = {r["failure_mode_id"] for r in
                q("SELECT failure_mode_id FROM repair_protocols;")}
    built, skipped = [], []
    for fm in rows:
        if fm["id"] in existing:
            skipped.append(fm["id"][:8])
            continue
        built.append(build_protocol(fm))

    if skipped:
        print(f"  Already exist (skipped): {len(skipped)}")
    print(f"  To insert: {len(built)}")

    from collections import Counter
    print("  By severity:", dict(Counter(r["severity"] for r in rows)))
    print("  By platform:", dict(Counter(r["slug"] for r in rows)))

    if DRY:
        print("(dry-run) no writes")
        for b in built[:2]:
            print(json.dumps({k: b[k] for k in ("title", "skill_level", "labor_minutes")}, indent=1))
            print(f"    steps: {len(b['steps'])}")
        return

    if not built:
        print("Nothing to insert.")
        return

    vals = []
    for b in built:
        steps_j = json.dumps(b["steps"]).replace("'", "''")
        parts_j = json.dumps(b["parts"]).replace("'", "''")
        tools_arr = "ARRAY[" + ",".join(f"'{esc(t)}'" for t in b["tools_required"]) + "]"
        vals.append(
            f"('{b['failure_mode_id']}','{esc(b['title'])}','{b['skill_level']}',"
            f"{b['labor_minutes']},{tools_arr},'{parts_j}'::jsonb,'{steps_j}'::jsonb,"
            f"'engineering-estimate',1)"
        )

    # Batch to keep each statement well under any request-size limit.
    BATCH = 25
    for i in range(0, len(vals), BATCH):
        chunk = vals[i:i + BATCH]
        run("INSERT INTO repair_protocols "
            "(failure_mode_id, title, skill_level, labor_minutes, tools_required, "
            "parts_json, steps_json, source_url, version) "
            f"VALUES {','.join(chunk)} ON CONFLICT DO NOTHING;")
        print(f"  inserted batch {i // BATCH + 1} ({len(chunk)} rows)")

    tot = q("SELECT count(*) AS n FROM repair_protocols;")
    print(f"  repair_protocols total: {tot[0]['n'] if tot else '?'}")
    gap = q(GAP_SQL)
    print(f"  remaining FM gap: {len(gap)}")


if __name__ == "__main__":
    main()
