#!/usr/bin/env python3
"""TrustLeaf logo generator — leaf + shield, brand colors (SVG -> PNG)."""
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', 'pillow'])
    from PIL import Image, ImageDraw, ImageFont

S = 512
img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# rounded-square dark background
d.rounded_rectangle([16, 16, S-16, S-16], radius=96, fill=(16, 33, 26, 255))

# leaf shape (teal-green gradient feel)
GREEN = (52, 199, 123)
DARK_GREEN = (30, 140, 84)
d.polygon([(256, 90), (400, 190), (370, 360), (256, 430), (142, 360), (112, 190)],
          fill=GREEN)
d.polygon([(256, 130), (365, 210), (340, 340), (256, 392), (172, 340), (147, 210)],
          fill=(40, 170, 104))

# stem
d.line([(256, 200), (256, 380)], fill=(16, 33, 26), width=10)

# leaf veins
for y0 in range(230, 360, 40):
    d.line([(256, y0), (200, y0-30)], fill=(16, 33, 26), width=6)
    d.line([(256, y0), (312, y0-30)], fill=(16, 33, 26), width=6)

# "TL" text
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 88)
except Exception:
    font = ImageFont.load_default()
d.text((256, 300), 'TL', font=font, fill=(255, 255, 255), anchor='mm')

img.save('/home/ubuntu/trustleaf/docs/trustleaf_logo.png')
img.resize((256, 256)).save('/home/ubuntu/trustleaf/docs/trustleaf_logo_256.png')
print('logo saved: /home/ubuntu/trustleaf/docs/trustleaf_logo.png')
