#!/usr/bin/env python3
"""Build TrustLeaf demo video (YouTube-style, ~60s) via PIL frames + ffmpeg.
Scenes:
1. Intro: logo + title + tagline
2. Problem: centralized vendor scores
3. Solution: live web + OFAC + AI jury
4. Code: contract highlights (real code)
5. Deploy proof: real tx hash ACCEPTED
6. CTA: GitHub link
Dark theme, green TrustLeaf accent."""
from PIL import Image, ImageDraw, ImageFont
import subprocess, os

W, H = 1920, 1080
FPS = 30
OUT = '/home/ubuntu/trustleaf/docs'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

def font(size):
    try: return ImageFont.truetype(FONT, size)
    except: return ImageFont.load_default()

def mono(size):
    try: return ImageFont.truetype(MONO, size)
    except: return ImageFont.load_default()

BG = (12, 24, 18)
GREEN = (52, 199, 123)
WHITE = (240, 245, 240)
GRAY = (140, 155, 148)
RED = (235, 90, 90)
BLUE = (90, 160, 235)

def base_frame():
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    # subtle grid
    for x in range(0, W, 80):
        d.line([(x, 0), (x, H)], fill=(16, 30, 22))
    for y in range(0, H, 80):
        d.line([(0, y), (W, y)], fill=(16, 30, 22))
    return img, d

def logo(d, x, y, scale=1.0):
    s = int(120 * scale)
    d.polygon([(x, y - s), (x + s*0.75, y - s*0.25), (x + s*0.6, y + s*0.55),
               (x, y + s), (x - s*0.6, y + s*0.55), (x - s*0.75, y - s*0.25)],
              fill=GREEN)
    d.line([(x, y - s*0.4), (x, y + s*0.6)], fill=BG, width=int(8*scale))
    d.text((x, y + s*0.05), 'TL', font=font(int(44*scale)), fill=WHITE, anchor='mm')

