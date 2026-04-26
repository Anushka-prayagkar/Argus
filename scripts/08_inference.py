import cv2
from ultralytics import YOLO

MODEL = r"D:\ArgusAI - DEMO DAY\runs\argus_v22\weights\best.pt"
IMAGE = r"D:\ArgusAI - DEMO DAY\image.png"     # ← Indian pothole image

model  = YOLO(MODEL)
result = model(IMAGE, conf=0.10)[0]
result.show()                       # opens window with boxes drawn
print(f"Detections: {len(result.boxes)}")
for box in result.boxes:
    print(f"  Class: {int(box.cls)} Conf: {float(box.conf):.3f}")