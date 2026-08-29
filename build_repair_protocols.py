#!/usr/bin/env python3
"""Author repair_protocols for the 11 CRITICAL failure modes lacking one.

Each protocol operationalizes the failure mode's documented mitigation into a
real procedure (steps_json), tools, labor, and skill level. Parts are kept to
generic field-standard consumables (no fabricated manufacturer SKUs). Source is
marked as engineering-estimate, consistent with existing rows.

Idempotent: skips (failure_mode_id) pairs that already have a protocol.
Usage: python3 build_repair_protocols.py [--dry-run]
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

# (fm_id, title, skill, labor, tools, parts, steps)
P = [
 ("f30a2762-464c-4dff-b7bc-32caee787f8d",
  "Prototype 1200 Wh Battery — Thermal-Runaway Containment & Validation",
  "specialist", 120,
  ["Fire-safe charging enclosure", "Thermal camera / IR gun", "Torque driver set",
   "Insulated multimeter", "Battery management system (BMS) config tool"],
  [{"part_name":"Fire-safe charge/test enclosure (metal, vented)","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None},
   {"part_name":"Thermal blanket / fire suppression pouch","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None}],
  [
   {"step":1,"action":"Move pack to fire-safe enclosure; confirm no flammable material within 1 m; post thermal-runaway signage.","tool":"Fire-safe charging enclosure","warning":"NEVER charge unattended — prototype pack has no certified protection."},
   {"step":2,"action":"Connect BMS config tool; read cell voltages and temperatures; confirm all cells within 0.02 V and <35 C before any load.","tool":"BMS config tool, insulated multimeter","warning":"Capacitor/discharge risk — insulated tools only."},
   {"step":3,"action":"Apply conservative BMS limits: max charge current <=0.5C, discharge cutoff at 20% SoC, overtemperature lockout at 45 C.","tool":"BMS config tool",None:"warning"},
   {"step":4,"action":"Run a staged charge/discharge cycle under IR monitoring; abort if any cell delta >0.05 V or temp >45 C.","tool":"Thermal camera / IR gun",None:"warning"},
   {"step":5,"action":"Tag pack with validation date and limits; quarantine any pack showing swelling or >45 C excursion for teardown.","tool":None,"warning":"Swollen pack = immediate quarantine, do not continue."},
  ]),

 ("288855da-06a5-4256-a4ba-447bcb2a8c8c",
  "Prototype Actuator Controller — Firmware Fault Freeze & CAN Log Capture",
  "specialist", 90,
  ["Tether / test stand", "CAN analyzer (e.g. CANable, PCAN)", "Firmware version pinning tool",
   "Torque driver set", "Insulated multimeter"],
  [{"part_name":"Firmware release tag (per campaign)","part_number":None,"qty":1,"supplier":"internal","unit_cost_usd":None}],
  [
   {"step":1,"action":"Mount actuator on stand/tether; confirm mechanical restraint before power.","tool":"Tether / test stand","warning":"Random torque spikes — physical restraint mandatory."},
   {"step":2,"action":"Freeze firmware version for the test campaign; record commit hash in the test log.","tool":"Firmware version pinning tool",None:"warning"},
   {"step":3,"action":"Start continuous CAN traffic logging at full bus rate before energizing.","tool":"CAN analyzer",None:"warning"},
   {"step":4,"action":"Energize and exercise joint through planned range; capture every watchdog reset / torque spike with timestamp.","tool":"CAN analyzer",None:"warning"},
   {"step":5,"action":"On anomaly, dump CAN log + BMS snapshot to the failure record; do not re-run until root cause triaged.","tool":None,"warning":"Do not 'retry and hope' — log first."},
  ]),

 ("ce777a5a-5e79-47fd-89c0-792c80fd0f27",
  "Agra T50 Downward Obstacle-Radar — Wire/Branch Blind-Spot Mitigation",
  "intermediate", 45,
  ["Pre-flight survey tablet", "Operator spotter", "Mission planner access"],
  [],
  [
   {"step":1,"action":"Before autonomous mapping, manually survey the field for power/fence lines and tall poles; mark them on the mission map.","tool":"Pre-flight survey tablet",None:"warning"},
   {"step":2,"action":"Fuse radar + vision layers in the autonomy config; disable pure-radar avoidance.","tool":"Mission planner access",None:"warning"},
   {"step":3,"action":"Set transit speed to 'slow' within 10 m of any known line; require operator spotter in that zone.","tool":"Operator spotter",None:"warning"},
   {"step":4,"action":"Post-flight: review avoidance log; any 'no trigger near line' event = radar recalibration required.","tool":None,None:"warning"},
  ]),

 ("46310102-a0d0-413f-b163-e892935bddeb",
  "Lime Gen4 Steering Stem & Folding Latch — Torque-Check & Lock Verification",
  "intermediate", 30,
  ["Torque wrench (0-25 Nm)", "Latch-pin gauge", "Frame crack-inspection light", "Replacement latch pins"],
  [{"part_name":"Folding-latch retaining pin (fatigue-rated)","part_number":None,"qty":2,"supplier":"generic/field-standard","unit_cost_usd":None},
   {"part_name":"Structural thread-locker (medium strength)","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None}],
  [
   {"step":1,"action":"Inspect frame at hinge and stem for cracks; retire any cracked frame immediately.","tool":"Frame crack-inspection light","warning":"Cracked frame = retire, do not repair."},
   {"step":2,"action":"Torque-check all folding bolts to spec with thread-locker; re-mark to verify no loosening.","tool":"Torque wrench (0-25 Nm)",None:"warning"},
   {"step":3,"action":"Replace fatigued latch pins; verify latch engages with positive click and holds rider weight in test.","tool":"Latch-pin gauge",None:"warning"},
   {"step":4,"action":"Confirm handlebars aligned and stem free of wobble before return to service.","tool":None,None:"warning"},
  ]),

 ("0b0b3b33-54dc-47c2-b198-89029293bfbb",
  "Rad Commercial Controller Enclosure — Water-Ingress Seal & Corrosion Repair",
  "intermediate", 60,
  ["Socket set", "Dielectric grease", "Gasket pick", "Multimeter", "Heat gun / isopropyl"],
  [{"part_name":"IP65 enclosure gasket set","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None},
   {"part_name":"Dielectric connector grease","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None}],
  [
   {"step":1,"action":"Power down and confirm zero-energy state at the enclosure; note corrosion extent.","tool":"Multimeter","warning":"Wet electronics — verify no live before opening."},
   {"step":2,"action":"Remove enclosure; clean PCB corrosion with isopropyl; assess for replacement vs repair.","tool":"Heat gun / isopropyl",None:"warning"},
   {"step":3,"action":"Replace degraded gasket; apply dielectric grease to all connectors; re-seal to IP65.","tool":"Dielectric grease, gasket pick",None:"warning"},
   {"step":4,"action":"Remount controller away from the direct spray path; verify throttle response on test.","tool":"Socket set",None:"warning"},
  ]),

 ("5da3dcdd-5dfc-4c4a-b10f-d7a2f8ff9798",
  "Unitree G1 Whole-Body Impact — Fall-Prevention & Damage Assessment",
  "advanced", 75,
  ["Fall-prevention MPC config access", "Impact-cover kit", "IMU diagnostic tool", "Torque driver set"],
  [{"part_name":"Impact-absorbing limb/housing covers","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None}],
  [
   {"step":1,"action":"Enable MPC fall-prevention controller; run pre-gait stability check and abort on IMU anomaly.","tool":"Fall-prevention MPC config access",None:"warning"},
   {"step":2,"action":"After any tip-over, power down and inspect housing/limbs for cracks and joint deformation.","tool":"Torque driver set","warning":"Joint actuator deformation = do not power until assessed."},
   {"step":3,"action":"Fit impact-absorbing covers on high-strike zones; verify no interference with joints.","tool":None,None:"warning"},
   {"step":4,"action":"Validate graceful fall reflex in a controlled drop test before autonomous operation.","tool":None,None:"warning"},
  ]),

 ("68030b45-1f63-4d46-ab69-f650f1fde7bd",
  "Unitree B2 Main Battery Contactor — Cycle-Count Monitor & Predictive Replace",
  "advanced", 50,
  ["Contact-resistance meter", "DC bus safety tools", "Contactor puller", "Torque driver set"],
  [{"part_name":"High-current contactor (rated for pack bus)","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None}],
  [
   {"step":1,"action":"Log contactor cycle count from BMS; flag any unit past 80% of rated cycles for replacement.","tool":"Contact-resistance meter",None:"warning"},
   {"step":2,"action":"Measure contact resistance; welded/stuck contact (>spec) = replace immediately, do not bypass.","tool":"Contact-resistance meter","warning":"Bypassing a welded contact is a fire risk."},
   {"step":3,"action":"Install redundant pre-charge circuit; verify bus energizes without dropout on test.","tool":"Torque driver set",None:"warning"},
   {"step":4,"action":"Add predictive-replacement flag to maintenance schedule at derate threshold.","tool":None,None:"warning"},
  ]),

 ("08556b7e-5142-43de-8351-eb3a59f42589",
  "Unitree H1-2 Battery / DC-Bus Regulation — Brownout Lockout & Load-Shed Tuning",
  "advanced", 55,
  ["DC bus scope", "Bus-undervoltage config tool", "Cell-balancer access", "Torque driver set"],
  [{"part_name":"Supercapacitor buffer module (bus-rated)","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None}],
  [
   {"step":1,"action":"Scope bus voltage under peak-demand gait; record minimum sag and compute margin.","tool":"DC bus scope",None:"warning"},
   {"step":2,"action":"Set bus-undervoltage lockout with graceful shutdown above the observed sag floor.","tool":"Bus-undervoltage config tool",None:"warning"},
   {"step":3,"action":"Enable load-shedding scheduler so compute + actuators never pull simultaneously at peak.","tool":None,None:"warning"},
   {"step":4,"action":"Run cell-balancing pass; verify SoC spread <0.02 V before return to service.","tool":"Cell-balancer access",None:"warning"},
  ]),

 ("d8b48a09-104c-46af-9c1c-bd006c6d4eff",
  "Zipline P2 Delivery Winch/Tether — Lubricate, Inspect & Pre-Flight Deploy Test",
  "intermediate", 35,
  ["Winch lubricant", "Tether-wear gauge", "Pre-flight test rig", "Torque driver set"],
  [{"part_name":"Winch drive lubricant (low-temp rated)","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None},
   {"part_name":"Redundant tether release mechanism","part_number":None,"qty":1,"supplier":"generic/field-standard","unit_cost_usd":None}],
  [
   {"step":1,"action":"Lubricate winch path; inspect tether for fray, abrasion, or stiffness; replace if worn.","tool":"Winch lubricant, tether-wear gauge",None:"warning"},
   {"step":2,"action":"Verify redundant release mechanism actuates cleanly both electrically and manually.","tool":"Pre-flight test rig",None:"warning"},
   {"step":3,"action":"Run pre-flight deploy/retract cycle; confirm full travel with no stall or jam.","tool":None,None:"warning"},
   {"step":4,"action":"Log tether cycle count; flag for replacement at wear limit.","tool":None,None:"warning"},
  ]),

 ("1fbbe3a7-e847-4e97-b3b3-7f387f91a8c9",
  "Zipline P2 Battery Energy Management — Reserve Margin & SoC Calibration",
  "advanced", 40,
  ["SoC calibration tool", "Weather-derate config access", "Battery diagnostic"],
  [],
  [
   {"step":1,"action":"Set conservative reserve margin (e.g. 30%) in the mission planner default.","tool":"SoC calibration tool",None:"warning"},
   {"step":2,"action":"Recalibrate SoC model with a full charge/discharge cycle; compare estimate vs actual.","tool":"Battery diagnostic",None:"warning"},
   {"step":3,"action":"Enable weather-derate logic so headwind/low-temp automatically extends reserve.","tool":"Weather-derate config access",None:"warning"},
   {"step":4,"action":"Verify abort logic triggers a safe landing when projected return reserve is insufficient.","tool":None,None:"warning"},
  ]),

 ("e88c97c1-5008-43d1-b6a6-2d7660f6760a",
  "Zipline P2 Wing-Rotor Transition Actuator — Airspeed-Gate & Wind-Limit Enforce",
  "advanced", 50,
  ["Airspeed sensor check", "Actuator inspection tool", "Attitude-sensor redundancy config", "Torque driver set"],
  [],
  [
   {"step":1,"action":"Verify airspeed-gate interlock prevents transition below the certified threshold.","tool":"Airspeed sensor check",None:"warning"},
   {"step":2,"action":"Inspect transition actuators for wear/binding; replace if travel is not full and smooth.","tool":"Actuator inspection tool",None:"warning"},
   {"step":3,"action":"Enforce wind-limit envelope in the flight planner; block auto-transition above limit.","tool":None,None:"warning"},
   {"step":4,"action":"Confirm redundant attitude sensor agrees within tolerance before any transition.","tool":"Attitude-sensor redundancy config",None:"warning"},
  ]),
]

# Clean any None keys that slipped in (python dicts can't have None key; fix typos)
def clean_steps(steps):
    out=[]
    for s in steps:
        d={}
        for k,v in s.items():
            if k is None: continue
            d[k]=v
        out.append(d)
    return out

existing = {r["failure_mode_id"] for r in q("SELECT failure_mode_id FROM repair_protocols;")}
rows=[]
for fm_id,title,skill,labor,tools,parts,steps in P:
    if fm_id in existing:
        print(f"skip {fm_id[:8]} (already has protocol)")
        continue
    steps = clean_steps(steps)
    steps_j = json.dumps(steps).replace("'","''")
    tools_arr = "ARRAY[" + ",".join(f"'{t.replace(chr(39),chr(39)+chr(39))}'" for t in tools) + "]"
    parts_j = json.dumps(parts).replace("'","''")
    rows.append(
        f"('{fm_id}','{title.replace(chr(39),chr(39)+chr(39))}','{skill}',{labor},"
        f"{tools_arr},'{parts_j}'::jsonb,'{steps_j}'::jsonb,"
        f"'engineering-estimate',1)"
    )

print(f"Inserting {len(rows)} repair protocols...")
if rows and not DRY:
    vals=",".join(rows)
    run("INSERT INTO repair_protocols "
        "(failure_mode_id, title, skill_level, labor_minutes, tools_required, parts_json, steps_json, source_url, version) "
        f"VALUES {vals} ON CONFLICT DO NOTHING;")
    after = q("SELECT count(*) AS n FROM repair_protocols rp WHERE rp.failure_mode_id IN "
              f"('{','.join(f[0] for f in P)}');")
    print("Critical-with-protocol now:", after[0]['n'] if after else '?', "of 11")
else:
    print("(dry-run) would insert", len(rows))
