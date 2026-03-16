#!/usr/bin/env python3
"""Build Markdown from PDFs using:
1) PPStructureV3 for layout analysis
2) PaddleOCR for text-region OCR
3) PaddleOCRVL for table-region recognition

Output is assembled in top-to-bottom reading order.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import tempfile
from pathlib import Path
from typing import Iterable

import cv2
import pandas as pd
import torch
from PIL import Image
from paddleocr import PPStructureV3, PaddleOCRVL

TEXT_LABELS = {
    "text",
    "paragraph_title",
    "title",
    "header",
    "footer",
    "reference",
    "caption",
    "footnote",
    "equation_text",
    "abstract",
    "content",
    "ocr",
}

TABLE_LABELS = {"table"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PPStructureV3 + VietOCR + PaddleOCRVL to Markdown")
    parser.add_argument("--input", required=True, help="Input PDF file or folder")
    parser.add_argument("--output_dir", default=None, help="Output folder for .md files")
    parser.add_argument("--lang", default="vi", help="Language for PPStructureV3")
    parser.add_argument("--device", default="cpu", help="Inference device, e.g. cpu, gpu:0")
    parser.add_argument("--disable_mkldnn", action="store_true", help="Disable MKLDNN")
    parser.add_argument("--page_header", action="store_true", help="Include page headers in markdown")
    parser.add_argument("--vietocr_device", default="cpu", help="VietOCR device, e.g. cpu, cuda:0")
    parser.add_argument("--vietocr_config", default=None, help="Path to VietOCR yml config")
    parser.add_argument("--vietocr_weights", default=None, help="Path to VietOCR .pth weights")
    return parser.parse_args()


def safe_bbox(block) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = map(int, block.bbox)
    return x1, y1, x2, y2


def sort_blocks_top_down(blocks: Iterable) -> list:
    return sorted(blocks, key=lambda b: (int(b.bbox[1]), int(b.bbox[0])))


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def html_table_to_markdown(html: str) -> str:
    html = (html or "").strip()
    if not html:
        return ""

    try:
        tables = pd.read_html(io.StringIO(html))
        if not tables:
            return html
        md_tables = [df.fillna("").to_markdown(index=False) for df in tables]
        return "\n\n".join(md_tables)
    except Exception:
        return html


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
            normalized[k[7:] if k.startswith("module.") else k] = v
        ckpt = normalized

    model.load_state_dict(ckpt, strict=False)
    model.eval()
    return cfg, model, vocab, process_input, translate


def ocr_text_block_with_vietocr(vietocr_bundle, crop_bgr) -> str:
    if crop_bgr is None or crop_bgr.size == 0:
        return ""

    cfg, model, vocab, process_input, translate = vietocr_bundle
    pil_img = Image.fromarray(cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB))
    tensor = process_input(
        pil_img,
        cfg["dataset"]["image_height"],
        cfg["dataset"]["image_min_width"],
        cfg["dataset"]["image_max_width"],
    ).to(cfg["device"])

    pred_ids = translate(tensor, model)
    if len(pred_ids) == 0:
        return ""

    first_ids = pred_ids[0].tolist() if hasattr(pred_ids[0], "tolist") else list(pred_ids[0])
    text = vocab.decode(first_ids)
    return normalize_text(text)


def ocr_table_block_with_vl(vl: PaddleOCRVL, crop_bgr) -> str:
    if crop_bgr is None or crop_bgr.size == 0:
        return ""

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
        cv2.imwrite(tmp.name, crop_bgr)
        res = vl.predict(tmp.name)

    if not res:
        return ""

    page = res[0]
    blocks = page.get("parsing_res_list") if isinstance(page, dict) else getattr(page, "parsing_res_list", None)

    if blocks:
        table_contents = []
        for b in blocks:
            if getattr(b, "label", "") == "table":
                md = html_table_to_markdown(str(getattr(b, "content", "")))
                if md:
                    table_contents.append(md)
        if table_contents:
            return "\n\n".join(table_contents)

    markdown_val = page.get("markdown") if isinstance(page, dict) else getattr(page, "markdown", None)
    if markdown_val:
        return normalize_text(str(markdown_val))

    return ""


def build_pipelines(
    lang: str,
    device: str,
    disable_mkldnn: bool,
    vietocr_device: str,
    vietocr_config: str | None,
    vietocr_weights: str | None,
):
    enable_mkldnn = not disable_mkldnn
    base_dir = Path(__file__).resolve().parent
    vietocr_dir = base_dir / "vietocr"
    config_path = Path(vietocr_config) if vietocr_config else vietocr_dir / "config" / "vgg-seq2seq.yml"
    weights_path = Path(vietocr_weights) if vietocr_weights else vietocr_dir / "weight" / "vgg_seq2seq.pth"

    layout_pipe = PPStructureV3(
        lang=lang,
        device=device,
        enable_mkldnn=enable_mkldnn,
        enable_cinn=False,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        use_table_recognition=False,
        use_formula_recognition=False,
        use_seal_recognition=False,
        use_chart_recognition=False,
        use_region_detection=False,
    )

    vietocr_bundle = load_vietocr(vietocr_dir, config_path, weights_path, vietocr_device)

    table_vl = PaddleOCRVL(
        device=device,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_layout_detection=True,
        use_ocr_for_image_block=True,
        use_queues=False,
    )

    return layout_pipe, vietocr_bundle, table_vl


def process_pdf(pdf_path: Path, out_md: Path, layout_pipe, vietocr_bundle, table_vl, page_header: bool):
    results = layout_pipe.predict(str(pdf_path))

    md_parts: list[str] = []

    for page_idx, page in enumerate(results, 1):
        if page_header:
            md_parts.append(f"## Page {page_idx}\n")

        page_img = page["doc_preprocessor_res"]["output_img"]
        blocks = sort_blocks_top_down(page.get("parsing_res_list", []))

        for block in blocks:
            label = getattr(block, "label", "")
            x1, y1, x2, y2 = safe_bbox(block)
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = max(x1 + 1, x2)
            y2 = max(y1 + 1, y2)
            crop = page_img[y1:y2, x1:x2]

            if label in TABLE_LABELS:
                table_md = ocr_table_block_with_vl(table_vl, crop)
                if table_md:
                    md_parts.append(table_md)
                    md_parts.append("")
                continue

            if label in TEXT_LABELS:
                text = ocr_text_block_with_vietocr(vietocr_bundle, crop)
                if text:
                    md_parts.append(text)
                    md_parts.append("")
                continue

        md_parts.append("")

    out_md.write_text("\n".join(md_parts).strip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    if input_path.is_file():
        pdf_files = [input_path]
        output_dir = Path(args.output_dir) if args.output_dir else input_path.parent / "outputs_ppstructurev3_md"
    else:
        pdf_files = sorted(input_path.rglob("*.pdf"))
        output_dir = Path(args.output_dir) if args.output_dir else input_path / "outputs_ppstructurev3_md"

    output_dir.mkdir(parents=True, exist_ok=True)

    layout_pipe, vietocr_bundle, table_vl = build_pipelines(
        args.lang,
        args.device,
        args.disable_mkldnn,
        args.vietocr_device,
        args.vietocr_config,
        args.vietocr_weights,
    )

    if not pdf_files:
        print(f"No PDF files found in: {input_path}")
        return

    print(f"Found {len(pdf_files)} PDF files")
    for i, pdf in enumerate(pdf_files, 1):
        out_md = output_dir / f"{pdf.stem}.md"
        print(f"[{i}/{len(pdf_files)}] Processing {pdf.name}")
        process_pdf(pdf, out_md, layout_pipe, vietocr_bundle, table_vl, args.page_header)
        print(f"  Saved: {out_md}")


if __name__ == "__main__":
    main()
