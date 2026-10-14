-- HuggingFace enrichment: Unitree G1 loco-manipulation dataset
-- Found in live HuggingFace scrub (NVIDIA PhysicalAI-Robotics-Locomanipulation-GRAIL)
-- Real NVIDIA dataset: 611h of physics-validated 4D HOI trajectories for Unitree G1

INSERT INTO platform_sources (platform_id, source_type, source_name, source_url, license, description, size)
VALUES ('bab53eea-2dd9-4102-8269-d8cf075b34a1', 'dataset', 'PhysicalAI-Robotics-Locomanipulation-GRAIL',
        'https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Locomanipulation-GRAIL',
        'NVIDIA Open',
        'Physics-validated 4D human-object interaction (HOI) trajectories for the Unitree G1 humanoid — 611h of training data (100M+ frames @ 50Hz), Isaac Lab + SONIC whole-body tracker, multi-stage pipeline: SMPL-X via GEM-SMPL, FoundationPose object 6-DoF, GMR retargeting to G1, SONIC policy validation under contact dynamics',
        '611 h (100M+ frames); BONES-SEED subset 142,220 annotated sequences / 288h from 522 actors')
ON CONFLICT DO NOTHING;
