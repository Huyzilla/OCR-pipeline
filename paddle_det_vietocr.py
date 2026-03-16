#!/usr/bin/env python3
"""Hybrid OCR pipeline: PaddleOCR (text detection) + local VietOCR (text recognition).

Usage:
  python paddle_det_vietocr.py \
    --input /path/to/file.pdf \
    --output_txt /path/to/output.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from paddleocr import PaddleOCR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Paddle detection + VietOCR recognition")
    parser.add_argument("--input", required=True, help="Input PDF/image path")
    parser.add_argument("--output_txt", default=None, help="Output TXT path")
    parser.add_argument("--output_json", default=None, help="Output JSON path")
    parser.add_argument("--paddle_lang", default="vi", help="PaddleOCR language for detection pipeline")
    parser.add_argument("--paddle_device", default="cpu", help="Paddle device, e.g. cpu, gpu:0")
    parser.add_argument("--disable_mkldnn", action="store_true", help="Disable MKLDNN in PaddleOCR")
    parser.add_argument("--vietocr_device", default="cpu", help="VietOCR device: cpu or cuda:0")
    parser.add_argument("--vietocr_config", default=None, help="Path to VietOCR yml config")
    parser.add_argument("--vietocr_weights", default=None, help="Path to VietOCR .pth weights")
    parser.add_argument("--min_box_size", type=int, default=8, help="Skip tiny text boxes")
    return parser.parse_args()


def order_poly_indices(polys: list[np.ndarray]) -> list[int]:
    order_keys: list[tuple[float, float, int]] = []
    for i, poly in enumerate(polys):
        arr = np.asarray(poly, dtype=np.float32)
        y_min = float(np.min(arr[:, 1]))
        x_min = float(np.min(arr[:, 0]))
        order_keys.append((y_min, x_min, i))
    order_keys.sort(key=lambda x: (x[0], x[1]))
    return [x[2] for x in order_keys]


def crop_quad(img: np.ndarray, poly: np.ndarray) -> np.ndarray:
    pts = np.asarray(poly, dtype=np.float32)
    if pts.shape != (4, 2):
        x1, y1 = int(np.min(pts[:, 0])), int(np.min(pts[:, 1]))
        x2, y2 = int(np.max(pts[:, 0])), int(np.max(pts[:, 1]))
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
        if x2 <= x1 or y2 <= y1:
            return np.zeros((1, 1, 3), dtype=np.uint8)
        return img[y1:y2, x1:x2]

    width_a = np.linalg.norm(pts[2] - pts[3])
    width_b = np.linalg.norm(pts[1] - pts[0])
    max_w = max(int(width_a), int(width_b), 1)

    height_a = np.linalg.norm(pts[1] - pts[2])
    height_b = np.linalg.norm(pts[0] - pts[3])
    max_h = max(int(height_a), int(height_b), 1)

    dst = np.array(
        [[0, 0], [max_w - 1, 0], [max_w - 1, max_h - 1], [0, max_h - 1]],
        dtype=np.float32,
    )
    matrix = cv2.getPerspectiveTransform(pts, dst)
    warped = cv2.warpPerspective(img, matrix, (max_w, max_h), flags=cv2.INTER_CUBIC)
    return warped


def load_vietocr(vietocr_dir: Path, config_path: Path, weights_path: Path, device: str):
    sys.path.insert(0, str(vietocr_dir))
    from tool.config import Cfg
    from tool.translate import build_model, process_input, translate

    cfg = Cfg.load_config_from_file(str(config_path), base_file=str(vietocr_dir / "config" / "base.yml"))
    cfg["device"] = device

    model, vocab = build_model(cfg)

    ckpt = torch.load(str(weights_path), map_location=device)
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        ckpt = ckpt["state_dict"]

    if isinstance(ckpt, dict):
        normalized = {}
        for k, v in ckpt.items():
            if k.startswith("module."):
                normalized[k[7:]] = v
            else:
                normalized[k] = v
        ckpt = normalized

    model.load_state_dict(ckpt, strict=False)
    model.eval()

    return cfg, model, vocab, process_input, translate


def main() -> None:
    args = parse_args()

    base_dir = Path(__file__).resolve().parent
    vietocr_dir = base_dir / "vietocr"

    config_path = Path(args.vietocr_config) if args.vietocr_config else vietocr_dir / "config" / "vgg-seq2seq.yml"
    weights_path = Path(args.vietocr_weights) if args.vietocr_weights else vietocr_dir / "weight" / "vgg_seq2seq.pth"

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    output_txt = Path(args.output_txt) if args.output_txt else input_path.with_name(input_path.stem + "_paddle_det_vietocr.txt")
    output_json = Path(args.output_json) if args.output_json else input_path.with_name(input_path.stem + "_paddle_det_vietocr.json")

    disable_mkldnn = bool(args.disable_mkldnn)

    cfg, vietocr_model, vocab, process_input, translate = load_vietocr(
        vietocr_dir=vietocr_dir,
        config_path=config_path,
        weights_path=weights_path,
        device=args.vietocr_device,
    )

    ocr = PaddleOCR(
        lang=args.paddle_lang,
        device=args.paddle_device,
        enable_mkldnn=not disable_mkldnn,
        enable_cinn=False,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    results = ocr.predict(str(input_path))

    txt_lines: list[str] = []
    json_pages: list[dict] = []

    for page_idx, page in enumerate(results, 1):
        doc_pre = page["doc_preprocessor_res"]
        img = doc_pre["output_img"]

        raw_polys = page.get("dt_polys", [])
        polys = [np.asarray(p, dtype=np.float32) for p in raw_polys]
        ordered_indices = order_poly_indices(polys)

        page_items: list[dict] = []
        txt_lines.append(f"=== PAGE {page_idx} ===")

        for det_idx in ordered_indices:
            poly = polys[det_idx]
            crop = crop_quad(img, poly)
            if crop.shape[0] < args.min_box_size or crop.shape[1] < args.min_box_size:
                continue

            pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
            tensor = process_input(
                pil_img,
                cfg["dataset"]["image_height"],
                cfg["dataset"]["image_min_width"],
                cfg["dataset"]["image_max_width"],
            ).to(args.vietocr_device)

            pred_ids = translate(tensor, vietocr_model)
            first_ids = pred_ids[0].tolist() if hasattr(pred_ids[0], "tolist") else list(pred_ids[0])
            text = vocab.decode(first_ids).strip()
            if not text:
                continue

            txt_lines.append(text)
            page_items.append(
                {
                    "text": text,
                    "poly": np.asarray(poly, dtype=float).tolist(),
                }
            )

        txt_lines.append("")
        json_pages.append({"page": page_idx, "items": page_items})

    output_txt.write_text("\n".join(txt_lines), encoding="utf-8")
    output_json.write_text(json.dumps(json_pages, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved TXT: {output_txt}")
    print(f"Saved JSON: {output_json}")
    print(f"Pages: {len(results)}")


if __name__ == "__main__":
    main()
