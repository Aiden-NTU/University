"""Poster QR code for the hosted web twin.

    python src/make_qr.py https://<user>.github.io/<repo>/
"""
import sys

import qrcode
import qrcode.image.svg

import config as C

OUT = C.ROOT / "Poster"

if __name__ == "__main__":
    url = sys.argv[1]
    OUT.mkdir(exist_ok=True)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, border=4, box_size=40)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(OUT / "web_twin_qr.png")
    qr.make_image(image_factory=qrcode.image.svg.SvgPathImage).save(OUT / "web_twin_qr.svg")
    (OUT / "web_twin_url.txt").write_text(url + "\n")
    print("QR for", url, "->", OUT)
