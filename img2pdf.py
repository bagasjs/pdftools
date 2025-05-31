import os
import argparse
import pymupdf as fitz
from PIL import Image

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="pdf2img",
            description="Split one or many pages of PDF into image")
    parser.add_argument("inputs", nargs="*", help="The image file")
    parser.add_argument("-o", "--output", nargs=1, help="The output file", default="result.pdf")

    args = parser.parse_args()

    if len(args.inputs) < 1:
        print("error: please provide at least 1 valid image inputs")
        exit(-1)

    with fitz.open() as doc:
        for i, input in enumerate(args.inputs):
            if not os.path.exists(input):
                print(f"error: {input} is not valid")
            image = Image.open(input).convert("RGB")
            img_bytes = image.tobytes("jpeg", "RGB")
            width, height = image.size
            rect = fitz.Rect(0, 0, width, height)
            page = doc.new_page(width=width, height=height)
            page.insert_image(rect, stream=img_bytes)

        if doc.page_count > 0:
            doc.save(args.output)
            print(f"Saved PDF to {args.output}")
        else:
            print("error: no pages created, PDF not saved")
