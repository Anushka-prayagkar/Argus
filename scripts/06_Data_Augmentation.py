import os, cv2, glob
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import albumentations as A
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

TRAIN_IMGS   = "D:\\ArgusAI - DEMO DAY\\data\\merged\\train\\images"
TRAIN_LABELS = "D:\\ArgusAI - DEMO DAY\\data\\merged\\train\\labels"

bp = lambda mv=0.3: A.BboxParams(format="yolo", label_fields=["cls"], min_visibility=mv)

PIPELINES = {
    "night": A.Compose([
        A.RandomBrightnessContrast(brightness_limit=(-0.6, -0.25), contrast_limit=(-0.1, 0.3), p=1.0),
        A.HueSaturationValue(hue_shift_limit=5, sat_shift_limit=(-40, -10), val_shift_limit=(-50, -20), p=0.9),
        A.GaussNoise(std_range=(0.02, 0.08), p=0.6),
        A.RandomShadow(shadow_roi=(0, 0.4, 1, 1), shadow_dimension=4, p=0.5),
    ], bbox_params=bp()),

    "rain": A.Compose([
        A.MotionBlur(blur_limit=(5, 11), p=0.7),
        A.GaussianBlur(blur_limit=(3, 7), p=0.5),
        A.RandomRain(slant_range=(-10, 10), drop_length=12, drop_width=1, drop_color=(180, 180, 200), blur_value=3, brightness_coefficient=0.85, rain_type="drizzle", p=0.6),
        A.RandomBrightnessContrast(brightness_limit=(-0.25, 0.05), contrast_limit=(-0.15, 0.1), p=0.6),
        A.HueSaturationValue(sat_shift_limit=(-25, 0), val_shift_limit=(-20, 0), p=0.5),
    ], bbox_params=bp()),

    "sun": A.Compose([
        A.RandomBrightnessContrast(brightness_limit=(0.1, 0.4), contrast_limit=(0.1, 0.4), p=1.0),
        A.RandomShadow(shadow_roi=(0, 0.3, 1, 1), shadow_dimension=5, p=0.7),
        A.HueSaturationValue(hue_shift_limit=8, sat_shift_limit=(10, 35), val_shift_limit=(10, 30), p=0.6),
        A.GaussNoise(std_range=(0.01, 0.04), p=0.3),
    ], bbox_params=bp()),

    "haze": A.Compose([
        A.RandomFog(fog_coef_range=(0.1, 0.35), alpha_coef=0.1, p=0.8),
        A.RandomBrightnessContrast(brightness_limit=(-0.1, 0.15), contrast_limit=(-0.3, -0.05), p=0.7),
        A.GaussianBlur(blur_limit=(3, 5), p=0.5),
    ], bbox_params=bp()),

    "angle": A.Compose([
        A.Affine(translate_percent=0.06, scale=(0.85, 1.1), rotate=(-10, 10), border_mode=cv2.BORDER_REFLECT, p=0.85),
        A.Perspective(scale=(0.03, 0.07), keep_size=True, p=0.6),
        A.RandomBrightnessContrast(brightness_limit=0.15, p=0.4),
    ], bbox_params=bp(0.25)),
}

def read_label(path):
    boxes, classes = [], []
    for line in open(path).readlines():
        parts = line.strip().split()
        if len(parts) != 5: continue
        classes.append(int(float(parts[0])))
        boxes.append([float(x) for x in parts[1:]])
    return boxes, classes

def save_label(path, boxes, classes):
    with open(path, "w") as f:
        for cls, box in zip(classes, boxes):
            f.write(f"{cls} {' '.join(f'{x:.6f}' for x in box)}\n")

def process_image(img_path):
    stem  = os.path.splitext(os.path.basename(img_path))[0]
    label = os.path.join(TRAIN_LABELS, stem + ".txt")
    if not os.path.exists(label): return 0
    boxes, classes = read_label(label)
    if 0 not in classes: return 0

    image   = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
    created = 0

    for name, pipeline in PIPELINES.items():
        try:
            out       = pipeline(image=image, bboxes=boxes, cls=classes)
            aug_boxes = list(out["bboxes"])
            aug_cls   = list(out["cls"])
            if not aug_boxes: continue
            ext      = os.path.splitext(img_path)[1]
            new_stem = f"{stem}_aug_{name}"
            cv2.imwrite(os.path.join(TRAIN_IMGS, new_stem + ext), cv2.cvtColor(out["image"], cv2.COLOR_RGB2BGR))
            save_label(os.path.join(TRAIN_LABELS, new_stem + ".txt"), aug_boxes, aug_cls)
            created += 1
        except Exception:
            continue
    return created

images  = glob.glob(f"{TRAIN_IMGS}/*.jpg") + glob.glob(f"{TRAIN_IMGS}/*.png")
created = 0

with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(tqdm(executor.map(process_image, images), total=len(images), desc="Augmenting"))

print(f"\n----------- Created  : {created} augmented images")
print(f"  Original : {len(images)} images")
print(f"  New total: {len(images) + created} train images")