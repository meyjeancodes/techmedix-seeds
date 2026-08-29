#!/usr/bin/env python3
"""Generate seeds + SQL for 9 new TechMedix platforms from Hugging Face data.

Platforms (sourced from NVIDIA Open-H-Embodiment + kine2go datasets):
  Medical surgical robots: virtual-incision-mira, moon-surgical-maestro,
                            rob-surgical-bitrack, torin-surgical
  Research/medical manipulators: franka-panda, universal-ur5e, kuka-med14
  Quadruped: unitree-go2
  Humanoid: unitree-h2

Outputs:
  1. JSON seeds to ~/tm-seeds/pending/
  2. Prints SQL to widen enum + insert platform rows
  3. Optionally runs the SQL via `supabase db query --linked`

Usage:
  python3 ~/tm-seeds/generate_new_platforms.py --dry-run
  python3 ~/tm-seeds/generate_new_platforms.py --apply
"""
import json, os, subprocess, sys

DRY = '--dry-run' in sys.argv
APPLY = '--apply' in sys.argv
HOME = os.path.expanduser("~")
PENDING = os.path.join(HOME, "tm-seeds", "pending")

# ── Platform definitions ────────────────────────────────────────────────────
# name, manufacturer, type, introduced_year, slug, specs_json, image_url, notes
PLATFORMS = [
    {
        "slug": "virtual-incision-mira",
        "name": "MIRA",
        "manufacturer": "Virtual Incision",
        "type": "medical_surgical_robot",
        "introduced_year": 2021,
        "specs_json": {
            "category": "medical_surgical_robot",
            "miniaturized": True,
            "weight_kg": 1.0,
            "dof": 6,
            "minimally_invasive": True,
            "clinical_trials": ["colorectal resection (FDA IDE)"],
            "power": "battery-operated portable",
            "research_dataset": "NVIDIA Open-H-Embodiment (2026)",
        },
        "image_url": None,
        "notes": "Miniature surgical robot for abdominal procedures. NASA-funded, clinical trials for colorectal resection. Source: NVIDIA Open-H-Embodiment dataset (49 institutions).",
    },
    {
        "slug": "moon-surgical-maestro",
        "name": "Maestro",
        "manufacturer": "Moon Surgical",
        "type": "medical_surgical_robot",
        "introduced_year": 2023,
        "specs_json": {
            "category": "medical_surgical_robot",
            "assistive_arm": True,
            "dof": 7,
            "minimally_invasive": True,
            "function": "tissue manipulation + retraction",
            "research_dataset": "NVIDIA Open-H-Embodiment (2026)",
        },
        "image_url": None,
        "notes": "Assistive surgical robotic arm for tissue manipulation and retraction. CE-marked, used in European hospitals. Source: NVIDIA Open-H-Embodiment dataset.",
    },
    {
        "slug": "rob-surgical-bitrack",
        "name": "BiTrack",
        "manufacturer": "Rob Surgical",
        "type": "medical_surgical_robot",
        "introduced_year": 2021,
        "specs_json": {
            "category": "medical_surgical_robot",
            "specialty": "urology",
            "dof": 8,
            "dual_arm": True,
            "needle_driving": True,
            "minimally_invasive": True,
            "research_dataset": "NVIDIA Open-H-Embodiment (2026)",
        },
        "image_url": None,
        "notes": "Dual-arm surgical robot for urological procedures. CE-marked, needle-driving precision. Source: NVIDIA Open-H-Embodiment dataset.",
    },
    {
        "slug": "torin-surgical",
        "name": "Torin",
        "manufacturer": "Intuitive Surgical (advanced prototype)",
        "type": "medical_surgical_robot",
        "introduced_year": 2025,
        "specs_json": {
            "category": "medical_surgical_robot",
            "specialty": "general surgery",
            "targeted_recovery": True,
            "research_dataset": "NVIDIA Open-H-Embodiment (2026)",
        },
        "image_url": None,
        "notes": "Advanced surgical robotics prototype in the Open-H-Embodiment benchmark. Represents next-gen targeted-recovery surgery platform. Source: NVIDIA Open-H-Embodiment dataset.",
    },
    {
        "slug": "franka-panda",
        "name": "Panda",
        "manufacturer": "Franka Emika",
        "type": "manipulator",
        "introduced_year": 2017,
        "specs_json": {
            "category": "research_manipulator",
            "dof": 7,
            "payload_kg": 3.0,
            "reach_mm": 855,
            "joint_torque_sensors": True,
            "control_frequency_hz": 1000,
            "research_dataset": "NVIDIA Open-H-Embodiment (2026)",
        },
        "image_url": None,
        "notes": "7-DOF research manipulator with torque sensing at every joint. Widely used in academic robotics labs for manipulation research. Source: NVIDIA Open-H-Embodiment dataset.",
    },
    {
        "slug": "universal-ur5e",
        "name": "UR5e",
        "manufacturer": "Universal Robots",
        "type": "manipulator",
        "introduced_year": 2018,
        "specs_json": {
            "category": "research_manipulator",
            "dof": 6,
            "payload_kg": 5.0,
            "reach_mm": 850,
            "weight_kg": 20.6,
            "ip_rating": "IP54",
            "collaborative": True,
            "research_dataset": "NVIDIA Open-H-Embodiment (2026)",
        },
        "image_url": None,
        "notes": "6-DOB collaborative industrial robot arm used in healthcare manipulation research. Payload 5kg, reach 850mm. Source: NVIDIA Open-H-Embodiment dataset.",
    },
    {
        "slug": "kuka-med14",
        "name": "LBR Med 14",
        "manufacturer": "KUKA",
        "type": "manipulator",
        "introduced_year": 2020,
        "specs_json": {
            "category": "medical_manipulator",
            "dof": 7,
            "payload_kg": 14.0,
            "reach_mm": 820,
            "weight_kg": 49.0,
            "medical_certified": True,
            "ce_marked": True,
            "research_dataset": "NVIDIA Open-H-Embodiment (2026)",
        },
        "image_url": None,
        "notes": "7-DOF medical-grade manipulator, CE-marked for clinical use. 14kg payload, used in surgical assistance and ultrasound-guided procedures. Source: NVIDIA Open-H-Embodiment dataset.",
    },
    {
        "slug": "unitree-go2",
        "name": "Go2",
        "manufacturer": "Unitree Robotics",
        "type": "quadruped",
        "introduced_year": 2023,
        "specs_json": {
            "category": "quadruped",
            "dof": 12,
            "actuators": "12× BLDC joint motors",
            "weight_kg": 15.0,
            "top_speed_ms": 3.5,
            "battery_minutes": 60,
            "payload_kg": 10.0,
            "sensors": ["lidar", "depth_camera", "IMU", "foot_force"],
            "research_dataset": "MIMUW kine2go (2026)",
        },
        "image_url": None,
        "notes": "12-DOF quadruped for research and education. Real-world kinematic dataset (kine2go) provides 800 motion rollouts for locomotion policy training. Source: kine2go (Genesis simulator).",
    },
    {
        "slug": "unitree-h2",
        "name": "H2",
        "manufacturer": "Unitree Robotics",
        "type": "humanoid",
        "introduced_year": 2024,
        "specs_json": {
            "category": "humanoid",
            "dof": 26,
            "height_cm": 180,
            "weight_kg": 70.0,
            "actuators": "proprietary high-torque joints",
            "payload_kg": 8.0,
            "sensors": ["depth_camera", "lidar", "IMU", "6D_force_torque"],
            "research_dataset": "NVIDIA WorldModel Synthetic (2026)",
        },
        "image_url": None,
        "notes": "Full-size humanoid with 26 DOF. Used in NVIDIA WorldModel synthetic embodied-robot scenes dataset. We have Unitree H1-2; H2 is the taller, heavier successor.",
    },
]

