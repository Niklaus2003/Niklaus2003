#!/usr/bin/env python3
"""
Prepare a portrait photo for clean ASCII conversion:
  1. Downscale large images (for fast, high-quality segmentation)
  2. Remove background (rembg or smart OpenCV GrabCut fallback)
  3. Boost LOCAL contrast (CLAHE)
  4. Composite onto pure white so the background maps to space characters

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INP = os.path.join(HERE, "..", "avatar.jpg")
if not os.path.exists(DEFAULT_INP):
    DEFAULT_INP = os.path.join(HERE, "..", "avatar.png")
if not os.path.exists(DEFAULT_INP):
    DEFAULT_INP = os.path.join(HERE, "..", "source-photo.jpg")

INP = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INP
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")


def isolate_subject(img_path):
    pil_img = Image.open(img_path).convert("RGB")
    
    # Pre-scale to reasonable size for GrabCut / CLAHE performance & quality
    max_dim = 800
    w, h = pil_img.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        pil_img = pil_img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    
    # Try rembg if installed
    try:
        from rembg import remove
        print("Using rembg for neural background removal...")
        rgba = pil_img.convert("RGBA")
        cut = remove(rgba)
        rgb = np.array(cut.convert("RGB"))
        alpha = np.array(cut.split()[-1])
        return rgb, alpha
    except (ImportError, Exception) as e:
        print(f"rembg not active ({e}); using smart OpenCV GrabCut segmentation...")
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        h, w = img.shape[:2]
        mask = np.zeros((h, w), np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        # Foreground box with 6% margin
        rect = (int(w * 0.06), int(h * 0.04), int(w * 0.88), int(h * 0.92))
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return rgb, mask2


def main():
    if not os.path.exists(INP):
        print(f"Error: input file '{INP}' not found.")
        sys.exit(1)

    print(f"Processing image: {INP}")
    rgb, alpha = isolate_subject(INP)

    # 2. Local contrast enhancement (CLAHE)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Lift mids so the face lands in the sparse, crisp character spectrum
    gray = cv2.convertScaleAbs(gray, alpha=1.05, beta=18)

    # 3. Composite onto pure white background using feathered alpha mask
    mask = alpha.astype(np.float32) / 255.0
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
    out = gray.astype(np.float32) * mask + 255.0 * (1.0 - mask)
    out = np.clip(out, 0, 255).astype(np.uint8)

    Image.fromarray(out, mode="L").save(OUT)
    print("wrote", OUT, out.shape)


if __name__ == "__main__":
    main()
