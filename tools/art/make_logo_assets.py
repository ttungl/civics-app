#!/usr/bin/env python3
"""Build every logo asset from tools/art/logo-source.png.

Run from the repo root:  python3 tools/art/make_logo_assets.py
(og-image.png is rendered separately from tools/art/og.html.)
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
out = lambda name: os.path.join(ROOT, name)

src = np.array(Image.open(os.path.join(HERE, 'logo-source.png')).convert('RGBA'))
src[..., 3] = np.where(src[..., 3] < 12, 0, src[..., 3])      # drop faint edge haze
logo = Image.fromarray(src)

# The source stacks three bands: emblem, wordmark, tagline.
BANDS = {'full': (246, 966), 'mark': (246, 722), 'word': (758, 896)}
def crop(img, band):
    y0, y1 = BANDS[band]
    a = np.array(img)[y0:y1, :, 3]
    ys, xs = np.where(a > 0)
    return img.crop((xs.min(), y0 + ys.min(), xs.max() + 1, y0 + ys.max() + 1))

def on_white(img):
    c = Image.new('RGBA', img.size, (255, 255, 255, 255)); c.alpha_composite(img); return c.convert('RGB')

def width(img, w):
    return img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)

def height(img, h):
    return img.resize((round(img.width * h / img.height), h), Image.LANCZOS)

def recolor_navy(img, rgb=(111, 155, 255)):
    """Dark-mode variant: navy -> bright blue; red, white, and greys unchanged."""
    a = np.array(img).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    navy = (b > r + 25) & (r < 110) & (g < 130)
    for i, v in enumerate(rgb):
        a[..., i] = np.where(navy, v, a[..., i])
    return Image.fromarray(a.astype('uint8'), 'RGBA')

def fill_emblem_holes(img, emblem_height):
    """Paint white behind see-through areas enclosed by the emblem (Q/A letters, the document page),
    so they look white on any background. Letter counters in the wordmark below stay transparent."""
    from PIL import ImageFilter
    from scipy import ndimage
    clear = np.array(img)[..., 3] < 128
    labels, _ = ndimage.label(clear)                              # connected see-through regions
    edge = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    holes = clear & ~np.isin(labels, edge)                        # regions not touching the border
    holes[emblem_height:, :] = False
    mask = Image.fromarray((holes * 255).astype('uint8'), 'L').filter(ImageFilter.MaxFilter(5))
    white = Image.new('RGBA', img.size, (255, 255, 255, 0))
    white.putalpha(mask)
    white.alpha_composite(img)
    return white

full, mark, word = crop(logo, 'full'), crop(logo, 'mark'), crop(logo, 'word')
EMBLEM_H = mark.height  # emblem occupies the top of the full crop

# On white tiles (Home brand row, sidebar, link preview): flattened, no transparency.
f = width(on_white(full), 720); f.save(out('logo.png'), optimize=True); f.save(out('logo.webp'), quality=88, method=6)
height(on_white(mark), 200).save(out('logo-mark.webp'), quality=88, method=6)
height(on_white(word), 72).save(out('logo-wordmark.webp'), quality=88, method=6)

# Transparent (About page): light and dark variants.
width(fill_emblem_holes(full, EMBLEM_H), 640).save(out('logo-clear.webp'), quality=86, method=6, exact=True)
width(fill_emblem_holes(recolor_navy(full), EMBLEM_H), 640).save(out('logo-clear-dark.webp'), quality=86, method=6, exact=True)

# App icons: emblem centered on white.
def icon(size, pad, name):
    c = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    inner = int(size * (1 - 2 * pad)); s = inner / max(mark.size)
    m = mark.resize((round(mark.width * s), round(mark.height * s)), Image.LANCZOS)
    c.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
    c.convert('RGB').save(out(name), optimize=True)
icon(180, .10, 'apple-touch-icon.png'); icon(192, .10, 'icon-192.png'); icon(512, .10, 'icon-512.png')
icon(512, .20, 'icon-maskable-512.png'); icon(64, .04, 'favicon.png')

for n in ['logo.webp', 'logo-mark.webp', 'logo-wordmark.webp', 'logo-clear.webp', 'logo-clear-dark.webp', 'apple-touch-icon.png', 'favicon.png']:
    print(f'{n:22} {Image.open(out(n)).size}  {os.path.getsize(out(n)) // 1024} KB')
