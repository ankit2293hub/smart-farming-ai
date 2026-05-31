import cv2
import numpy as np

def estimate_severity(image_path: str) -> dict:
    img = cv2.imread(image_path)
    if img is None:
        return {"percentage": 0, "label": "Unknown"}

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Healthy green tissue
    green_mask    = cv2.inRange(hsv,
                        np.array([35, 40, 40]),
                        np.array([85, 255, 255]))

    # Diseased tissue (brown/yellow spots)
    diseased_mask = cv2.inRange(hsv,
                        np.array([10, 50, 50]),
                        np.array([35, 255, 200]))

    total    = cv2.countNonZero(green_mask) + cv2.countNonZero(diseased_mask)
    infected = cv2.countNonZero(diseased_mask)

    if total == 0:
        return {"percentage": 0, "label": "Unknown"}

    pct = (infected / total) * 100

    if pct < 20:    label = "Mild"
    elif pct < 50:  label = "Moderate"
    else:           label = "Severe"

    return {"percentage": round(pct, 1), "label": label}