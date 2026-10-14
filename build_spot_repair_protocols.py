#!/usr/bin/env python3
"""
Author repair_protocols for Boston Dynamics Spot's 6 failure modes.
Spot has 0 repair protocols currently — all 6 FMs lack one.
Each protocol operationalizes the FM's documented mitigation into a real procedure.
Parts are generic/field-standard; source = engineering-estimate.
Idempotent: skips FM IDs that already have a protocol.
Usage: python3 build_spot_repair_protocols.py [--dry-run]
"""
import json, subprocess, sys, os, re

DRY = '--dry-run' in sys.argv
HOME = os.path.expanduser("~")

def q(sql):
    out = subprocess.run(["supabase", "db", "query", "--linked", sql],
                         capture_output=True, text=True, cwd=HOME)
    raw = out.stdout
    s = raw.find("{")
    if s == -1:
        return []
    try:
        return json.loads(raw[s:]).get("rows", [])
    except Exception:
        m = re.search(r'"rows"\s*:\s*(\[.*\])\s*}', raw, re.S)
        return json.loads(m.group(1)) if m else []

def run(sql):
    r = subprocess.run(["supabase", "db", "query", "--linked", sql],
                       capture_output=True, text=True, cwd=HOME)
    if r.returncode != 0:
        raise RuntimeError(f"SQL failed: {(r.stderr or r.stdout)[:400]}")
    return r.stdout

