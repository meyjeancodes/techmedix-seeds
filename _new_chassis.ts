
// ─── Surgical robot chassis (medical-surgical platforms) ───────────────────────
// Schematic side-view of a standard 4-arm patient-side surgical robot (e.g.
// da Vinci / Versius / Hugo / Mako class). Geometry is a stylized-correct
// schematic — NOT a manufacturer CAD file. Parts map to the real serviceable
// subsystems a biomedical-tech would open.

const SURGICAL: ChassisDefinition = {
  id: "surgical",
  label: "Surgical Robot — Patient-Side Cart",
  viewBox: "0 0 220 360",
  silhouette:
    "M 100,20 L 120,20 L 120,40 L 132,52 L 132,96 L 150,96 L 158,120 L 158,250 L 62,250 L 62,120 L 70,96 L 88,96 L 100,40 Z " +
    "M 150,96 L 200,110 L 200,150 L 156,150 Z " +
    "M 62,96 L 20,110 L 20,150 L 64,150 Z " +
    "M 158,250 L 170,340 L 150,340 L 142,260 Z " +
    "M 62,250 L 50,340 L 70,340 L 78,260 Z",
  platformIds: [
    "intuitive-davinci",
    "cmr-versius",
    "jnj-ottava",
    "medtronic-hugo",
    "stryker-mako",
    "asensus-senhance",
  ],
  parts: [
    {
      id: "surge-boom",
      name: "Patient-Side Manipulator Booms",
      category: "actuator",
      d: "M 100,20 L 120,20 L 120,40 L 132,52 L 132,96 L 88,96 L 100,40 Z",
      explodeOffset: [0, -24],
      summary: "4 articulated arms on a sterile boom",
      details:
        "The patient-side cart carries the instrument arms (typically 4) on a sterile boom. Each arm is a sealed, reprocessable manipulator with a remote-center-of-motion (RCM) point that pivots about the port incision — this is what keeps the incision fixed while the tool tip moves.",
      failureSignature:
        "RCM pivot compliance drift (tissue drag at port), arm collision during setup, encoder zero-loss after reprocessing.",
      diagnosticCue:
        "Run the arm through a port-calibration routine; RCM error > 1 mm at the trocar = boom kinematics drift. Inspect the sterile drape for breach.",
      replacement:
        "Per-arm swap: 60 min, biomedical-certified. Full RCM re-calibration + drape-integrity test after install.",
      labelAnchor: [110, 58],
    },
    {
      id: "surge-instruments",
      name: "Instrument Drive Units",
      category: "end-effector",
      d: "M 150,96 L 200,110 L 200,150 L 156,150 Z M 62,96 L 20,110 L 20,150 L 64,150 Z",
      explodeOffset: [22, 6],
      summary: "Removable wristed instruments + drive",
      details:
        "Each arm terminates in a sterile instrument (forceps, scissors, needle-driver, monopolar) driven by a sealed instrument-drive unit. Wrist articulation is actuated at the distal link for fine motion.",
      failureSignature:
        "Wrist stall mid-procedure, instrument not recognized by drive, articulation jitter, seal failure on the shaft.",
      diagnosticCue:
        "Attach a known instrument; command wrist articulation 10×. > 2° dead-band or recognition fault = drive-unit or instrument fault.",
      replacement:
        "Instrument: per-case single-use/reprocess. Drive unit: 45 min, biomed cert. Re-zero wrist encoders.",
      labelAnchor: [180, 125],
    },
    {
      id: "surge-vision",
      name: "Endoscope / Vision Bridge",
      category: "sensor",
      d: "M 88,96 L 132,96 L 132,52 L 88,52 Z",
      explodeOffset: [0, -10],
      summary: "Stereo endoscope + light source",
      details:
        "A dual-channel endoscope provides the 3D surgical view. The vision cart processes the feed; a separate light source delivers illumination through the scope.",
      failureSignature:
        "Image dropout, color shift, fogging, light-source overtemp cutoff.",
      diagnosticCue:
        "Verify both channels render; check light-source temp. Fogging mid-case = insufflation/anti-fog fault, not a scope fault.",
      replacement:
        "Scope: per-case. Light source / vision bridge: 30 min, biomed cert.",
      labelAnchor: [110, 74],
    },
    {
      id: "surge-cart",
      name: "Base / Power & Insufflation",
      category: "frame",
      d: "M 62,120 L 158,120 L 158,250 L 62,250 Z",
      explodeOffset: [0, 14],
      summary: "Mobile base, power distribution, insufflator",
      details:
        "The cart base houses power distribution, the insufflator (for laparoscopic modes), and braking casters. It is the serviceable core — everything else mounts to the boom.",
      failureSignature:
        "Insufflation pressure instability, caster brake failure, base E-stop fault.",
      diagnosticCue:
        "Confirm set-pressure hold within ±2 mmHg. Test brake engage/disengage. Verify base E-stop interrupts all arm motion.",
      replacement:
        "Base service: 90 min, biomed cert. Re-run safety interlock test post-service.",
      labelAnchor: [110, 185],
    },
    {
      id: "surge-drive",
      name: "Column / Drive Actuators",
      category: "drivetrain",
      d: "M 158,250 L 170,340 L 150,340 L 142,260 Z M 62,250 L 50,340 L 70,340 L 78,260 Z",
      explodeOffset: [-18, 18],
      summary: "Setup-joint actuators + brakes",
      details:
        "The lower column holds the gross-positioning actuators (setup joints) used to park arms before draping. These are high-torque with holding brakes.",
      failureSignature:
        "Setup-joint sag under load, brake slip on power loss, positioning drift between cases.",
      diagnosticCue:
        "With brakes engaged, apply rated load; > 3 mm settle = brake or actuator fault. Re-home all setup joints between cases.",
      replacement:
        "Setup-joint actuator: 75 min, L3 biomed cert. Re-calibrate home positions.",
      labelAnchor: [60, 300],
    },
  ],
};

