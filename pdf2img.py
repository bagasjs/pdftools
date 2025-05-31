#!/usr/bin/python
import os
import argparse
import pymupdf as fitz
from PIL import Image
from io import BytesIO

def parse_selection(selection: str, end: int) -> list[int]:
    selection = selection.strip()
    if not selection:
        return []
    if selection.lower() == "all":
        return list(range(0, end))

    parts = [ part.strip() for part in selection.split(",") ]
    result = []
    for part in parts:
        if "-" in part:
            range_parts = part.split("-")
            if len(range_parts) != 2:
                raise ValueError(f"Invalid range {part}")
            rbegin = int(range_parts[0])
            rend   = int(range_parts[1]) if len(range_parts[1]) > 0 else end
            if rbegin > rend:
                rbegin, rend = rend, rbegin
            if rend > end:
                rend = end
            if rbegin > rend:
                continue
            result.extend(list(range(rbegin-1, rend)))
        else:
            result.append(int(part)-1)
    return sorted(list(set(result)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="pdf2img",
            description="Split one or many pages of PDF into image")
    parser.add_argument("-i", "--input", nargs=1, help="The PDF file")
    parser.add_argument("-d", "--dir", nargs=1, help="The output directory")
    parser.add_argument("-f", "--format", nargs=1, help="The output format could be either png, jpg", default=".png")
    parser.add_argument("-s", "--selection", nargs=1, help="Selection i.e. \"1-3,5,7-10\"", default="all")

    args = parser.parse_args()

    if len(args.input) < 1:
        print("error: please provide a valid PDF input")
        exit(-1)
    input = args.input[0]
    if not os.path.exists(input):
        print("error: please provide a valid PDF input")
        exit(-1)

    selection = args.selection[0]
    format = args.format

    dir = os.path.splitext(os.path.basename(input))[0]
    if args.dir:
        dir = args.dir[0]

    if os.path.isdir(dir):
        print(f"error: the provided directory {dir} is already exists. Please remove it first.")
        exit(-1)
    os.mkdir(dir)

    with fitz.Document(input) as doc:
        selected = parse_selection(selection, end=doc.page_count)
        for i in selected:
            page = doc.load_page(i)
            image = Image.open(BytesIO(page.get_pixmap(dpi=300).tobytes()))
            image.save(os.path.join(dir, f"{i}{format}"))

