-- HuggingFace enrichment: new platform_sources rows
-- Found via live scrub of huggingface.co/datasets (robotics category, 2024-2026)
-- All URLs verified against search results; sizes/labels are from dataset cards.

INSERT INTO platform_sources (platform_id, source_type, source_name, source_url, license, description, size) VALUES

-- ── Manipulators (Franka Panda, UR5e, KUKA LBR Med 14) ─────────────────────

-- DROID: 76k trajectories, 350h, Franka Panda w/ stereo RGB-D + wrist cam
('64a200f8-578f-4420-a48f-4634d333f5ec', 'dataset', 'DROID',
 'https://huggingface.co/datasets/KarlP/droid', 'CC-BY-4.0',
 '76k teleoperated manipulation trajectories, 350h, 564 scenes, 86 tasks, Franka Panda — largest in-the-wild manipulation dataset',
 '2 TB (LeRobot format); 1.13 TB (unofficial OXE port)'),

('64a200f8-578f-4420-a48f-4634d333f5ec', 'dataset', 'PhysicalAI-Robotics-Manipulation-SingleArm',
 'https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-SingleArm', 'NVIDIA Open',
 'IsaacSim-generated Franka Panda block stacking, cabinet/drawer opening — 7-DOF joint + gripper actions, wrist+world RGB-D',
 '15.3 GB (subset already on file; full dataset larger)'),

('686ad073-f264-4d22-9dfa-41dc7342465e', 'dataset', 'Open X-Embodiment',
 'https://huggingface.co/datasets/jxu124/OpenX-Embodiment', 'CC-BY-4.0 (varies per subdataset)',
 '1M+ real robot trajectories, 22 embodiments — includes Berkeley UR5, Franka, KUKA subsets; RT-X / RT-2-X training data',
 '1.13 TB (unofficial port) / 2TB+ (full OXE)'),

-- ── Delivery ground robots (Serve RS2, Starship Gen3) ────────────────────────

('91dea3f8-e757-40d7-90b0-4a99e73e5a5a', 'dataset', 'R-KNav',
 'https://huggingface.co/datasets/robotcom/R-KNav_dataset', '—',
 '300h sample of real-world sidewalk rover (R-Kiwi) navigation across 15 US locations — last-mile delivery autonomy data',
 '300 h sample (full fleet dataset larger)'),

('91dea3f8-e757-40d7-90b0-4a99e73e5a5a', 'dataset', 'Simaihub-Mobile-Robot-Nav',
 'https://huggingface.co/datasets/Simaihub/Simaihub_Mobile_Robot_Navigation_Training_Dataset_sample', '—',
 'Licensed expert navigation trajectories for offline RL / imitation learning — multi-scene indoor AMR, dynamic obstacles, domain randomization (Isaac Lab, v2.0 2026-08-14)',
 '—'),

('597dc9ad-0217-4441-9fab-02971548410b', 'dataset', 'R-KNav',
 'https://huggingface.co/datasets/robotcom/R-KNav_dataset', '—',
 'Sidewalk rover navigation dataset — relevant to sidewalk delivery robot autonomy (Starship-class)',
 '300 h sample'),

-- ── Quadrupeds (Unitree B2, Go2, Boston Dynamics Spot) ───────────────────────

('1ebaf54f-9eb6-4a7a-bb49-8a15d87e26a0', 'dataset', 'GrandTour',
 'https://huggingface.co/datasets/leggedrobotics/grand_tour_dataset', 'CC-BY-4.0',
 'ETH RSL GrandTour: largest open-access legged-robotics dataset — multi-modal (spinning LiDAR, RGB, stereo depth, proprioception), ANYmal-D across alpine/forest/urban/demolished-building environments with RTK-GNSS + total-station ground truth',
 '—'),

('42167878-8aee-475b-8ff5-fb3bb335da6b', 'dataset', 'Quadruped-SLAM-Dataset',
 'https://github.com/EN3D-Lab/Quadruped-SLAM-dataset', '—',
 'Unitree Go2 SLAM dataset — leg kinematics (joint encoders + contact), IMU, Hesai XT16 3D LiDAR; diverse locomotion (walking, stairs, running, slip/fall/recovery) on Road00 (1240s, 12.1 GB)',
 '12.1 GB (Road00 seq)'),

('9a9b7db6-81d1-4b34-9ccf-a9e7ea0dd933', 'dataset', 'GrandTour',
 'https://huggingface.co/datasets/leggedrobotics/grand_tour_dataset', 'CC-BY-4.0',
 'Legged-robotics multi-modal dataset — quadruped state estimation, perception, and SLAM benchmarks (Spot-class legged platform applications)',
 '—'),

-- ── Drones (DJI Agras T50, Matrice 350, Agras T60, Skydio X10) ─────────────

('c6c39ca9-7a23-4d92-adad-86d7be455007', 'dataset', 'Seraphim-Drone-Detection',
 'https://huggingface.co/datasets/lgrzybowski/seraphim-drone-detection-dataset', '—',
 'Comprehensive drone image detection dataset curated from 23 open-source sources — UAV detection across varying scales/environments (ag-drone surveillance relevance)',
 '—'),

('190266eb-73cf-4c55-9b16-3fb80826425a', 'dataset', 'Seraphim-Drone-Detection',
 'https://huggingface.co/datasets/lgrzybowski/seraphim-drone-detection-dataset', '—',
 'Drone detection image dataset — relevant to enterprise drone perception / detect-and-avoid (Matrice-class inspection use)',
 '—'),

('8b6daa76-3265-4435-bdf2-0a698a214fff', 'dataset', 'Seraphim-Drone-Detection',
 'https://huggingface.co/datasets/lgrzybowski/seraphim-drone-detection-dataset', '—',
 'Drone detection image dataset — relevant to ag-drone surveillance and collision avoidance',
 '—'),

('d0e6900e-12ff-4382-9742-cd7e281ce461', 'dataset', 'Seraphim-Drone-Detection',
 'https://huggingface.co/datasets/lgrzybowski/seraphim-drone-detection-dataset', '—',
 'Drone detection image dataset — relevant to NDAA-compliant inspection drone perception (Skydio-class)',
 '—'),

-- ── Orthopedic surgery robot (Mako) ──────────────────────────────────────────

('aef927e7-d47d-45e8-9a79-84e2cd4f847a', 'dataset', 'OAIZIB-CM',
 'https://huggingface.co/datasets/YongchengYAO/OAIZIB-CM', '—',
 'Automated Segmentation of Knee Bone and Cartilage (CartiMorph project) — knee MRI bone/cartilage/meniscus segmentation; relevant to Mako knee arthroplasty CT-planning pipeline',
 '—'),

('aef927e7-d47d-45e8-9a79-84e2cd4f847a', 'dataset', 'Pelvic-Bone-Fragments-Segmentation',
 'https://huggingface.co/datasets/Novel-BioMedAI/Pelvic_Bone_Fragments_with_Injuries_Segmentation_Challenge', '—',
 'MICCAI 2024 PENGWIN challenge — pelvic fracture segmentation from CT; relevant to Mako spine/pelvic procedure planning',
 '—')

ON CONFLICT DO NOTHING;
