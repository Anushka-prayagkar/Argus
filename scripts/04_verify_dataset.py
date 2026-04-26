import os, glob
from collections import Counter

DEST = "D:\\ArgusAI - DEMO DAY\\data\\merged"
NAMES = {0: "pothole", 1: "pedestrian", 2: "obstacle"}

def verify_split(split):
    imgs   = glob.glob(f"{DEST}/{split}/images/*.jpg")
    imgs  += glob.glob(f"{DEST}/{split}/images/*.png")
    labels = glob.glob(f"{DEST}/{split}/labels/*.txt")

    no_label     = 0
    empty_label  = 0
    class_counts = Counter()
    corrupt      = 0

    for img in imgs:
        stem  = os.path.splitext(os.path.basename(img))[0]
        label = os.path.join(DEST, split, "labels", stem + ".txt")

        if not os.path.exists(label):
            no_label += 1
            continue

        lines = open(label).readlines()
        if not lines:
            empty_label += 1
            continue

        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                corrupt += 1
                continue
            try:
                cls = int(parts[0])
                _ = [float(x) for x in parts[1:]]
                class_counts[cls] += 1
            except ValueError:
                corrupt += 1

    print(f"\n  {split.upper()}")
    print(f"    Images       : {len(imgs)}")
    print(f"    Labels       : {len(labels)}")
    print(f"    Missing label: {no_label}")
    print(f"    Empty label  : {empty_label}")
    print(f"    Corrupt lines: {corrupt}")
    print(f"    Class distribution:")
    for cls_id, count in sorted(class_counts.items()):
        name = NAMES.get(cls_id, f"unknown_{cls_id}")
        print(f"      Class {cls_id} ({name:<12}): {count:>6} annotations")

print("-" * 20)
print("DATASET VERIFICATION")

for split in ["train", "valid", "test"]:
    verify_split(split)
print("\n" + "-" * 20)