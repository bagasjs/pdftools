#!/usr/bin/python
import os
import argparse
import pymupdf as fitz
from PIL import Image
from io import BytesIO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="pdfcompress",
            description="Compress a PDF")
    parser.add_argument("-i", "--input",  nargs=1, help="The PDF file")
    parser.add_argument("-o", "--output", nargs=1, help="The output file path")

    args = parser.parse_args()

    if len(args.input) < 1:
        print("error: please provide a valid PDF input")
        exit(-1)

    if len(args.output) < 1:
        print("error: please provide a valid output file path")
        exit(-1)

    input = args.input[0]
    if not os.path.exists(input):
        print("error: please provide a valid PDF input")
        exit(-1)

    with fitz.open(input) as doc:
        doc.save(args.output[0], garbage=4, deflate=True)

