#!/usr/bin/env python3






import argparse
import json
import logging
import sys
from pathlib import Path

from PIL import Image  # 

class ImageCipher:
    def __init__(self, key: int):
        self.key = key
        logging.debug(f"ImageCipher initialized with key={key}")

    def process(self, src: Path, dst: Path):
        try:
            img = Image.open(src)
        except Exception as e:
            logging.error(f"Cannot open source image: {e}")
            sys.exit(1)
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                r, g, b = pixels[x, y]
                pixels[x, y] = (r ^ self.key, g ^ self.key, b ^ self.key)
        try:
            img.save(dst)
            logging.info(f"Saved processed image to {dst}")
        except Exception as e:
            logging.error(f"Cannot save output image: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Simple Image XOR Cipher")
    parser.add_argument('--config', type=Path, help='JSON config file')
    parser.add_argument('--key', type=int, default=17, help='XOR key (0–255)')
    parser.add_argument('--input', type=Path, help='Source image path')
    parser.add_argument('--output', type=Path, help='Destination image path')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    lvl = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=lvl, format='%(levelname)s: %(message)s')

    cfg = {}
    if args.config:
        try:
            cfg = json.loads(args.config.read_text())
        except Exception as e:
            logging.error(f"Config load error: {e}")
            sys.exit(1)

    key = cfg.get('key', args.key)
    src = Path(cfg.get('input', args.input))
    dst = Path(cfg.get('output', args.output))
    if not src or not dst:
        logging.error("Must specify --input and --output (or via config)")
        sys.exit(1)

    ImageCipher(key).process(src, dst)

if __name__ == '__main__':
    main()