# (fm_id, title, skill, labor_min, tools[], parts[], steps[])
P = [
    # Wireless comms module — control latency / safe-stand
    ("361fdf1e-80be-4cc5-a501-f6e73e7a6dc1",
     "Spot Wireless Comms Module — RF Survey, Mesh/LTE Config & Comms-Loss Behavior Validation",
     "intermediate", 55,
     ["RF spectrum analyzer / Wi-Fi scanner", "LTE/modem config tool", "Mesh radio config tool",
      "Test tablet (Spot control UI)", "Tripod / mounting hardware"],
     [{"part_name": "Mesh/LTE payload radio (per mission profile)", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Power down Spot; confirm zero-energy state before opening any comms bay.",
       "tool": None, "warning": "Live comms bay = RF exposure + electrical risk — verify powered off."},
      {"step": 2, "action": "Survey the RF environment at the deployment site: scan for congested 2.4/5 GHz channels and LTE signal strength; record baseline.",
       "tool": "RF spectrum analyzer / Wi-Fi scanner", "warning": "Do not deploy into an RF environment you have not surveyed — comms loss risk is site-specific."},
      {"step": 3, "action": "Configure comms-loss behavior per mission profile: choose safe-sit vs. return-to-home per site risk; verify the chosen behavior in test before field use.",
       "tool": "Mesh radio config tool, LTE/modem config tool", "warning": "Comms-loss behavior must be pre-set per site — do not rely on default in an unfamiliar deployment."},
      {"step": 4, "action": "If the site RF environment is congested or weak, install a mesh/LTE payload radio with a clear antenna placement; re-survey after install to confirm improvement.",
       "tool": "Mesh/LTE payload radio (per mission profile)", "warning": "Antenna placement matters — obstructed or body-shadowed antenna negates the upgrade."},
      {"step": 5, "action": "Pre-survey the RF environment for each new site and record it in the mission profile; set comms-loss behavior before the robot engages autonomy.",
       "tool": "Test tablet (Spot control UI)", "warning": "Skipping the RF pre-survey = accepting uncharacterized comms-loss risk."},
      {"step": 6, "action": "Log RF survey result, comms-loss config, and any payload radio installed; schedule re-survey if the site RF environment changes.",
       "tool": None, "warning": "Site changes (new equipment, construction) can change RF — re-survey, do not assume."},
     ]),

    # Perception cameras — low light / glare / obstacle avoidance
    ("36e72b8c-47a0-496e-a385-e0639695c8d7",
     "Spot Perception Cameras — Lens Cleaning, Low-Light Validation & Lidar Fallback Check",
     "intermediate", 40,
     ["Lens cleaning kit (microfiber + validated cleaner)", "Lidar payload (if adding fallback)",
      "Test course (stairs / dark corner / glare source)", "Calibration phantom / fiducial set"],
     [{"part_name": "Lidar payload (optional fallback for dark environments)", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None},
      {"part_name": "Lens cover / protective hood (per site)", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Inspect both stereo cameras and the wrist camera for dust, smudges, condensation, or physical damage; clean with validated lens cleaner and microfiber.",
       "tool": "Lens cleaning kit (microfiber + validated cleaner)", "warning": "Do not use solvents not approved for the lens coating — damage is irreversible."},
      {"step": 2, "action": "Run a low-light / glare validation: navigate the test course in the worst expected lighting; confirm obstacle avoidance and stair traversal succeed.",
       "tool": "Test course (stairs / dark corner / glare source)", "warning": "If the robot refuses stairs or misjudges obstacles in low light, do not deploy in that lighting without a lidar fallback."},
      {"step": 3, "action": "If low-light performance is insufficient, add a lidar payload and confirm the robot uses it for perception in dark environments (via pre-mapped Autowalk with fiducials).",
       "tool": "Lidar payload (optional fallback for dark environments)", "warning": "Adding lidar without re-mapping / re-fiducialing the site does not fix the gap — update the mission map."},
      {"step": 4, "action": "Install lens covers / protective hoods if the site has abrasive dust, spray, or glare sources; confirm they do not obstruct the field of view.",
       "tool": "Lens cover / protective hood (per site)", "warning": "A cover that obstructs FOV is worse than no cover — verify unobstructed view after install."},
      {"step": 5, "action": "Schedule lens inspection and cleaning per deployment frequency; log any lens damage or recurring glare issues.",
       "tool": None, "warning": "Dirty lenses are the most common perception failure — inspect before every deployment in dirty/wet conditions."},
     ]),

    # 605 Wh swappable battery — capacity fade
    ("ee7312aa-69a3-4d4d-b49d-711745aa7f13",
     "Spot 605 Wh Swappable Battery — Capacity Check, Rotation & Retirement Protocol",
     "intermediate", 35,
     ["Battery diagnostic / capacity-test tool", "Balance charger (per fleet)", "SOC meter / BMS reader",
      "Labeling / tagging supplies", "Fire-safe storage container (per fleet policy)"],
     [{"part_name": "Replacement 605 Wh swappable battery pack", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None},
      {"part_name": "Battery retirement / quarantine label", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Pull the battery from the robot; confirm it is at a safe SOC before handling (do not handle a fully charged pack for a capacity test).",
       "tool": "SOC meter / BMS reader", "warning": "High SOC pack = thermal/runaway risk in a fault — discharge to a safe handling SOC first."},
      {"step": 2, "action": "Run a capacity test (full discharge at rated load) and compare to the nominal 605 Wh; flag any pack below 80% of nominal capacity for retirement.",
       "tool": "Battery diagnostic / capacity-test tool", "warning": "A pack below 80% capacity will cause unexpected low-battery sit-downs mid-mission — retire, do not keep in rotation."},
      {"step": 3, "action": "If the pack passes, rotate it into the fleet with a balanced-charger cycle; store at ~50% SOC if not in immediate use.",
       "tool": "Balance charger (per fleet)", "warning": "Storing a lithium pack at full or empty SOC for extended periods accelerates degradation — store at ~50% SOC."},
      {"step": 4, "action": "If the pack fails the 80% threshold, label it for retirement, move it to fire-safe storage, and remove it from the active rotation.",
       "tool": "Battery retirement / quarantine label", "warning": "A retired pack must not be reinstalled — physical segregation from the active pool is required."},
      {"step": 5, "action": "Use dock-based self-charging where available; rotate battery packs to spread cycles across the fleet rather than over-using a single pack.",
       "tool": None, "warning": "Overusing one pack concentrates cycles and shortens fleet battery life — rotate."},
      {"step": 6, "action": "Log capacity-test result, SOC at storage, retirement date (if applicable), and next-check interval; track per-pack cycle count where the BMS exposes it.",
       "tool": None, "warning": "A pack that fails capacity test and is reinstalled = surprise low-battery failure in the field — log and segregate."},
     ]),

    # Rubber foot contact pads — delamination / slip
    ("95fe0225-ca8c-4a9d-a1b2-15460618a9ec",
     "Spot Rubber Foot Contact Pads — Inspection, Replacement & Traction Check",
     "basic", 20,
     ["Foot-pad replacement kit (per Spot generation)", "Torque driver (small)", "Visual inspection light",
      "Traction test surface (smooth floor + abrasive surface)"],
     [{"part_name": "Rubber foot contact pad (per Spot generation, qty 4)", "part_number": None, "qty": 4,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Inspect all four foot pads for delamination, cracks, thinning, or embedded debris; retire and replace any pad that is visibly worn or delaminating.",
       "tool": "Visual inspection light", "warning": "A delaminating pad can detach mid-walk — replace on inspection, not on failure."},
      {"step": 2, "action": "Replace worn pads with the correct kit for the Spot generation; confirm the pad seats fully and the retention is positive.",
       "tool": "Foot-pad replacement kit (per Spot generation)", "warning": "Wrong-generation pad = poor retention or fit — verify the kit matches the Spot variant."},
      {"step": 3, "action": "Torque any retaining hardware to spec after replacement; confirm no play or wobble in the replaced pad.",
       "tool": "Torque driver (small)", "warning": "Loose pad hardware = rattle and eventual loss — torque to spec."},
      {"step": 4, "action": "Run a traction check on the smooth floor and an abrasive surface; confirm the robot does not slip or degrade gait on either surface.",
       "tool": "Traction test surface (smooth floor + abrasive surface)", "warning": "Slipping on smooth floors after pad work = the pads are not seated or are the wrong type."},
      {"step": 5, "action": "Avoid deploying on abrasive hot surfaces (e.g. hot concrete in sun) without checking pad temperature and wear; schedule pad replacement per inspection interval.",
       "tool": None, "warning": "Hot abrasive surfaces accelerate pad wear — inspect before and after such deployments."},
     ]),

    # Leg hip actuator — gearbox wear
    ("3ede0d08-9e21-4f0f-8c33-8bba46829ac7",
     "Spot Hip Actuator — Per-Joint Telemetry Review, Wear-Threshold Swap & Duty-Cycle Management",
     "advanced", 70,
     ["Joint torque/current telemetry tool (Spot diagnostics)", "Thermal camera / IR gun",
      "Actuator replacement kit (per Spot generation, hip)", "Torque driver set (leg)",
      "Gait analysis / asymmetry check tool"],
     [{"part_name": "Hip actuator replacement unit (per Spot generation)", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Pull per-joint current and temperature telemetry for the affected hip actuator over the recent mission history; identify elevated current or temperature trends.",
       "tool": "Joint torque/current telemetry tool (Spot diagnostics)", "warning": "Actuator wear shows up as rising current at a given load — trend it, do not judge on a single reading."},
      {"step": 2, "action": "Run a gait asymmetry check: compare the affected leg's kinematics and current draw against the opposite leg under a standard load; quantify any asymmetry.",
       "tool": "Gait analysis / asymmetry check tool", "warning": "Unquantified asymmetry = you cannot set a swap threshold — measure it."},
      {"step": 3, "action": "If current/temperature trend or asymmetry exceeds the wear threshold, schedule the hip actuator swap; avoid sustained max-payload stair climbs in the interim.",
       "tool": "Actuator replacement kit (per Spot generation, hip)", "warning": "Sustained max-payload stair climbs on a worn hip actuator accelerate failure — derate until swapped."},
      {"step": 4, "action": "Swap the hip actuator using the correct kit for the Spot generation; torque all leg fasteners to spec; confirm no play or binding.",
       "tool": "Torque driver set (leg)", "warning": "Leg fasteners at wrong torque = wobble or loosening — torque to spec after any actuator work."},
      {"step": 5, "action": "After swap, re-run the gait asymmetry check to confirm symmetry is restored; confirm no elevated current on the replaced leg under standard load.",
       "tool": "Gait analysis / asymmetry check tool", "warning": "A replaced actuator that still shows asymmetry = the root cause may be elsewhere — re-check before declaring done."},
      {"step": 6, "action": "Log the telemetry trend, swap date, and next telemetry review interval; track per-actuator cycle/load history where Spot diagnostics expose it.",
       "tool": None, "warning": "A hip actuator that failed once and is not trended = repeat failure risk — log and review."},
     ]),

    # Lower-leg (knee) actuator — thermal shutdown
    ("4f8c95aa-7781-4e4b-b439-e7437c8480a8",
     "Spot Knee Actuator — Thermal Telemetry, Duty-Cycle Derating & Cool-Down Validation",
     "advanced", 65,
     ["Joint thermal telemetry tool (Spot diagnostics)", "Thermal camera / IR gun",
      "Knee actuator replacement kit (per Spot generation)", "Torque driver set (leg)",
      "Incline/stair test course (loaded)"],
     [{"part_name": "Knee actuator replacement unit (per Spot generation)", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Pull thermal telemetry for the knee actuator across recent missions; identify repeated thermal trips or rising temperature under load.",
       "tool": "Joint thermal telemetry tool (Spot diagnostics)", "warning": "A knee actuator that thermal-shuts its leg under load = fall/compliance risk — treat as safety-relevant."},
      {"step": 2, "action": "Limit continuous incline/stair duty cycles at high payload until the root cause is addressed; monitor thermal telemetry during any loaded incline/stair work.",
       "tool": None, "warning": "Pushing a thermally-shutting knee actuator through repeated stair climbs = repeated shutdowns and fall risk — derate first."},
      {"step": 3, "action": "If the actuator is thermally-shutting repeatedly, schedule the knee actuator swap using the correct kit; allow a full cool-down between missions in the interim.",
       "tool": "Knee actuator replacement kit (per Spot generation)", "warning": "A knee actuator that has thermal-tripped should not be returned to full duty without replacement or engineering review."},
      {"step": 4, "action": "Swap the knee actuator; torque all leg fasteners to spec; confirm the new actuator seats and there is no binding or play.",
       "tool": "Torque driver set (leg)", "warning": "Leg fasteners at wrong torque after actuator swap = wobble or loosening — torque to spec."},
      {"step": 5, "action": "Run a loaded incline/stair test on the replacement actuator; confirm no thermal trip over a sustained cycle at the expected mission load; thermal-camera the actuator afterward.",
       "tool": "Incline/stair test course (loaded)", "warning": "A replacement actuator that thermal-trips on the first loaded stair test = the load or cooling is not right — investigate before field."},
      {"step": 6, "action": "Log thermal telemetry trend, replacement date, cool-down practice, and next thermal review interval; track per-actuator thermal history where Spot diagnostics expose it.",
       "tool": None, "warning": "A knee actuator replaced once and not trended = repeat risk — log thermal history."},
     ]),
]

