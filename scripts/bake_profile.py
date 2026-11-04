"""Offline, lossless baking of the existing lookup-filter animation.

The daily contribution refresh does not need Pillow, Playwright, or a GPU.
"""
from pathlib import Path
import argparse, base64, gzip, hashlib, io, json, tempfile
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'design'
W, H, COUNT, FPS = 1136, 1384, 120, 30

def packed(image):
    atlas = Image.new('RGB', (W, 624))
    atlas.paste(image.crop((0, 98, W, 515)), (0, 0))
    atlas.paste(image.crop((0, 1177, W, H)), (0, 417))
    return atlas

def capture(folder, channel):
    from playwright.sync_api import sync_playwright
    import compose_live_filters as live
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / 'assets').mkdir()
        live.ROOT, live.DESIGN = tmp, DESIGN
        live.compose()
        template = (tmp / 'assets/profile.svg').read_text(encoding='utf-8')
        with gzip.open(DESIGN / 'orbital-lookups.json.gz', 'rt') as f:
            original = json.load(f)['atlas']
        maps = Image.open(io.BytesIO(base64.b64decode(original.split(',')[1])))
        if maps.n_frames != COUNT:
            raise ValueError('Expected exactly 120 lookup frames')
        with sync_playwright() as p:
            options = {'headless': True, 'args': ['--force-color-profile=srgb']}
            if channel:
                options['channel'] = channel
            browser = p.chromium.launch(**options)
            try:
                page = browser.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
                for i in range(COUNT):
                    maps.seek(i)
                    buffer = io.BytesIO()
                    maps.convert('RGBA').save(buffer, format='PNG')
                    single = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()
                    svg = tmp / 'frame.svg'
                    svg.write_text(template.replace(original, single), encoding='utf-8')
                    page.goto(svg.as_uri(), wait_until='load')
                    page.screenshot(path=str(folder / f'baseline-{i:03}.png'), scale='css')
                    print(f'Captured {i + 1}/{COUNT}', flush=True)
                return browser.version
            finally:
                browser.close()

def verify(folder, target, engine):
    durations = [round((i + 1) * 1000 / FPS) - round(i * 1000 / FPS) for i in range(COUNT)]
    base = Image.open(folder / 'baseline-000.png').convert('RGB')
    with Image.open(target) as animation:
        if animation.n_frames != COUNT or animation.info.get('loop') != 0:
            raise ValueError('Frame count or looping changed')
        for i in range(COUNT):
            animation.seek(i)
            decoded = animation.convert('RGB')
            if animation.info.get('duration') != durations[i]:
                raise ValueError(f'Timing changed in frame {i}')
            composed = base.copy()
            composed.paste(decoded.crop((0, 0, W, 417)), (0, 98))
            composed.paste(decoded.crop((0, 417, W, 624)), (0, 1177))
            with Image.open(folder / f'baseline-{i:03}.png') as expected:
                if expected.size != (W, H) or ImageChops.difference(composed, expected.convert('RGB')).getbbox():
                    raise ValueError(f'Pixel mismatch in frame {i}')
    report = {'frames': COUNT, 'fps': FPS, 'seconds': 4, 'resolution': [W, H],
              'atlas_resolution': [W, 624], 'durations_ms': durations,
              'pixels_compared': COUNT * W * H, 'changed_pixels': 0,
              'source_sha256': hashlib.sha256((DESIGN / 'reference.png').read_bytes()).hexdigest(),
              'animation_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
              'capture_browser': engine, 'encoding': 'WebP lossless', 'bytes': target.stat().st_size}
    return report

def bake(folder, method, engine):
    frames = []
    for i in range(COUNT):
        with Image.open(folder / f'baseline-{i:03}.png') as im:
            frames.append(packed(im.convert('RGB')))
    durations = [round((i + 1) * 1000 / FPS) - round(i * 1000 / FPS) for i in range(COUNT)]
    target = DESIGN / 'baked-orbits.webp'
    pending = target.with_suffix('.pending.webp')
    frames[0].save(pending, format='WEBP', save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, lossless=True, quality=100,
                   method=method, exact=True, minimize_size=True)
    report = verify(folder, pending, engine)
    pending.replace(target)
    (DESIGN / 'bake-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel', default=None, help='Installed browser, e.g. chrome')
    parser.add_argument('--frames-dir', type=Path, help='Reuse existing native PNG captures')
    parser.add_argument('--method', type=int, choices=range(7), default=4)
    args = parser.parse_args()
    if args.frames_dir:
        bake(args.frames_dir, args.method, 'Chrome 156.0.8078.80 / existing native captures')
    else:
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            engine = capture(directory, args.channel)
            bake(directory, args.method, engine)
