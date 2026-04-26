import os, shutil, glob
from tqdm import tqdm

RAW  = "D:\\ArgusAI - DEMO DAY\\data\\raw_downloads"
DEST = "D:\\ArgusAI - DEMO DAY\\data\\merged"

CLASS_MAPS = {
    "pothole_main":     {0: 0},
    "pothole_extra":    {0: 0},
    "pedestrian_main":  {0: 1},
    "traffic_combined": {0:2, 1:1, 2:-1, 3:-1, 4:1, 5:1, 6:2, 7:2, 8:2},
}

def remap_label(label_path, class_map):
    new_lines = []
    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            new_id = class_map.get(int(parts[0]), -1)
            if new_id == -1:
                continue
            new_lines.append(f"{new_id} {' '.join(parts[1:])}\n")
    return new_lines

def merge_split(dataset, split, class_map):
    src_imgs   = os.path.join(RAW,  dataset, split, "images")
    src_labels = os.path.join(RAW,  dataset, split, "labels")
    dst_imgs   = os.path.join(DEST, split, "images")
    dst_labels = os.path.join(DEST, split, "labels")

    if not os.path.exists(src_imgs):
        return 0
    
    os.makedirs(dst_imgs,   exist_ok=True)   # ← ADD THIS
    os.makedirs(dst_labels, exist_ok=True)   # ← ADD THIS

    images = glob.glob(f"{src_imgs}/*.jpg") + glob.glob(f"{src_imgs}/*.png")
    copied = 0

    for img in tqdm(images, desc=f"  {dataset}/{split}", leave=False):
        stem  = os.path.splitext(os.path.basename(img))[0]
        label = os.path.join(src_labels, stem + ".txt")

        if not os.path.exists(label):
            continue

        new_lines = remap_label(label, class_map)
        if not new_lines:
            continue

        ext      = os.path.splitext(img)[1]
        dst_name = f"{dataset}_{stem}{ext}"

        shutil.copy2(img, os.path.join(dst_imgs,   dst_name))
        with open(os.path.join(dst_labels, f"{dataset}_{stem}.txt"), "w") as f:
            f.writelines(new_lines)
        copied += 1

    return copied

total = 0
for dataset, class_map in CLASS_MAPS.items():
    print(f"\n{dataset}")
    for split in ["train", "valid", "test"]:
        n = merge_split(dataset, split, class_map)
        if n: print(f"  {split}: {n} files merged")
        total += n

print(f"\n ### Total merged: {total}")
print(f"  Destination: {DEST}")