# ── Failure mode seeds ──────────────────────────────────────────────────────
FM_SEEDS = {
    "virtual-incision-mira": [
        {"name": "miniaturized_instrument_slip", "component": "surgical_instrument_tip", "severity": "critical", "mtbf_hours_est": 120, "symptoms": "instrument slip during tissue manipulation; loss of grip precision; unexpected tissue movement", "mitigation": "tip surface coating; grip-force feedback; instrument replacement schedule; surgeon override"},
        {"name": "battery_depletion_mid_procedure", "component": "power_system", "severity": "high", "mtbf_hours_est": 200, "symptoms": "sudden power loss; low-battery warning; reduced actuator torque; emergency shutdown", "mitigation": "pre-op battery check; redundant power cell; hot-swap battery bay; procedure-time limit"},
        {"name": "imaging_fiber_breakage", "component": "endoscopic_imaging", "severity": "high", "mtbf_hours_est": 150, "symptoms": "image degradation; fiberoptic break; dark spots in view; loss of depth perception", "mitigation": "fiber strain relief; pre-op imaging check; redundant imaging; scope replacement"},
        {"name": "sterilization_cycle_fatigue", "component": "instrument_housing", "severity": "medium", "mtbf_hours_est": 300, "symptoms": "housing micro-cracks; seal degradation; discoloration; joint stiffness after autoclave", "mitigation": "cycle-count tracking; seal replacement schedule; single-use sheath option; material upgrade"},
    ],
    "moon-surgical-maestro": [
        {"name": "arm_drift_during_retraction", "component": "arm_actuator", "severity": "critical", "mtbf_hours_est": 180, "symptoms": "unintended arm movement; tissue tension loss; drift from hold position; surgeon repositioning", "mitigation": "brake-on-idle; encoder recalibration; force-limit clamp; scheduled joint service"},
        {"name": "trocar_interface_wear", "component": "trocar_mount", "severity": "high", "mtbf_hours_est": 250, "symptoms": "play in instrument mount; wobble; misalignment; increased insertion force", "mitigation": "trocar replacement schedule; mount inspection; insertion-force monitoring; sterile re-mount"},
        {"name": "software_watchdog_timeout", "component": "control_system", "severity": "high", "mtbf_hours_est": 350, "symptoms": "arm freeze; system reboot; loss of control input; emergency stop activation", "mitigation": "watchdog tuning; dual-controller redundancy; real-time kernel; fault-log analysis"},
        {"name": "arm_cable_fatigue", "component": "internal_cabling", "severity": "medium", "mtbf_hours_est": 400, "symptoms": "intermittent signal loss; arm position error; cable harness wear; connector corrosion", "mitigation": "flex-rated cable; strain relief; bend-radius limit; preventive replacement"},
    ],
    "rob-surgical-bitrack": [
        {"name": "needle_driver_misalignment", "component": "needle_instrument", "severity": "critical", "mtbf_hours_est": 140, "symptoms": "needle deflection; off-target placement; suture failure; tissue tear", "mitigation": "needle-guide calibration; driver-jaw replacement; pre-op alignment check; force feedback"},
        {"name": "dual_arm_desync", "component": "arm_coordination", "severity": "high", "mtbf_hours_est": 220, "symptoms": "arms out of phase; collision risk; workspace violation; master-slave lag", "mitigation": "clock-sync protocol; arm-collision avoidance; workspace boundary; re-mastering routine"},
        {"name": "registration_drift", "component": "patient_registration", "severity": "high", "mtbf_hours_est": 280, "symptoms": "robot-patient coordinate mismatch; targeting error; navigation offset; re-registration needed", "mitigation": "fiducial tracking; continuous registration; drift alarm; re-calibration protocol"},
        {"name": "arm_joint_overtorque", "component": "arm_actuator", "severity": "medium", "mtbf_hours_est": 350, "symptoms": "joint thermal overload; torque limiting; reduced speed; cooldown required", "mitigation": "torque-limit tuning; thermal monitoring; duty-cycle management; cooling period"},
    ],
    "torin-surgical": [
        {"name": "targeted_recovery_tracking_loss", "component": "recovery_tracking_system", "severity": "high", "mtbf_hours_est": 200, "symptoms": "loss of recovery trajectory; tracking drift; fiducial occlusion; guidance error", "mitigation": "multi-camera redundancy; predictive tracking; re-acquisition protocol; surgeon override"},
        {"name": "prototype_actuator_failure", "component": "precision_actuator", "severity": "critical", "mtbf_hours_est": 160, "symptoms": "actuator stalling; position error; unexpected motion; emergency halt", "mitigation": "actuator health monitoring; redundant actuation; graceful degradation; fail-safe braking"},
        {"name": "haptic_feedback_dropout", "component": "force_feedback", "severity": "medium", "mtbf_hours_est": 300, "symptoms": "loss of tactile sensation; force display freeze; latency spike; feedback oscillation", "mitigation": "haptic calibration; signal filtering; latency monitoring; redundant sensor"},
        {"name": "navigation_system_drift", "component": "optical_navigation", "severity": "high", "mtbf_hours_est": 250, "symptoms": "spatial reference drift; instrument tip error; field-of-view loss; recalibration trigger", "mitigation": "active LED tracking; drift correction; reference marker check; environmental lighting control"},
    ],
    "franka-panda": [
        {"name": "joint_torque_sensor_drift", "component": "joint_torque_sensor", "severity": "high", "mtbf_hours_est": 400, "symptoms": "force reading offset; contact detection false-positive; reduced manipulation accuracy", "mitigation": "sensor recalibration; temperature compensation; drift monitoring; sensor replacement"},
        {"name": "gripper_slip_during_manipulation", "component": "franka_hand_gripper", "severity": "medium", "mtbf_hours_est": 350, "symptoms": "object drop; grip-force insufficient; finger wear; slippage on smooth surfaces", "mitigation": "gripper pad replacement; force-closure grasp planning; tactile sensing; slip detection"},
        {"name": "controller_desync", "component": "real_time_controller", "severity": "high", "mtbf_hours_est": 500, "symptoms": "1kHz control loop missed; arm jitter; communication timeout; emergency stop", "mitigation": "real-time kernel tuning; network QoS; watchdog monitoring; redundant control link"},
        {"name": "joint_overtemperature", "component": "joint_actuator", "severity": "medium", "mtbf_hours_est": 450, "symptoms": "motor thermal warning; reduced torque; cooldown pause; joint error", "mitigation": "thermal model; duty-cycle limit; active cooling; ambient temperature control"},
    ],
    "universal-ur5e": [
        {"name": "wrist_joint_backlash", "component": "wrist_joint", "severity": "medium", "mtbf_hours_est": 400, "symptoms": "position error at wrist; play in end-effector; reduced path accuracy", "mitigation": "harmonic drive inspection; backlash compensation; joint replacement; path recalibration"},
        {"name": "teach_pendant_cable_fatigue", "component": "teach_pendant", "severity": "low", "mtbf_hours_est": 600, "symptoms": "intermittent pendant connection; cable fraying; connector looseness", "mitigation": "cable strain relief; connector inspection; wireless pendant option; preventive replacement"},
        {"name": "safety_zone_violation", "component": "safety_scanner", "severity": "high", "mtbf_hours_est": 500, "symptoms": "unexpected entry into workspace; safety stop; reduced throughput; zone breach", "mitigation": "safety scanner calibration; zone configuration; light-curtain backup; access control"},
        {"name": "joint_motor_thermal_overload", "component": "joint_actuator", "severity": "medium", "mtbf_hours_est": 450, "symptoms": "motor temperature warning; reduced speed; cooldown required; duty-cycle limit hit", "mitigation": "thermal monitoring; duty-cycle management; ambient cooling; payload derating"},
    ],
    "kuka-med14": [
        {"name": "force_torque_sensor_drift", "component": "joint_torque_sensor", "severity": "high", "mtbf_hours_est": 350, "symptoms": "force reading offset; contact detection error; reduced compliance accuracy", "mitigation": "sensor recalibration; drift monitoring; temperature compensation; sensor replacement"},
        {"name": "medical_housing_seal_wear", "component": "arm_housing", "severity": "medium", "mtbf_hours_est": 500, "symptoms": "IP-rating compromise; seal degradation; cleaning fluid ingress; discoloration", "mitigation": "seal replacement schedule; IP testing; cleaning protocol; housing inspection"},
        {"name": "lightweight_arm_resonance", "component": "arm_structure", "severity": "medium", "mtbf_hours_est": 400, "symptoms": "vibration at certain poses; path oscillation; settling time increase", "mitigation": "vibration damping; trajectory filtering; stiffness tuning; payload verification"},
        {"name": "certification_expiry", "component": "medical_certification", "severity": "high", "mtbf_hours_est": 8760, "symptoms": "CE-mark lapse; regulatory non-compliance; clinical-use suspension; audit finding", "mitigation": "certification tracking; renewal calendar; notified-body engagement; documentation audit"},
    ],
    "unitree-go2": [
        {"name": "leg_joint_actuator_overheat", "component": "leg_joint_motor", "severity": "high", "mtbf_hours_est": 200, "symptoms": "motor thermal warning; reduced torque; gait degradation; emergency stop", "mitigation": "thermal monitoring; gait derating; cooling period; ambient temperature limit"},
        {"name": "foot_contact_sensor_failure", "component": "foot_force_sensor", "severity": "medium", "mtbf_hours_est": 300, "symptoms": "lost ground-contact feedback; gait instability; stumble; fall risk", "mitigation": "sensor redundancy; gait adaptation; sensor replacement; terrain assessment"},
        {"name": "battery_cell_imbalance", "component": "battery_pack", "severity": "high", "mtbf_hours_est": 400, "symptoms": "reduced runtime; voltage sag; BMS warning; sudden shutdown", "mitigation": "cell balancing; BMS calibration; battery replacement; charge-cycle tracking"},
        {"name": "lidar_occlusion", "component": "lidar_sensor", "severity": "medium", "mtbf_hours_est": 350, "symptoms": "partial field-of-view loss; navigation drift; obstacle miss; localization error", "mitigation": "lidar cleaning; occlusion detection; redundant camera; sensor fusion"},
    ],
    "unitree-h2": [
        {"name": "hip_actuator_overload", "component": "hip_joint_actuator", "severity": "critical", "mtbf_hours_est": 200, "symptoms": "hip torque saturation; walking instability; fall risk; actuator thermal shutdown", "mitigation": "torque-limit tuning; gait derating; hip cooling; payload verification"},
        {"name": "arm_manipulation_payload_exceed", "component": "arm_actuator", "severity": "high", "mtbf_hours_est": 300, "symptoms": "arm oscillation; grasp failure; joint overload; reduced reach accuracy", "mitigation": "payload monitoring; grasp-force limit; arm-stabilization control; task replanning"},
        {"name": "balance_controller_instability", "component": "balance_control", "severity": "critical", "mtbf_hours_est": 250, "symptoms": "upper-body oscillation; foot-slip; IMU drift; corrective step failure", "mitigation": "IMU recalibration; balance-gain tuning; foot-force feedback; emergency sit"},
        {"name": "battery_thermal_runaway_risk", "component": "battery_pack", "severity": "critical", "mtbf_hours_est": 500, "symptoms": "cell temperature spike; BMS thermal alert; reduced power; emergency shutdown", "mitigation": "thermal monitoring; cell balancing; BMS threshold; battery replacement protocol"},
    ],
}


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
    os.makedirs(PENDING, exist_ok=True)

    # ── Step 1: Widen enum if needed ─────────────────────────────────────────
    enum_sql = (
        "ALTER TABLE platforms DROP CONSTRAINT IF EXISTS platforms_type_check;\n"
        "ALTER TABLE platforms ADD CONSTRAINT platforms_type_check\n"
        "  CHECK ((type = ANY (ARRAY["
        "'humanoid'::text, 'quadruped'::text, 'drone'::text, "
        "'delivery_ground'::text, 'delivery_air'::text, "
        "'warehouse_amr'::text, 'micromobility'::text, 'other'::text, "
        "'medical_surgical_robot'::text, 'orthopedic_robot'::text, "
        "'rehab_exoskeleton'::text, 'agri_robot'::text, "
        "'construction_robot'::text, 'manipulator'::text"
        "])));"
    )
    print("=" * 60)
    print("STEP 1: Widen platforms.type enum to include 'manipulator'")
    print("=" * 60)
    print(enum_sql)
    if APPLY:
        print(run_sql(enum_sql))
        print("✓ Enum widened")
    elif DRY:
        print("(dry-run)")
    print()

    # ── Step 2: Insert platform rows ─────────────────────────────────────────
    print("=" * 60)
    print("STEP 2: Insert platform rows")
    print("=" * 60)
    for p in PLATFORMS:
        slug = p["slug"]
        # Check if platform already exists
        existing = q(f"SELECT id FROM platforms WHERE slug='{slug}';")
        if '"rows": [{"id":' in existing or '"rows": [{"id"' in existing:
            print(f"  {slug}: already exists, skip")
            continue
        name = p["name"].replace("'", "''")
        mfr = p["manufacturer"].replace("'", "''")
        ptype = p["type"]
        year = p.get("introduced_year") or "NULL"
        specs = json.dumps(p.get("specs_json", {})).replace("'", "''")
        notes = (p.get("notes") or "").replace("'", "''")
        img = f"'{p['image_url']}'" if p.get("image_url") else "NULL"
        sql = (
            f"INSERT INTO platforms "
            f"(slug, name, manufacturer, type, introduced_year, specs_json, "
            f"techmedix_status, image_url, notes) "
            f"VALUES ('{slug}', '{name}', '{mfr}', '{ptype}', {year}, "
            f"'{specs}'::jsonb, 'supported', {img}, '{notes}');"
        )
        print(f"  {slug}: INSERT")
        if APPLY:
            print(f"    {run_sql(sql)[:100]}")
    print()

    # ── Step 3: Write failure mode seed JSONs ────────────────────────────────
    print("=" * 60)
    print("STEP 3: Write failure mode seed JSONs")
    print("=" * 60)
    for slug, fms in FM_SEEDS.items():
        path = os.path.join(PENDING, f"{slug}.json")
        payload = {"slug": slug, "failure_modes": fms}
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"  {path} ({len(fms)} FMs)")
    print()

    # ── Step 4: Next step ────────────────────────────────────────────────────
    print("=" * 60)
    print("NEXT: Run apply_fms.py to insert failure modes")
    print("=" * 60)
    print(f"  python3 {os.path.join(HOME, 'tm-seeds', 'apply_fms.py')} --dry-run")
    print(f"  python3 {os.path.join(HOME, 'tm-seeds', 'apply_fms.py')}")
    print()
    if not APPLY:
        print("Tip: re-run with --apply to execute enum + inserts live.")


if __name__ == "__main__":
    main()
