from ultralytics import YOLO

MODEL_PATH = "models/best.pt"
IMAGE_PATH = "test_images/test.jpg"

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("Running normal YOLO inference...")

results = model.predict(
    source=IMAGE_PATH,
    conf=0.25,
    device=0,
    save=True,
    project="normal_results",
    name="prediction"
)

print("\n=== NORMAL YOLO DETECTIONS ===")

total = 0

for result in results:
    total += len(result.boxes)

    for i, box in enumerate(result.boxes, start=1):
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        print(
            f"{i}. Class={model.names[class_id]} | "
            f"Confidence={confidence:.3f}"
        )

print(f"\nObjects detected: {total}")
print("Done.")
print("Check: normal_results/prediction/")