// ─── Rehabilitation exoskeleton chassis (e.g. EksoNR class) ────────────────────
// Schematic of a powered gait exoskeleton: hip + knee actuators, trunk frame,
// foot plates. Stylized-correct, not manufacturer CAD.

const EXO: ChassisDefinition = {
  id: "exo",
  label: "Rehab Exoskeleton — Powered Gait Frame",
  viewBox: "0 0 200 360",
  silhouette:
    "M 70,30 L 130,30 L 134,70 L 140,150 L 120,180 L 120,300 L 80,300 L 80,180 L 60,150 L 66,70 Z " +
    "M 80,300 L 70,346 L 96,346 L 100,300 Z " +
    "M 120,300 L 130,346 L 104,346 L 100,300 Z",
  platformIds: ["ekso-eksonr"],
  parts: [
    {
      id: "exo-trunk",
      name: "Trunk / Control Frame",
      category: "compute",
      d: "M 70,30 L 130,30 L 134,70 L 66,70 Z",
      explodeOffset: [0, -18],
      summary: "Onboard controller, IMU, power",
      details:
        "The trunk frame holds the gait controller, IMU for balance/orientation, and the main battery. It wraps the patient's torso via a harness.",
      failureSignature:
        "IMU drift causing asymmetric assist, controller fault mid-stride, battery sag under dual-actuator load.",
      diagnosticCue:
        "Zero the IMU at standing rest; drift > 2° = calibration needed. Check battery under a loaded stride cycle.",
      replacement:
        "Controller: 30 min, L2 cert. Battery: 20 min. Re-run gait-calibration macro.",
      labelAnchor: [100, 50],
    },
    {
      id: "exo-hip",
      name: "Hip Actuators",
      category: "actuator",
      d: "M 60,150 L 140,150 L 140,180 L 60,180 Z",
      explodeOffset: [0, -8],
      summary: "Bilateral hip flexion/extension drives",
      details:
        "Hip actuators deliver the primary gait-assist torque. They are the highest-duty actuators in the device and the dominant wear item.",
      failureSignature:
        "Asymmetric assist (one side lags), hip over-temp, audible grind at end-of-travel.",
      diagnosticCue:
        "Command a seated hip flex/extend 10×; compare L/R motor current. > 15% delta = worn side.",
      replacement:
        "Hip actuator: 60 min, L3 cert. Re-zero joint encoders + gait recal.",
      labelAnchor: [100, 165],
    },
    {
      id: "exo-knee",
      name: "Knee Actuators",
      category: "actuator",
      d: "M 80,180 L 120,180 L 120,300 L 80,300 Z",
      explodeOffset: [0, 12],
      summary: "Bilateral knee extension drives",
      details:
        "Knee actuators assist stance stability and swing clearance. They bear peak load during sit-to-stand transitions.",
      failureSignature:
        "Knee buckle under load, extension lag, thermal cutoff on repeated stands.",
      diagnosticCue:
        "Perform 5 sit-to-stand cycles; monitor knee motor current. Cutout or > 20% L/R asymmetry = actuator fault.",
      replacement:
        "Knee actuator: 60 min, L3 cert. Re-run transition-calibration.",
      labelAnchor: [100, 240],
    },
    {
      id: "exo-foot",
      name: "Foot Plates / Cuffs",
      category: "frame",
      d: "M 80,300 L 70,346 L 96,346 L 100,300 Z M 120,300 L 130,346 L 104,346 L 100,300 Z",
      explodeOffset: [16, 18],
      summary: "Ankle-foot orthosis + cuffs",
      details:
        "Foot plates and leg cuffs transfer assist torque to the patient and provide ground reference for the gait controller.",
      failureSignature:
        "Cuff slippage (lost torque transfer), plate crack, strap wear.",
      diagnosticCue:
        "Fit-check cuffs; perform a loaded stand. Slippage > 5 mm = re-fit or replace straps.",
      replacement:
        "Cuffs/straps: 15 min, L1. Plates: 30 min, L2 cert.",
      labelAnchor: [85, 325],
    },
  ],
};

