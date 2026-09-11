from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

MODEL_PATH = "models/best.pt"
IMAGE_PATH = "test_images/test.jpg"

print("Loading YOLO model...")

detection_model = AutoDetectionModel.from_pretrained(
    model_type="ultralytics",
    model_path=MODEL_PATH,
    confidence_threshold=0.25,
    device="cuda:0",
)

print("Running SAHI sliced inference...")

result = get_sliced_prediction(
    IMAGE_PATH,
    detection_model,
    slice_height=512,
    slice_width=512,
    overlap_height_ratio=0.2,
    overlap_width_ratio=0.2,
)

print("\n=== DETECTIONS ===")
print("Objects detected:", len(result.object_prediction_list))

for i, prediction in enumerate(result.object_prediction_list, start=1):
    print(
        f"{i}. Class={prediction.category.name} | "
        f"Confidence={prediction.score.value:.3f}"
    )

result.export_visuals(export_dir="sahi_results")

print("\nDone.")
print("Check the folder: sahi_results")