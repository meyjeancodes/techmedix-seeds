#!/usr/bin/env python3
"""
Generate a manufacturer-accurate Unitree G1 blueprint from the real open-source
URDF (BSD-3, unitree_ros g1_29dof). Robust XML parse of the URDF; for each link
with a visual mesh we compute its world transform via the joint tree, then load
the STL and place every vertex in world coordinates. Side-view (X-Z) convex hull
per sub-assembly, grouped by official G1 link naming. Emits a TS snippet to
/Users/megan/tm-seeds/g1-chassis.ts (staged OUTSIDE any git tree).
"""
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import ConvexHull
from pathlib import Path

URDF = "/Users/megan/masters/unitree_ros/robots/g1_description/g1_29dof.urdf"
MESH_DIR = Path("/Users/megan/masters/unitree_ros/robots/g1_description/meshes")
OUT = Path("/Users/megan/tm-seeds/g1-chassis.ts")

GROUP_RULES = [
    ("head",   ["head", "d455", "d435", "camera", "lidar"]),
    ("torso",  ["waist", "torso", "base_link", "imu", "pelvis", "constraint", "support", "shoulder"]),
    ("arm-l",  ["left_elbow", "left_wrist", "left_arm", "Link11_L", "Link12_L", "Link13_L"]),
    ("arm-r",  ["right_elbow", "right_wrist", "right_arm", "Link11_R", "Link12_R", "Link13_R"]),
    ("hand-l", ["left_hand", "left_palm", "left_index", "left_middle", "left_ring", "left_little", "left_thumb", "left_rubber", "L_hand", "left_swing"]),
    ("hand-r", ["right_hand", "right_palm", "right_index", "right_middle", "right_ring", "right_little", "right_thumb", "right_rubber", "R_hand", "right_swing"]),
    ("leg-l",  ["left_hip", "left_knee", "left_ankle", "Link14_L", "Link15_L", "Link16_L", "Link17_L", "left_foot"]),
    ("leg-r",  ["right_hip", "right_knee", "right_ankle", "Link14_R", "Link15_R", "Link16_R", "Link17_R", "right_foot"]),
]

def group_for(name: str):
    l = name.lower()
    for g, ks in GROUP_RULES:
        if any(k in l for k in ks):
            return g
    return "other"

def rot_rpy(rpy):
    r, p, y = rpy
    Rx = np.array([[1,0,0],[0,np.cos(r),-np.sin(r)],[0,np.sin(r),np.cos(r)]])
    Ry = np.array([[np.cos(p),0,np.sin(p)],[0,1,0],[-np.sin(p),0,np.cos(p)]])
    Rz = np.array([[np.cos(y),-np.sin(y),0],[np.sin(y),np.cos(y),0],[0,0,1]])
    return Rz @ Ry @ Rx

tree = ET.parse(URDF)
root = tree.getroot()

links = {}
for ln in root.findall("link"):
    name = ln.get("name")
    mesh = None; R = np.eye(3); t = np.zeros(3)
    vis = ln.find("visual")
    if vis is not None:
        geo = vis.find("geometry")
        if geo is not None:
            mesh_el = geo.find("mesh")
            if mesh_el is not None:
                mesh = mesh_el.get("filename")
        origin = vis.find("origin")
        if origin is not None:
            xyz = origin.get("xyz"); rpy = origin.get("rpy")
            if xyz: t = np.array([float(v) for v in xyz.split()])
            if rpy: R = rot_rpy([float(v) for v in rpy.split()])
    links[name] = {"mesh": mesh, "R": R, "t": t}

joints = {}
for jn in root.findall("joint"):
    parent = jn.find("parent"); child = jn.find("child")
    if parent is None or child is None: continue
    R = np.eye(3); t = np.zeros(3)
    origin = jn.find("origin")
    if origin is not None:
        xyz = origin.get("xyz"); rpy = origin.get("rpy")
        if xyz: t = np.array([float(v) for v in xyz.split()])
        if rpy: R = rot_rpy([float(v) for v in rpy.split()])
    joints[jn.get("name")] = {"parent": parent.get("link"), "child": child.get("link"), "R": R, "t": t}

child_to_parent = {j["child"]: j for j in joints.values()}

cache = {}
def load_mesh(fname):
    if fname in cache: return cache[fname]
    p = Path(fname)
    if not p.is_absolute():
        p = MESH_DIR / Path(fname).name
    if not p.exists():
        p = MESH_DIR / (Path(fname).stem + ".STL")
    if not p.exists():
        cache[fname] = None; return None
    m = trimesh.load(str(p))
    v = np.asarray(m.vertices) if not hasattr(m, "geometry") else np.vstack([g.vertices for g in m.geometry.values()])
    cache[fname] = v; return v