def clean_steps(steps):
    out = []
    for s in steps:
        d = {}
        for k, v in s.items():
            if k is None:
                continue
            d[k] = v
        out.append(d)
    return out

existing = {r["failure_mode_id"] for r in q("SELECT failure_mode_id FROM repair_protocols;")}
rows = []
for fm_id, title, skill, labor, tools, parts, steps in P:
    if fm_id in existing:
        print(f"skip {fm_id[:8]} (already has protocol)")
        continue
    steps = clean_steps(steps)
    steps_j = json.dumps(steps).replace("'", "''")
    tools_arr = "ARRAY[" + ",".join(f"'{t.replace(chr(39), chr(39)+chr(39))}'" for t in tools) + "]"
    parts_j = json.dumps(parts).replace("'", "''")
    rows.append(
        f"('{fm_id}','{title.replace(chr(39), chr(39)+chr(39))}','{skill}',{labor},"
        f"{tools_arr},'{parts_j}'::jsonb,'{steps_j}'::jsonb,"
        f"'engineering-estimate',1)"
    )

print(f"Inserting {len(rows)} Spot repair protocols...")
if rows and not DRY:
    vals = ",".join(rows)
    run("INSERT INTO repair_protocols "
        "(failure_mode_id, title, skill_level, labor_minutes, tools_required, parts_json, steps_json, source_url, version) "
        f"VALUES {vals} ON CONFLICT DO NOTHING;")
    after = q("SELECT count(*) AS n FROM repair_protocols rp WHERE rp.failure_mode_id IN "
              f"('{','.join(f[0] for f in P)}');")
    print(f"Spot protocols now: {after[0]['n'] if after else '?'} of {len(P)} targeted")
    gap = q("""SELECT count(*) AS n FROM failure_modes fm
               JOIN platforms p ON p.id = fm.platform_id
               WHERE p.slug='boston_dynamics_spot'
               AND NOT EXISTS (SELECT 1 FROM repair_protocols rp WHERE rp.failure_mode_id=fm.id);""")
    print(f"Spot remaining gap: {gap[0]['n'] if gap else '?'}")
else:
    print(f"(dry-run) would insert {len(rows)}")
