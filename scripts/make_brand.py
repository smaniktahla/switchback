"""Generate logo/favicon assets from assets/switchback-logo-source.webp -> app/static/ (+ assets/social-preview.png)."""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

SRC, OUT = Path("assets/switchback-logo-source.webp"), Path("app/static")
im = Image.open(SRC).convert("RGB"); a = np.array(im).astype(int)
BG = a[5, 5]


def transparent(img, tol=26):
    """Make the page background (reachable from the border) transparent; keeps white shapes inside the logo."""
    arr = np.array(img.convert("RGB")).astype(int)
    near = np.abs(arr - BG).sum(2) <= tol
    h, w = near.shape; seen = np.zeros_like(near); q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not seen[y, x]: seen[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True; q.append((ny, nx))
    alpha = np.where(seen, 0, 255).astype(np.uint8)
    out = Image.fromarray(np.dstack([arr.astype(np.uint8), alpha]), "RGBA")
    return out


def square(img, size, pad=0.06, bg=None):
    s = max(img.size); canvas = Image.new("RGBA", (s, s), bg or (0, 0, 0, 0))
    canvas.paste(img, ((s - img.width) // 2, (s - img.height) // 2), img)
    p = int(s * pad); big = Image.new("RGBA", (s + 2 * p, s + 2 * p), bg or (0, 0, 0, 0)); big.paste(canvas, (p, p), canvas)
    return big.resize((size, size), Image.LANCZOS)


mark = im.crop((350, 200, 905, 852)); mark_t = transparent(mark)
full_t = transparent(im.crop((90, 195, 1170, 1045)))
mark_t.save(OUT / "logo-mark.png"); full_t.resize((int(full_t.width * 0.55), int(full_t.height * 0.55)), Image.LANCZOS).save(OUT / "logo.png")
for n in (16, 32, 48, 180, 192, 512):
    ic = square(mark_t, n, pad=0.04, bg=(252, 251, 248, 255))   # light backing so the dark road stays visible on dark browser tabs
    if n in (32, 192, 512): ic.save(OUT / f"icon-{n}.png")
    if n == 180: ic.convert("RGB").save(OUT / "apple-touch-icon.png")
square(mark_t, 256, pad=0.04, bg=(252, 251, 248, 255)).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
# GitHub social preview 1280x640 (upload manually in repo Settings -> Social preview)
bgc = tuple(int(v) for v in BG); card = Image.new("RGB", (1280, 640), bgc)
lock = im.crop((90, 195, 1170, 1045)); lock = lock.resize((int(lock.width * 560 / lock.height), 560), Image.LANCZOS)
card.paste(lock, ((1280 - lock.width) // 2, 40)); card.save("assets/social-preview.png")
print("ok")
