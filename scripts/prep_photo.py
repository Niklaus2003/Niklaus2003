#!/usr/bin/env python3
"""
Prepare Aaron Francis's helmet character avatar for high-definition ASCII conversion:
  1. Frames the full helmet character from avatar.jpg (1024x1440 centered crop).
  2. Applies smooth elliptical background masking to zero out extraneous night bokeh.
  3. Lifts shadow detail in the visor opening (eyes, eyebrows, flower, balaclava) via gamma curve.
  4. Applies multi-scale CLAHE to crisply capture the eyes, white flower, STUDDS logo, and chin vent.
  5. Saves source-prepped.png for make_ascii_svg.py.
"""
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "avatar.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")


def prep(image_path, out_path):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        sys.exit(1)

    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: could not read {image_path}")
        sys.exit(1)

    h_orig, w_orig = img.shape[:2]

    # Full helmet framing
    if w_orig >= 1480 and h_orig >= 1024:
        crop = img[0:1024, 40:1480]
    else:
        crop = img

    h, w = crop.shape[:2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # 1. Smooth elliptical mask to isolate helmet & communicator from night bokeh
    mask = np.zeros((h, w), dtype=np.float32)
    # Main helmet dome and body
    cv2.ellipse(mask, (int(w * 0.48), int(h * 0.49)), (int(w * 0.42), int(h * 0.48)), 0, 0, 360, 1.0, -1)
    # Communicator unit on right side
    cv2.ellipse(mask, (int(w * 0.87), int(h * 0.73)), (int(w * 0.10), int(h * 0.20)), -20, 0, 360, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (61, 61), 22)

    # 2. Lift shadows across image
    norm = gray.astype(np.float32) / 255.0
    lifted = np.power(norm, 0.58) * 255.0

    # 3. Overall CLAHE
    clahe_main = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(12, 12))
    main_enh = clahe_main.apply(lifted.astype(np.uint8))

    # 4. Local enhancement for visor opening (eyes, eyebrows, white flower)
    face_mask = np.zeros((h, w), dtype=np.float32)
    cv2.ellipse(face_mask, (int(w * 0.41), int(h * 0.47)), (int(w * 0.20), int(h * 0.11)), 0, 0, 360, 1.0, -1)
    face_mask = cv2.GaussianBlur(face_mask, (71, 71), 25)

    clahe_face = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(6, 6))
    face_enh = clahe_face.apply(lifted.astype(np.uint8))

    combined = (main_enh.astype(np.float32) * (1.0 - face_mask) + face_enh.astype(np.float32) * face_mask)

    # 5. Mask out background to pure black
    masked_img = (combined * mask).astype(np.uint8)

    # 6. Unsharp mask for crisp eye catchlights and visor details
    blurred = cv2.GaussianBlur(masked_img, (0, 0), 1.5)
    final_enh = cv2.addWeighted(masked_img, 1.35, blurred, -0.35, 0)

    cv2.imwrite(out_path, final_enh)
    print(f"Prepped image saved to {out_path} ({final_enh.shape[1]}x{final_enh.shape[0]})")


if __name__ == "__main__":
    prep(INP, OUT)
