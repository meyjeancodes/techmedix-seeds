#!/usr/bin/env python3
"""Generate manufacturer-accurate Unitree B2 blueprint silhouettes from the real
open-source URDF (BSD-3, unitree_ros b2_description/urdf/b2_description.urdf).
Side-view (X-Z) convex hull per sub-assembly. B2 is a quadruped, so we group
body + each leg. Emits TS to /Users/megan/tm-seeds/b2-chassis.ts (staged
OUTSIDE any git tree).
"""
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import ConvexHull
from pathlib import Path

URDF = "/Users/megan/masters/unitree_ros/robots/b2_description/urdf/b2_description.urdf"
MESH_DIR = Path("/Users/megan/masters/unitree_ros/robots/b2_description/meshes")
OUT = Path("/Users/megan/tm-seeds/b2-chassis.ts")

GROUP_RULES = [
    ("body",    ["trunk", "base_link", "hip", "imu", "lidar"]),
    ("leg-fl",  ["FL_", "fl_"]),
    ("leg-fr",  ["FR_", "fr_"]),
    ("leg-rl",  ["RL_", "rl_"]),
    ("leg-rr",  ["RR_", "rr_"]),
]

def group_for(name):
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

tree = ET.parse(URDF); root = tree.getroot()
links = {}
for ln in root.findall("link"):
    name = ln.get("name"); mesh=None; R=np.eye(3); t=np.zeros(3)
    vis = ln.find("visual")
    if vis is not None:
        geo = vis.find("geometry")
        if geo is not None:
            m = geo.find("mesh"); mesh = m.get("filename") if m is not None else None
        o = vis.find("origin")
        if o is not None:
            if o.get("xyz"): t=np.array([float(v) for v in o.get("xyz").split()])
            if o.get("rpy"): R=rot_rpy([float(v) for v in o.get("rpy").split()])
    links[name]={"mesh":mesh,"R":R,"t":t}

joints={}
for jn in root.findall("joint"):
    par=jn.find("parent"); chi=jn.find("child")
    if par is None or chi is None: continue
    R=np.eye(3); t=np.zeros(3)
    o=jn.find("origin")
    if o is not None:
        if o.get("xyz"): t=np.array([float(v) for v in o.get("xyz").split()])
        if o.get("rpy"): R=rot_rpy([float(v) for v in o.get("rpy").split()])
    joints[jn.get("name")]={"parent":par.get("link"),"child":chi.get("link"),"R":R,"t":t}

child_to_parent={j["child"]:j for j in joints.values()}
cache={}
def load_mesh(fname):
    if fname in cache: return cache[fname]
    p=Path(fname)
    if not p.is_absolute(): p=MESH_DIR/Path(fname).name
    if not p.exists(): p=MESH_DIR/(Path(fname).stem+".dae")
    if not p.exists(): p=MESH_DIR/(Path(fname).stem+".STL")
    if not p.exists():
        cache[fname]=None; return None
    m=trimesh.load(str(p))
    v=np.asarray(m.vertices) if not hasattr(m,"geometry") else np.vstack([g.vertices for g in m.geometry.values()])
    cache[fname]=v; return v

def world_tf(link):
    R=np.eye(3); t=np.zeros(3); chain=[]
    cur=link
    while cur in child_to_parent:
        chain.append(child_to_parent[cur]); cur=child_to_parent[cur]["parent"]
    for j in reversed(chain):
        R=j["R"]@R; t=j["R"]@t+j["t"]
    li=links.get(link)
    if li and li["R"] is not None:
        R=li["R"]@R; t=li["R"]@t+li["t"]
    return R,t

group_pts={g:[] for g,_ in GROUP_RULES}; group_pts["other"]=[]
loaded=skipped=0
for name,info in links.items():
    if not info["mesh"]: continue
    verts=load_mesh(info["mesh"])
    if verts is None or len(verts)<4: skipped+=1; continue
    R,t=world_tf(name)
    world=(R@verts.T).T+t
    group_pts[group_for(name)].append(world[:,[0,2]])
    loaded+=1

ALL=np.vstack([np.vstack(v) for v in group_pts.values() if v]) if any(group_pts.values()) else np.zeros((0,2))
if len(ALL)==0: raise SystemExit("no points")
minx,maxx=ALL[:,0].min(),ALL[:,0].max(); minz,maxz=ALL[:,1].min(),ALL[:,1].max()
W,H=400,280; spanx=maxx-minx; spanz=maxz-minz
scale=min(W/(spanx*1.12), H/(spanz*1.08))
def norm(p):
    x=(p[0]-minx)*scale+(W-spanx*scale)/2
    y=H-((p[1]-minz)*scale+(H-spanz*scale)/2)
    return (round(float(x),1),round(float(y),1))
def simplify(pts,eps=1.6):
    pts=np.asarray(pts,float)
    if len(pts)<3: return pts
    keep=np.zeros(len(pts),bool); keep[0]=keep[-1]=True; stack=[(0,len(pts)-1)]
    while stack:
        s,e=stack.pop(); dmax,idx=0.0,s
        a,b=pts[s],pts[e]; seg=1e-9 if np.allclose(a,b) else np.linalg.norm(b-a)
        for i in range(s+1,e):
            d=np.linalg.norm(np.cross(b-a,a-pts[i]))/seg
            if d>dmax: dmax,idx=d,i
        if dmax>eps: keep[idx]=True; stack+=[(s,idx),(idx,e)]
    return pts[keep]
def hull_path(pts_list):
    merged=np.vstack([p for p in pts_list if len(p)])
    if len(merged)<4: return ""
    try: hull=ConvexHull(merged); v=merged[hull.vertices]
    except: v=merged
    c=v.mean(0); v=v[np.argsort(np.arctan2(v[:,1]-c[1],v[:,0]-c[0]))]
    vn=[norm(p) for p in v]; s=simplify(vn,2.0)
    if len(s)<3: s=vn
    return "M "+" L ".join(f"{x},{y}" for x,y in s)+" Z"

group_paths={g:hull_path(pts) for g,pts in group_pts.items() if pts}
lines=["// AUTO-GENERATED from Unitree B2 open-source URDF (BSD-3).",
"// Source: unitree_ros/robots/b2_description/urdf/b2_description.urdf",
"// Side-view convex-hull silhouettes per sub-assembly (true poses).",
"// ViewBox 0 0 400 280. Teaching text curated by hand.",
'export const B2_SILHOUETTE_D: Record<string,string> = {']
for g,d in group_paths.items():
    if d: lines.append(f'  "{g}": "{d}",')
lines.append("};")
OUT.write_text("\n".join(lines))
print(f"loaded {loaded} skipped {skipped}")
for g,pts in group_pts.items():
    n=sum(len(p) for p in pts)
    if n:
        a=np.vstack(pts); print(f"  {g:7s} verts={n:6d} x[{a[:,0].min():.2f},{a[:,0].max():.2f}] z[{a[:,1].min():.2f},{a[:,1].max():.2f}] {'yes' if group_paths.get(g) else 'NO'}")
print(f"span {spanx:.3f} x {spanz:.3f} m  scale {scale:.1f}")
