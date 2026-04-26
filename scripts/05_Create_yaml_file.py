import os, yaml

MERGED = "D:\\ArgusAI - DEMO DAY\\data\\merged"

data = {
    "path"  : MERGED,
    "train" : "train/images",
    "val"   : "valid/images",
    "test"  : "test/images",
    "nc"    : 3,
    "names" : {0: "pothole", 1: "pedestrian", 2: "obstacle"}
}

# Write yaml
yaml_path = os.path.join(MERGED, "data.yaml")
with open(yaml_path, "w") as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

# Verify it immediately
with open(yaml_path) as f:
    loaded = yaml.safe_load(f)

print("data.yaml created and verified")