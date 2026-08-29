#!/usr/bin/env python3
"""Generate platform_sources SQL, then run it via supabase db query."""
import json, os, subprocess, sys

HOME = os.path.expanduser("~")

SOURCES = [
    ("intuitive-davinci", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "750h surgical robotics training data, da Vinci kinematics + video", "4.5 TB"),
    ("intuitive-davinci", "model", "GR00T-H", "https://huggingface.co/nvidia/GR00T-H", "NVIDIA Open", "3B VLA foundation model for surgical robotics policy", "3B params"),
    ("intuitive-davinci", "model", "Cosmos-H-Surgical-Simulator", "https://huggingface.co/nvidia/Cosmos-H-Surgical-Simulator", "NVIDIA Open", "Action-conditioned surgical world foundation model", "2B params"),
    ("intuitive-davinci", "adapter", "dVRK", "https://github.com/jhu-dvrk/saw", "BSD", "da Vinci Research Kit — open research interface", None),
    ("cmr-versius", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "CMR Versius clinical procedures", "4.5 TB"),
    ("asensus-senhance", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Senhance surgical system data", "4.5 TB"),
    ("jnj-ottava", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Johnson & Johnson Ottava surgical platform", "4.5 TB"),
    ("medtronic-hugo", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Medtronic Hugo surgical system", "4.5 TB"),
    ("virtual-incision-mira", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Virtual Incision MIRA miniature surgical robot", "4.5 TB"),
    ("moon-surgical-maestro", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Moon Surgical Maestro assistive arm", "4.5 TB"),
    ("rob-surgical-bitrack", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Rob Surgical BiTrack dual-arm urology robot", "4.5 TB"),
    ("torin-surgical", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Torin surgical robotics prototype", "4.5 TB"),
    ("franka-panda", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Franka Panda 7-DOF research manipulator", "4.5 TB"),
    ("franka-panda", "dataset", "Manipulation-SingleArm", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-SingleArm", "NVIDIA Open", "Single-arm manipulation dataset", "15.3 GB"),
    ("universal-ur5e", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Universal Robots UR5e collaborative arm", "4.5 TB"),
    ("kuka-med14", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "KUKA LBR Med 14 medical-grade manipulator", "4.5 TB"),
    ("unitree_g1", "dataset", "WorldModel Synthetic", "https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes", "NVIDIA Open", "Unitree G1 synthetic embodied-robot scenes", "2.08 TB"),
    ("unitree_g1", "dataset", "UBTECH challenge2026", "https://huggingface.co/datasets/UBTECH-Robotics/challenge2026_dataset", "—", "Humanoid manipulation tasks", "59.7 GB"),
    ("unitree_g1", "dataset", "Community Dataset v3", "https://huggingface.co/datasets/HuggingFaceVLA/community_dataset_v3", "Apache 2.0", "Cross-embodiment pretraining (791 datasets, 46 robot types)", "758 GB"),
    ("unitree-h1-2", "dataset", "WorldModel Synthetic", "https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes", "NVIDIA Open", "Unitree H1-2 synthetic embodied-robot scenes", "2.08 TB"),
    ("unitree-h2", "dataset", "WorldModel Synthetic", "https://huggingface.co/datasets/nvidia/PhysicalAI-WorldModel-Synthetic-Embodied-Robot-Scenes", "NVIDIA Open", "Unitree H2 synthetic embodied-robot scenes", "2.08 TB"),
    ("figure-02", "dataset", "UBTECH challenge2026", "https://huggingface.co/datasets/UBTECH-Robotics/challenge2026_dataset", "—", "Humanoid manipulation tasks", "59.7 GB"),
    ("tesla-optimus", "dataset", "UBTECH challenge2026", "https://huggingface.co/datasets/UBTECH-Robotics/challenge2026_dataset", "—", "Humanoid manipulation tasks", "59.7 GB"),
    ("boston_dynamics_spot", "dataset", "Community Dataset v3", "https://huggingface.co/datasets/HuggingFaceVLA/community_dataset_v3", "Apache 2.0", "Cross-embodiment pretraining dataset", "758 GB"),
    ("unitree-b2", "dataset", "kine2go", "https://huggingface.co/datasets/MIMUW-Robotics/kine2go", "CC-BY-4.0", "Unitree Go2 kinematic motion dataset (800 rollouts)", "31 GB"),
    ("unitree-go2", "dataset", "kine2go", "https://huggingface.co/datasets/MIMUW-Robotics/kine2go", "CC-BY-4.0", "Unitree Go2 kinematic motion dataset (800 rollouts)", "31 GB"),
    ("dji_matrice_350", "dataset", "U2UData-2", "https://huggingface.co/datasets/fengtt42/U2UData-2", "—", "15 UAVs, 120h autonomous collaborative flight", None),
    ("skydio_x10", "dataset", "U2UData-2", "https://huggingface.co/datasets/fengtt42/U2UData-2", "—", "15 UAVs, 120h autonomous collaborative flight", None),
    ("dji_agras_t50", "dataset", "U2UData-2", "https://huggingface.co/datasets/fengtt42/U2UData-2", "—", "15 UAVs, 120h autonomous collaborative flight", None),
    ("dji-agras-t60", "dataset", "U2UData-2", "https://huggingface.co/datasets/fengtt42/U2UData-2", "—", "15 UAVs, 120h autonomous collaborative flight", None),
    ("zipline_p2", "dataset", "U2UData-2", "https://huggingface.co/datasets/fengtt42/U2UData-2", "—", "15 UAVs, 120h autonomous collaborative flight", None),
    ("serve-rs2", "dataset", "vehicle-fleet-management", "https://huggingface.co/datasets/mindweave/vehicle-fleet-management", "—", "60 vehicles, 15,000 trip records", None),
    ("starship_gen3", "dataset", "vehicle-fleet-management", "https://huggingface.co/datasets/mindweave/vehicle-fleet-management", "—", "60 vehicles, 15,000 trip records", None),
    ("amazon_proteus", "dataset", "vehicle-fleet-management", "https://huggingface.co/datasets/mindweave/vehicle-fleet-management", "—", "60 vehicles, 15,000 trip records", None),
    ("amazon_proteus", "dataset", "iot-sensor-telemetry", "https://huggingface.co/datasets/mindweave/iot-sensor-telemetry", "—", "Smart factory IoT telemetry, predictive maintenance", None),
    ("bird_three", "dataset", "iot-sensor-telemetry", "https://huggingface.co/datasets/mindweave/iot-sensor-telemetry", "—", "Smart factory IoT telemetry", None),
    ("lime_gen4", "dataset", "iot-sensor-telemetry", "https://huggingface.co/datasets/mindweave/iot-sensor-telemetry", "—", "Smart factory IoT telemetry", None),
    ("rad_commercial", "dataset", "iot-sensor-telemetry", "https://huggingface.co/datasets/mindweave/iot-sensor-telemetry", "—", "Smart factory IoT telemetry", None),
    ("veo-s1", "dataset", "iot-sensor-telemetry", "https://huggingface.co/datasets/mindweave/iot-sensor-telemetry", "—", "Smart factory IoT telemetry", None),
    ("lely-discovery-collector", "dataset", "iot-sensor-telemetry", "https://huggingface.co/datasets/mindweave/iot-sensor-telemetry", "—", "Smart factory IoT telemetry", None),
    ("dewalt-dale", "dataset", "iot-sensor-telemetry", "https://huggingface.co/datasets/mindweave/iot-sensor-telemetry", "—", "Smart factory IoT telemetry", None),
    ("ekso-eksonr", "dataset", "iot-sensor-telemetry", "https://huggingface.co/datasets/mindweave/iot-sensor-telemetry", "—", "Smart factory IoT telemetry", None),
    ("stryker-mako", "dataset", "Open-H-Embodiment", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment", "CC-BY-4.0", "Orthopedic surgical robot data", "4.5 TB"),
]

def main():
    # Get platform IDs via a single query, parse the JSON properly
    raw = subprocess.run(
        ["supabase", "db", "query", "--linked", "SELECT id, slug FROM platforms;"],
        capture_output=True, text=True, cwd=HOME
    ).stdout

    # Find the JSON object in the output
    start = raw.find('{"rows"')
    if start == -1:
        start = raw.find('{')
    if start == -1:
        print("Could not parse platform query output")
        return

    try:
        data = json.loads(raw[start:])
        plats = {r["slug"]: r["id"] for r in data.get("rows", [])}
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return

    print(f"Loaded {len(plats)} platforms")

    # Build a single SQL file with all inserts
    sql_lines = ["INSERT INTO platform_sources (platform_id, source_type, source_name, source_url, license, description, size) VALUES "]
    values = []

    for slug, stype, name, url, lic, desc, size in SOURCES:
        pid = plats.get(slug)
        if not pid:
            print(f"  !! {slug}: no platform row")
            continue
        lic_val = f"'{lic}'" if lic else "NULL"
        size_val = f"'{size}'" if size else "NULL"
        desc_esc = desc.replace("'", "''")
        name_esc = name.replace("'", "''")
        values.append(f"('{pid}', '{stype}', '{name_esc}', '{url}', {lic_val}, '{desc_esc}', {size_val})")

    sql_lines.append(",\n".join(values))
    sql_lines.append("ON CONFLICT DO NOTHING;")

    full_sql = "\n".join(sql_lines)

    # Write to file
    sql_path = os.path.join(HOME, "tm-seeds", "populate_sources.sql")
    with open(sql_path, "w") as f:
        f.write(full_sql)
    print(f"SQL written to {sql_path} ({len(values)} rows)")

    # Run it
    r = subprocess.run(
        ["supabase", "db", "query", "--linked", full_sql],
        capture_output=True, text=True, cwd=HOME
    )
    if r.returncode != 0:
        print(f"Error: {r.stderr[:300]}")
    else:
        print(f"Done | inserted {len(values)} sources")


if __name__ == "__main__":
    main()
