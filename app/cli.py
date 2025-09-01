from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from app.pdf_render import render_pdf_pages_to_images
from app.gpt_extractor import extract_page_structure_from_image
from app.excel_writer import write_pages_to_excel


def parse_pages_arg(pages: str, total_pages: int) -> List[int]:
    selected: List[int] = []
    for part in pages.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            try:
                start = int(start_s)
                end = int(end_s)
            except ValueError:
                continue
            if start > end:
                start, end = end, start
            selected.extend(list(range(start, end + 1)))
        else:
            try:
                selected.append(int(part))
            except ValueError:
                continue
    # Deduplicate and clamp
    selected = sorted({p for p in selected if 1 <= p <= total_pages})
    return selected


def main(argv: List[str] | None = None) -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Convert PDF pages to structured Excel using GPT Vision.")
    parser.add_argument("--pdf", required=True, help="Path to input PDF")
    parser.add_argument("--out", required=True, help="Path to output .xlsx file")
    parser.add_argument("--pages", default="", help="Pages to process, e.g. '1', '3-7', '1,3,5-8'")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model to use (vision capable)")
    parser.add_argument("--dpi", type=int, default=200, help="Render DPI (150-250 is typical)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists")

    args = parser.parse_args(argv)

    if not os.path.isfile(args.pdf):
        print(f"Error: PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    if os.path.exists(args.out) and not args.overwrite:
        print(f"Error: Output exists (use --overwrite): {args.out}", file=sys.stderr)
        return 2

    # Render once to know page count
    # We open the PDF quickly to get total pages via renderer implementation detail
    try:
        images_all = render_pdf_pages_to_images(args.pdf, dpi=args.dpi, page_numbers=None)
    except Exception as exc:  # noqa: BLE001
        print(f"Error rendering PDF: {exc}", file=sys.stderr)
        return 1

    total_pages = len(images_all)
    if total_pages == 0:
        print("No pages rendered from PDF.", file=sys.stderr)
        return 1

    if args.pages.strip():
        selected_pages = parse_pages_arg(args.pages.strip(), total_pages)
        if not selected_pages:
            print("No valid pages selected.", file=sys.stderr)
            return 1
        # Render only selected pages at requested DPI
        images = render_pdf_pages_to_images(args.pdf, dpi=args.dpi, page_numbers=selected_pages)
    else:
        images = images_all

    # Initialize OpenAI client (requires OPENAI_API_KEY environment variable)
    try:
        client = OpenAI()
        # Test auth by doing nothing; client lazy-loads
    except Exception as exc:  # noqa: BLE001
        print(f"Error initializing OpenAI client: {exc}", file=sys.stderr)
        return 1

    structured_by_page: Dict[int, dict] = {}
    for page_number in sorted(images.keys()):
        image_bytes = images[page_number]
        print(f"Processing page {page_number}...", flush=True)
        try:
            data = extract_page_structure_from_image(
                image_bytes=image_bytes,
                client=client,
                model=args.model,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  Failed to extract page {page_number}: {exc}", file=sys.stderr)
            continue
        structured_by_page[page_number] = data

    if not structured_by_page:
        print("No pages were successfully extracted.", file=sys.stderr)
        return 1

    try:
        write_pages_to_excel(structured_by_page, args.out)
    except Exception as exc:  # noqa: BLE001
        print(f"Error writing Excel: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote Excel to: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())