import torch
from ultralytics import YOLO

def main():
    WEIGHTS = "D:\\ArgusAI - DEMO DAY\\runs\\argus_v22\\weights\\last.pt"
    DATA    = "D:\\ArgusAI - DEMO DAY\\data\\merged\\data.yaml"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device : {device}")
    print(f"GPU    : {torch.cuda.get_device_name(0)}")

    model = YOLO(WEIGHTS)
    model.train(resume=True)

    metrics = model.val(data=DATA)
    print(f"\n{'='*40}")
    print(f"mAP@0.5      : {metrics.box.map50:.4f}")
    print(f"mAP@0.5:0.95 : {metrics.box.map:.4f}")
    print(f"Precision    : {metrics.box.p.mean():.4f}")
    print(f"Recall       : {metrics.box.r.mean():.4f}")
    print(f"{'='*40}")

    model.export(format="onnx", imgsz=640, opset=17, simplify=True)
    print("ONNX export complete.")

if __name__ == "__main__":
    main()