def scene1():  # 5s intro
    img, d = base_frame()
    logo(d, 260, 480, 2.2)
    d.text((420, 420), 'TrustLeaf', font=font(130), fill=WHITE)
    d.text((424, 560), 'Verifiable Supplier Trust Scores', font=font(48), fill=GREEN)
    d.text((424, 640), 'An Intelligent Contract on GenLayer', font=font(36), fill=GRAY)
    d.text((W//2, 980), 'github.com/Azet17/trustleaf', font=mono(30), fill=GRAY, anchor='mm')
    return img

def scene2():  # 10s problem
    img, d = base_frame()
    d.text((120, 100), 'THE TRUST PROBLEM', font=font(72), fill=RED)
    rows = [
        ('Alibaba-style vendor scores', 'controlled by ONE platform'),
        ('"Verified supplier" badges', 'purchasable, stale, unaudited'),
        ('International buyers', 'wire $50K on blind trust'),
        ('Deterministic smart contracts', 'CANNOT judge live web evidence'),
    ]
    y = 260
    for a, b in rows:
        d.rounded_rectangle([120, y, W-120, y+130], radius=20, fill=(20, 36, 28))
        d.text((160, y+28), a, font=font(42), fill=WHITE)
        d.text((160, y+78), b, font=font(36), fill=RED)
        y += 160
    return img

def scene3():  # 12s solution
    img, d = base_frame()
    d.text((120, 100), 'THE SOLUTION', font=font(72), fill=GREEN)
    d.text((120, 200), 'Score suppliers 0-100 ON-CHAIN from live evidence', font=font(40), fill=WHITE)
    steps = [
        ('1', 'Render supplier website LIVE', 'gl.nondet.web.render'),
        ('2', 'Screen OFAC sanctions list', 'authoritative source'),
        ('3', 'AI validator jury judges signals', 'Equivalence Principle'),
        ('4', 'Score + rationale stored on-chain', 'auditable forever'),
        ('5', 'Appeal with evidence -> re-scored', 'fresh live evaluation'),
    ]
    y = 300
    for n, t, sub in steps:
        d.ellipse([140, y, 200, y+60], fill=GREEN)
        d.text((170, y+30), n, font=font(38), fill=BG, anchor='mm')
        d.text((230, y+2), t, font=font(40), fill=WHITE)
        d.text((230, y+42), sub, font=mono(28), fill=GREEN)
        y += 118
    return img

def scene4():  # 15s code
    img, d = base_frame()
    d.text((120, 80), 'THE CONTRACT  —  supplier_trust.py', font=font(56), fill=WHITE)
    d.rounded_rectangle([120, 190, W-120, H-160], radius=24, fill=(18, 32, 25))
    code = [
        ('class SupplierTrustScore(gl.Contract):', WHITE),
        ('    supplier_counter: bigint', GREEN),
        ('    suppliers: TreeMap[str, str]', GREEN),
        ('', WHITE),
        ('    @gl.public.write', BLUE),
        ('    def register_supplier(self, name: str,', WHITE),
        ('                         website: str, country: str) -> int:', WHITE),
        ('        def fetch_and_judge() -> str:', WHITE),
        ('            site = gl.nondet.web.render(website, mode="text")', GREEN),
        ('            sanctions = gl.nondet.web.render(ofac_url, mode="text")', GREEN),
        ('            # ... trust signals computed from LIVE evidence ...', GRAY),
        ('        record = gl.eq_principle.strict_eq(fetch_and_judge)', BLUE),
        ('        self.suppliers[str(sid)] = record', WHITE),
        ('', WHITE),
        ('    # score 0-100  |  sanctions hit = auto-zero', GRAY),
        ('    # appeal with new evidence -> fresh re-evaluation', GRAY),
    ]
    y = 230
    for line, color in code:
        d.text((160, y), line, font=mono(30), fill=color)
        y += 46
    return img

def scene5():  # 12s deploy proof
    img, d = base_frame()
    d.text((120, 100), 'DEPLOYED — LIVE ON GENLAYER', font=font(64), fill=GREEN)
    d.rounded_rectangle([120, 230, W-120, 420], radius=24, fill=(18, 32, 25))
    d.text((160, 265), 'TRANSACTION', font=font(34), fill=GRAY)
    d.text((160, 320), '0x114ce1ad298639d5eb9621dd', font=mono(42), fill=WHITE)
    d.text((160, 370), '9294994d594d73b2', font=mono(42), fill=WHITE)
    d.rounded_rectangle([120, 460, W-120, 600], radius=24, fill=(18, 32, 25))
    d.text((160, 495), 'STATUS', font=font(34), fill=GRAY)
    d.ellipse([W-320, 490, W-260, 550], fill=GREEN)
    d.text((160, 540), 'ACCEPTED — validator consensus reached', font=font(40), fill=GREEN)
    d.text((120, 680), 'Deployed via GenLayer Studio  ·  testnet', font=font(34), fill=GRAY)
    d.text((120, 740), 'Frontend genuinely calls the contract (genlayer-js)', font=font(34), fill=GRAY)
    return img

def scene6():  # 6s CTA
    img, d = base_frame()
    logo(d, W//2, 340, 2.0)
    d.text((W//2, 560), 'TrustLeaf', font=font(96), fill=WHITE, anchor='mm')
    d.text((W//2, 660), 'Trust infrastructure for agentic commerce', font=font(40), fill=GREEN, anchor='mm')
    d.rounded_rectangle([W//2-500, 760, W//2+500, 860], radius=24, fill=(20, 36, 28))
    d.text((W//2, 810), 'github.com/Azet17/trustleaf', font=mono(44), fill=WHITE, anchor='mm')
    return img

# Build scenes with durations (seconds)
scenes = [(scene1, 5), (scene2, 9), (scene3, 11), (scene4, 14), (scene5, 12), (scene6, 6)]
frames_dir = '/tmp/tl_frames'
os.makedirs(frames_dir, exist_ok=True)

n = 0
for fn, dur in scenes:
    img = fn()
    for _ in range(dur * FPS):
        img.save(f'{frames_dir}/f{n:05d}.png')
        n += 1

print(f'frames :: {n} ({n/FPS:.0f}s)')

# ffmpeg: frames -> mp4 (h264, yuv420p, faststart for web/telegram)
subprocess.run(['ffmpeg', '-y', '-framerate', str(FPS), '-i', f'{frames_dir}/f%05d.png',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium',
                '-movflags', '+faststart', f'{OUT}/trustleaf_demo.mp4'],
               check=True, capture_output=True)
print('video ::', f'{OUT}/trustleaf_demo.mp4', os.path.getsize(f'{OUT}/trustleaf_demo.mp4'), 'bytes')