// ─── Delivery-air VTOL chassis (e.g. DJI Matrice 350 class) ──────────────────
// Schematic hexacopter with folding arms + downward gimbal. Stylized-correct.

const DELIVERY_AIR_VTOL: ChassisDefinition = {
  id: "delivery-air-vtol",
  label: "Aerial Delivery Drone — Hexacopter",
  viewBox: "0 0 320 240",
  silhouette:
    "M 120,110 L 200,110 L 210,130 L 110,130 Z " +
    "M 120,110 L 60,60 L 80,55 L 135,100 Z " +
    "M 200,110 L 260,60 L 240,55 L 185,100 Z " +
    "M 110,130 L 40,150 L 55,160 L 120,138 Z " +
    "M 210,130 L 280,150 L 265,160 L 200,138 Z " +
    "M 135,130 L 95,185 L 110,188 L 145,135 Z " +
    "M 185,130 L 225,185 L 210,188 L 175,135 Z " +
    "M 150,138 L 170,138 L 165,200 L 155,200 Z",
  platformIds: ["dji_matrice_350", "dji-agras-t60"],
  parts: [
    {
      id: "vtol-core",
      name: "Central Core / Flight Controller",
      category: "compute",
      d: "M 120,110 L 200,110 L 210,130 L 110,130 Z",
      explodeOffset: [0, -16],
      summary: "Flight controller, GPS, battery bay",
      details:
        "The central core houses the flight controller, RTK-GPS module, and the primary battery bay. All six arms mount here radially.",
      failureSignature:
        "GPS fix loss, flight-controller brownout, battery contact dropout under vibration.",
      diagnosticCue:
        "Check RTK fix status and satellite count pre-flight. Log battery contact resistance; intermittent power = bay fault.",
      replacement:
        "Core: 45 min, L2 cert. Battery bay: 20 min. Re-run compass + IMU calibration.",
      labelAnchor: [160, 120],
    },
    {
      id: "vtol-arm-f",
      name: "Front Folding Arms (×2)",
      category: "actuator",
      d: "M 120,110 L 60,60 L 80,55 L 135,100 Z M 200,110 L 260,60 L 240,55 L 185,100 Z",
      explodeOffset: [-22, -10],
      summary: "Folding motor arms + ESCs",
      details:
        "Front arms fold for transport and carry the forward pair of rotors + electronic speed controllers. Folding locks are a wear/inspection point.",
      failureSignature:
        "Folding-lock slip in flight, ESC over-temp, rotor desync.",
      diagnosticCue:
        "Verify fold-lock engagement before each flight. Post-flight: check ESC temp symmetry across all six.",
      replacement:
        "Arm/ESC: 30 min per arm, L2 cert. Re-center rotor and re-test spin-up.",
      labelAnchor: [70, 70],
    },
    {
      id: "vtol-arm-r",
      name: "Rear Rotor Arms (×4)",
      category: "actuator",
      d: "M 110,130 L 40,150 L 55,160 L 120,138 Z M 210,130 L 280,150 L 265,160 L 200,138 Z M 135,130 L 95,185 L 110,188 L 145,135 Z M 185,130 L 225,185 L 210,188 L 175,135 Z",
      explodeOffset: [22, 8],
      summary: "Four rear/diagonal rotors + ESCs",
      details:
        "The remaining four arms provide thrust and attitude control. Coaxial or offset pairs give the hexacopter its redundancy.",
      failureSignature:
        "Single-rotor failure (loss of redundancy), vibration harmonics, prop imbalance.",
      diagnosticCue:
        "Spin each rotor to hover RPM; measure vibration. One arm hot or imbalanced = prop/motor fault.",
      replacement:
        "Motor/prop: 20 min per rotor, L1 cert. Balance-check after swap.",
      labelAnchor: [255, 155],
    },
    {
      id: "vtol-payload",
      name: "Payload / Gimbal Mount",
      category: "sensor",
      d: "M 150,138 L 170,138 L 165,200 L 155,200 Z",
      explodeOffset: [0, 24],
      summary: "Downward gimbal / delivery bay",
      details:
        "The underside carries either a stabilized gimbal (imaging/survey) or a payload/delivery bay. It is the primary mission interface.",
      failureSignature:
        "Gimbal jitter, payload release fault, bay door stuck.",
      diagnosticCue:
        "Run a gimbal self-test (full pan/tilt). For delivery: perform a tethered release test before flight.",
      replacement:
        "Gimbal/bay: 25 min, L2 cert. Re-calibrate gimbal if fitted.",
      labelAnchor: [160, 175],
    },
  ],
};

