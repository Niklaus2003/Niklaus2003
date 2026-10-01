#!/usr/bin/env python3
"""
Prepare Aaron Francis's avatar image faithfully without destructive cropping
or background cutting:
  1. Load full avatar.jpg (preserves the complete original artwork/photo)
  2. Enhance local contrast and micro-details with CLAHE
  3. Clean up ultra-low noise so pure black background maps to spaces

Output: source-prepped.png, consumed by make_ascii_svg.py.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "avatar.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")


def prep(image_path, out_path):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        sys.exit(1)

    print(f"Faithfully processing full image {image_path}...")
    pil_img = Image.open(image_path).convert("RGB")
    arr = np.array(pil_img)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE to balance contrast so all subject details pop
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Slight lift so midtones stand out
    lifted = cv2.convertScaleAbs(enhanced, alpha=1.08, beta=8)

    # Clean dark floor (values < 22 -> 0 so background is crisp pure space)
    cleaned = np.where(lifted < 22, 0, lifted)

    Image.fromarray(cleaned, mode="L").save(out_path)
    print(f"Wrote faithful prepped image to {out_path} with size {cleaned.shape}")


if __name__ == "__main__":
    prep(INP, OUT)
