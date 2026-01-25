edf_path = "../eegDetectionApi/.data/edfs/sample.edf"
channel = "C3"

from DetectionConfig.detect import DetectionInstructions, detect_spindles
dto = DetectionInstructions(
    detection_id="test_detection",
    edf_absolute_path=edf_path,
    channel=channel,
    configuration={},
)

results = detect_spindles(dto)
for res in results:
    print(f"Spindle detected from {res.start_seconds} to {res.end_seconds} seconds.")
