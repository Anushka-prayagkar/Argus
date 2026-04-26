import os
from roboflow import Roboflow

API_KEY = "3vZ8QEY8SItgjBNEqrbn"
ROOT = "D:\\ArgusAI - DEMO DAY\\data\\raw_downloads"

rf = Roboflow(api_key=API_KEY)

DATASETS = [
    ("intel-unnati-training-program", "pothole-detection-bqu6s",  "pothole_main"),
    ("kartik-zvust",                  "pothole-detection-yolo-v8", "pothole_extra"),
    ("yolov8-training-l1ktn",         "pedestrians-ihyip",         "pedestrian_main"),
    ("adp-l8hde",                     "yolov8-6apfg",              "traffic_combined"),
    ("object-detect-ydedz",           "vehicle-detection-2.0-wwhpg","vehicles"),
]

DATASETS_POTHOLES = [
    ("smartathon", "new-pothole-detection", "pothole_main")
]

def downloads(workspace, project, folder):
    save_at = os.path.join(ROOT, folder)
    for i in range(1,5):
        try:
            rf.workspace(workspace).project(project).version(i).download(
                "yolov8", location=save_at, overwrite=True
            )
            print(f"{folder} - version{i}")
            return True
        except Exception as e:
            if "404" in str(e): continue
            print(f"x{folder} i{i}: {e}")
    print(f"x{folder} - all version failed")
    return False

for ws, proj, folder in DATASETS:
    print(f"\ndownloading {folder}...")
    downloads(ws, proj, folder)