def world_tf(link):
    R = np.eye(3); t = np.zeros(3); chain = []
    cur = link
    while cur in child_to_parent:
        chain.append(child_to_parent[cur]); cur = child_to_parent[cur].get("parent") if False else child_to_parent[cur]["parent"]
    for j in reversed(chain):
        R = j["R"] @ R; t = j["R"] @ t + j["t"]
    li = links.get(link)
    if li and li["R"] is not None:
        R = li["R"] @ R; t = li["R"] @ t + li["t"]
    return R, t

group_pts = {g: [] for g, _ in GROUP_RULES}
group_pts["other"] = []
loaded = 0; skipped = 0
for name, info in links.items():
    if not info["mesh"]: continue
    verts = load_mesh(info["mesh"])
    if verts is None or len(verts) < 4:
        skipped += 1; continue
    R, t = world_tf(name)
    world = (R @ verts.T).T + t
    group_pts[group_for(name)].append(world[:, [0, 2]])
    loaded += 1

ALL = np.vstack([np.vstack(v) for v in group_pts.values() if v]) if any(group_pts.values()) else np.zeros((0,2))
if len(ALL) == 0:
    raise SystemExit("no mesh points resolved")

minx, maxx = ALL[:,0].min(), ALL[:,0].max()
minz, maxz = ALL[:,1].min(), ALL[:,1].max()
W, H = 200, 360
spanx = maxx - minx; spanz = maxz - minz
scale = min(W/(spanx*1.12), H/(spanz*1.08))

def norm(p):
    x = (p[0]-minx)*scale + (W - spanx*scale)/2
    y = H - ((p[1]-minz)*scale + (H - spanz*scale)/2)
    return (round(float(x),1), round(float(y),1))

def simplify(pts2d, epsilon=1.6):
    """Ramer–Douglas–Peucker on an open polyline (pts2d: Nx2)."""
    pts2d = np.asarray(pts2d, dtype=float)
    if len(pts2d) < 3:
        return pts2d
    keep = np.zeros(len(pts2d), dtype=bool); keep[0] = keep[-1] = True
    stack = [(0, len(pts2d) - 1)]
    while stack:
        s, e = stack.pop()
        d_max, idx = 0.0, s
        a, b = pts2d[s], pts2d[e]
        if np.allclose(a, b):
            seg_len = 1e-9
        else:
            seg_len = np.linalg.norm(b - a)
        for i in range(s + 1, e):
            p = pts2d[i]
            d = np.linalg.norm(np.cross(b - a, a - p)) / seg_len
            if d > d_max:
                d_max, idx = d, i
        if d_max > epsilon:
            keep[idx] = True
            stack.append((s, idx)); stack.append((idx, e))
    return pts2d[keep]

def hull_path(pts_list):
    merged = np.vstack([p for p in pts_list if len(p)])
    if len(merged) < 4:
        return ""
    try:
        hull = ConvexHull(merged); v = merged[hull.vertices]
    except Exception:
        v = merged
    # order hull points by angle around centroid for a clean closed loop
    c = v.mean(axis=0)
    v = v[np.argsort(np.arctan2(v[:,1]-c[1], v[:,0]-c[0]))]
    vn = [norm(p) for p in v]
    # simplify the closed loop (drop first/last duplicate by RDP on open, then close)
    simplified = simplify(vn, epsilon=1.8)
    if len(simplified) < 3:
        simplified = vn
    return "M " + " L ".join(f"{x},{y}" for x,y in simplified) + " Z"

group_paths = {g: hull_path(pts) for g, pts in group_pts.items() if pts}

lines = []
lines.append("// AUTO-GENERATED from Unitree G1 open-source URDF (BSD-3).")
lines.append("// Source: unitree_ros/robots/g1_description/g1_29dof.urdf")
lines.append("// Side-view convex-hull silhouettes per sub-assembly (true poses).")
lines.append("// Teaching text, explodeOffset, labelAnchor, category curated by hand.")
lines.append("export const G1_SILHOUETTE_D: Record<string,string> = {")
for g, d in group_paths.items():
    if d:
        lines.append(f'  "{g}": "{d}",')
lines.append("};")
OUT.write_text("\n".join(lines))

print(f"loaded {loaded} meshes, skipped {skipped}")
print("WROTE", OUT)
for g, pts in group_pts.items():
    n = sum(len(p) for p in pts)
    if n:
        arr = np.vstack(pts)
        arr_z = arr[:,1]
        print(f"  {g:7s} verts={n:7d} z[{arr_z.min():.2f},{arr_z.max():.2f}] path={'yes' if group_paths.get(g) else 'NO'}")
print(f"span {spanx:.3f} x {spanz:.3f} m  scale {scale:.1f}")
