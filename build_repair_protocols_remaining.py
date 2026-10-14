#!/usr/bin/env python3
"""Add repair_protocols for the 7 remaining CRITICAL failure modes.

These operationalize each FM's documented mitigation (in root_cause) into a
real procedure. Parts are generic/field-standard; source = engineering-estimate.
Idempotent: skips FM IDs that already have a protocol.
Usage: python3 build_repair_protocols_remaining.py [--dry-run]
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
    # moon-surgical-maestro — arm actuator drift during retraction
    ("fde64598-4dd0-41fa-ba13-b52fdbe0e527",
     "Maestro Assistive Arm — Drift Calibration & Brake-On-Idle Verification",
     "specialist", 75,
     ["Encoder calibration tool", "Force-torque sensor", "Torque driver set",
      "Brake test rig", "Debug/PC interface"],
     [{"part_name": "Encoder replacement kit (per actuator)", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None},
      {"part_name": "Force-limit clamp retrofit kit", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Quiet the OR: confirm no patient present; lock arm in home position; detach instrument.",
       "tool": "Debug/PC interface", "warning": "Arm under power can move — ensure physical restraint before calibration."},
      {"step": 2, "action": "Run encoder calibration routine via manufacturer tool; record zero-position offsets per joint.",
       "tool": "Encoder calibration tool", "warning": "Do not skip zero-position reference — drift resumes from wrong baseline."},
      {"step": 3, "action": "Verify brake-on-idle: command zero torque, confirm arm holds position for 60 s with <2 mm drift.",
       "tool": "Brake test rig", "warning": "Brake failure = immediate return-to-shop; do not put back in service."},
      {"step": 4, "action": "Set force-limit clamp to surgical-tissue threshold; confirm arm stops on over-force within 100 ms.",
       "tool": "Force-torque sensor", "warning": "Too-sensitive clamp causes nuisance stops; too-loose = tissue risk — tune with phantom tissue."},
      {"step": 5, "action": "Log calibration date + drift reading; schedule next joint service at the prescribed interval.",
       "tool": None, "warning": "Drift recurring before service interval = root cause not addressed; escalate."},
     ]),

    # rob-surgical-bitrack — needle driver misalignment
    ("9ff966b9-5a67-4b0c-ad0e-fb0d3c3ea679",
     "BiTrack Needle Driver — Guide Calibration & Jaw Inspection",
     "specialist", 60,
     ["Needle-guide calibration fixture", "VisionRegistration tool", "Driver-jaw replacement kit",
      "Torque driver set", "Sterile field kit"],
     [{"part_name": "Needle-driver jaw insert (wear-rated)", "part_number": None, "qty": 2,
       "supplier": "generic/field-standard", "unit_cost_usd": None},
      {"part_name": "Needle-guide calibration reference needle", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Set up calibration fixture on sterile field; load reference needle; confirm fixture is level.",
       "tool": "Needle-guide calibration fixture", "warning": "Calibration off-level = residual error stays in the guide."},
      {"step": 2, "action": "Run needle-guide calibration: drive reference needle through full range; record deviation at each pose.",
       "tool": "VisionRegistration tool", "warning": "Deviation >1 mm at any pose = adjust or replace jaw before next case."},
      {"step": 3, "action": "Inspect driver jaws for wear, burr, or debris; replace jaw inserts if wear exceeds spec.",
       "tool": "Driver-jaw replacement kit", "warning": "Worn jaw = needle deflection source — do not reuse worn inserts."},
      {"step": 4, "action": "Perform pre-op alignment check on the actual procedure needle; confirm placement within tolerance on phantom.",
       "tool": "Torque driver set", "warning": "Never skip pre-op check on a new needle lot or after jaw service."},
      {"step": 5, "action": "Document calibration values + jaw replacement date; set next inspection in the maintenance calendar.",
       "tool": None, "warning": "Per-case needle deflection event = re-run full calibration before next case."},
     ]),

    # torin-surgical — prototype actuator failure
    ("af8d370b-0927-4db0-8a65-7baf0cfd7a4e",
     "Torin Prototype Actuator — Health Monitoring & Fail-Safe Braking Validation",
     "specialist", 90,
     ["Actuator health monitor / diagnostic PC", "Torque/position reference rig",
      "Fail-safe brake test fixture", "Thermal camera", "Torque driver set"],
     [{"part_name": "Redundant actuation module (prototype-grade)", "part_number": None, "qty": 1,
       "supplier": "internal/research", "unit_cost_usd": None},
      {"part_name": "Fail-safe braking retrofit kit", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Mount actuator on reference rig; confirm mechanical restraint before any power applied.",
       "tool": "Torque/position reference rig", "warning": "Prototype actuator can produce unexpected motion — restraint mandatory."},
      {"step": 2, "action": "Connect health monitor; log baseline torque, position error, temperature, and current draw over a full cycle.",
       "tool": "Actuator health monitor / diagnostic PC", "warning": "Store baseline — any future deviation is the first failure signal."},
      {"step": 3, "action": "Exercise fail-safe brake: cut power abruptly at mid-stroke; confirm arm holds within 5 mm with no creep.",
       "tool": "Fail-safe brake test fixture", "warning": "Brake that fails to hold = do not return to service; prototype risk is unacceptable."},
      {"step": 4, "action": "Verify graceful degradation: disable primary actuation path; confirm redundant path takes over within commanded tolerance.",
       "tool": "Actuator health monitor / diagnostic PC", "warning": "Redundant path must be tested independently, not just assumed."},
      {"step": 5, "action": "Run thermal imaging under peak load; flag any hot-spot >allowed delta-T for teardown.",
       "tool": "Thermal camera", "warning": "Overheating prototype actuator = immediate quarantine for engineering review."},
      {"step": 6, "action": "Record health baseline + brake test result; tag actuator with validation stamp and next-check interval.",
       "tool": None, "warning": "Prototype hardware has no certified MTBF — treat every validation as time-limited."},
     ]),

    # unitree-h2 — battery thermal runaway risk
    ("91bf77d1-a9ca-4c63-b65a-5ca05270cae1",
     "Unitree H2 Battery Pack — Thermal Monitoring, Cell Balancing & BMS Threshold Tune",
     "advanced", 80,
     ["Thermal camera / IR gun", "Cell-balancer access", "BMS config tool",
      "Insulated multimeter", "Fire-safe test enclosure"],
     [{"part_name": "Battery pack replacement unit (per spec)", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None},
      {"part_name": "Thermal blanket / fire suppression pouch", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Move pack to fire-safe enclosure; confirm no flammable material within 1 m; post thermal-runaway signage.",
       "tool": "Fire-safe test enclosure", "warning": "Never charge or discharge a suspect pack unattended."},
      {"step": 2, "action": "Connect BMS config tool; read per-cell voltages and temperatures; confirm all cells within 0.02 V and <35 C before load.",
       "tool": "BMS config tool, insulated multimeter", "warning": "Cell delta >0.05 V or any cell >35 C = do not charge; investigate first."},
      {"step": 3, "action": "Run a full cell-balancing pass; verify SoC spread <0.02 V and per-cell temperature within 3 C of ambient afterward.",
       "tool": "Cell-balancer access", "warning": "Unbalanced pack = thermal hotspot risk — balance before any load test."},
      {"step": 4, "action": "Tune BMS thresholds: set overtemperature lockout with graceful shutdown margin above observed thermal floor.",
       "tool": "BMS config tool", "warning": "Threshold too tight = nuisance shutdowns; too loose = runaway risk — tune with thermal monitoring live."},
      {"step": 5, "action": "Run a staged charge/discharge under IR monitoring; abort if any cell delta >0.05 V or temp >allowed limit.",
       "tool": "Thermal camera / IR gun", "warning": "Any swelling, venting, or >limit temp = immediate quarantine."},
      {"step": 6, "action": "Tag pack with validation date, balance state, and BMS threshold set; schedule next thermal check.",
       "tool": None, "warning": "Pack showing any irregularity = replace, do not re-tune indefinitely."},
     ]),

    # unitree-h2 — hip actuator overload
    ("dd9d8565-cd36-4f22-92ad-2ab69a68a505",
     "Unitree H2 Hip Actuator — Torque-Limit Tuning & Gait Derating Validation",
     "advanced", 70,
     ["Torque/position reference rig", "Gait controller config access",
      "Thermal camera", "IMU diagnostic tool", "Torque driver set"],
     [{"part_name": "Hip actuator replacement unit (per spec)", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Mount hip actuator on reference rig; confirm mechanical restraint; zero the position reference.",
       "tool": "Torque/position reference rig", "warning": "High-torque hip actuator can break free — restraint mandatory."},
      {"step": 2, "action": "Measure torque ripple and peak torque under commanded gait range; identify the saturation point.",
       "tool": "Torque/position reference rig", "warning": "Saturation without detection = uncontrolled motion — tune limits before field use."},
      {"step": 3, "action": "Tune torque-limit in gait controller: set ceiling below the observed saturation point with a safety margin.",
       "tool": "Gait controller config access", "warning": "Limit too conservative = degraded gait; too loose = thermal shutdown risk — validate on rig first."},
      {"step": 4, "action": "Derate gait speed/payload for the high-torque regime; verify no thermal shutdown over a sustained walk cycle.",
       "tool": "Gait controller config access, thermal camera", "warning": "Thermal shutdown during a walk = fall hazard — derate until stable."},
      {"step": 5, "action": "Verify hip cooling path: confirm coolant flow / passive cooling is unobstructed and within spec.",
       "tool": "Thermal camera", "warning": "Blocked cooling = rapid thermal buildup — inspect before every high-torque session."},
      {"step": 6, "action": "Run payload verification: load to spec, walk full cycle, confirm no torque saturation or thermal alarm.",
       "tool": "Torque driver set", "warning": "Payload above spec = actuations outside validated envelope — do not field."},
      {"step": 7, "action": "Log torque-limit setpoint, derate config, and thermal result; tag actuator with validation stamp.",
       "tool": None, "warning": "Any saturation event in the field = return to shop for re-tune before next deployment."},
     ]),

    # unitree-h2 — balance controller instability
    ("05e44a3f-0428-4788-9d5d-334b582592d5",
     "Unitree H2 Balance Controller — IMU Recalibration, Gain Tuning & Emergency Sit Validation",
     "advanced", 85,
     ["IMU calibration tool", "Motion capture / reference tracking",
      "Balance controller config access", "Force-plate or foot-force sensor",
      "Emergency-stop test rig", "Torque driver set"],
     [{"part_name": "IMU replacement unit (per spec)", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Mount robot in a safe test rig; confirm emergency-stop is reachable and tested before any balance work.",
       "tool": "Emergency-stop test rig", "warning": "Balance testing without a reachable E-stop = unacceptable risk."},
      {"step": 2, "action": "Recalibrate IMU: run full bias/alignment routine; confirm gyro bias and accel within spec after calibration.",
       "tool": "IMU calibration tool", "warning": "Drifted IMU = balance controller flying blind — recalibrate before any standing test."},
      {"step": 3, "action": "Tune balance gains in the controller: start low, step up while monitoring oscillation; lock gains that are stable without overshoot.",
       "tool": "Balance controller config access", "warning": "Gain too high = oscillation and fall; too low = no correction — tune incrementally with spotter."},
      {"step": 4, "action": "Verify foot-force feedback loop: command a perturbation, confirm the robot responds with corrective step within spec.",
       "tool": "Force-plate or foot-force sensor", "warning": "No corrective response to perturbation = balance loop not closed — do not go autonomous."},
      {"step": 5, "action": "Validate emergency sit: trigger E-stop during standing gait; confirm robot sits safely without toppling.",
       "tool": "Emergency-stop test rig", "warning": "E-stop that causes a fall = redesign the fall strategy before any human-proximity use."},
      {"step": 6, "action": "Run a sustained standing/walk cycle under motion capture; confirm oscillation stays within allowed envelope.",
       "tool": "Motion capture / reference tracking", "warning": "Any drift or oscillation growth over time = gain or IMU issue — stop and investigate."},
      {"step": 7, "action": "Log IMU calibration values, gain setpoint, and emergency-sit result; schedule next IMU check.",
       "tool": None, "warning": "Reoccurring oscillation after tuning = root cause (IMU, mechanical, or control) not resolved."},
     ]),

    # virtual-incision-mira — miniaturized instrument tip slip
    ("5f71d8aa-539f-4130-ae05-15c323037a05",
     "MIRA Miniaturized Instrument Tip — Surface Coating, Grip-Force Feedback & Replacement Schedule",
     "specialist", 65,
     ["Grip-force calibration tool", "Tip surface inspection microscope",
      "Instrument replacement kit (sterile)", "Torque driver set (miniature)",
      "Phantom tissue test rig"],
     [{"part_name": "Instrument tip replacement unit (sterile, per lot)", "part_number": None, "qty": 2,
       "supplier": "generic/field-standard", "unit_cost_usd": None},
      {"part_name": "Tip surface coating application kit", "part_number": None, "qty": 1,
       "supplier": "generic/field-standard", "unit_cost_usd": None}],
     [
      {"step": 1, "action": "Inspect instrument tip under microscope for coating wear, micro-cracks, or surface degradation.",
       "tool": "Tip surface inspection microscope", "warning": "Worn coating = slip risk — replace, do not re-coat a compromised tip in the field."},
      {"step": 2, "action": "Apply / verify tip surface coating per manufacturer spec; confirm uniform coverage and cure before use.",
       "tool": "Tip surface coating application kit", "warning": "Incomplete coating = uneven friction — reject and re-coat."},
      {"step": 3, "action": "Calibrate grip-force feedback: command a grip torque, confirm sensor reads within tolerance on phantom tissue.",
       "tool": "Grip-force calibration tool", "warning": "Grip-force reading offset = either drop or crush — calibrate before every case."},
      {"step": 4, "action": "Run instrument replacement schedule check: confirm tip is within its validated cycle count / usage window.",
       "tool": "Instrument replacement kit (sterile)", "warning": "Over-cycled miniaturized tip = material fatigue — replace on schedule, not on failure."},
      {"step": 5, "action": "Perform surgeon-override drill: confirm the surgeon can take manual control within the allowed latency when grip feedback flags.",
       "tool": "Phantom tissue test rig", "warning": "Override latency too high = tissue damage window — validate on phantom before live patient."},
      {"step": 6, "action": "Log tip cycle count, coating state, and grip-force calibration; set next replacement in the sterile-instruments calendar.",
       "tool": None, "warning": "Any slip event in a case = pull the instrument lot and inspect all tips from that batch."},
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

print(f" Inserting {len(rows)} repair protocols...")
if rows and not DRY:
    vals = ",".join(rows)
    run("INSERT INTO repair_protocols "
        "(failure_mode_id, title, skill_level, labor_minutes, tools_required, parts_json, steps_json, source_url, version) "
        f"VALUES {vals} ON CONFLICT DO NOTHING;")
    after = q("SELECT count(*) AS n FROM repair_protocols rp WHERE rp.failure_mode_id IN "
              f"('{','.join(f[0] for f in P)}');")
    print(" Critical-with-protocol now:", after[0]['n'] if after else '?', "of 7 targeted")
    # verify gap is closed
    gap = q("""SELECT count(*) AS n FROM failure_modes fm
               WHERE fm.severity='critical'
               AND NOT EXISTS (SELECT 1 FROM repair_protocols rp WHERE rp.failure_mode_id=fm.id);""")
    print(" Remaining critical gap:", gap[0]['n'] if gap else '?')
else:
    print("(dry-run) would insert", len(rows))
