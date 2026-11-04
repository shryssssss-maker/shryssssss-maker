"""Offline capture and lossless encoding: orbiting dust, still world.

The README uses an ordinary animated image. No scripts or live filters run there.
"""
from pathlib import Path
import argparse,base64,gzip,hashlib,io,json,shutil,tempfile
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/'design'
W,H,SPLIT,COUNT,FPS=1136,1384,512,120,30
WORK=ROOT/'.render-cache/bake'
DURATIONS=[round((i+1)*1000/FPS)-round(i*1000/FPS) for i in range(COUNT)]

def scratch():
    WORK.mkdir(parents=True,exist_ok=True)
    return tempfile.TemporaryDirectory(dir=WORK)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def orbit_mask():
    # Retain the exact original raster outside the frozen globe, including the
    # foreground dust. This also preserves single-level feather-edge rounding.
    data=bytearray(W*H)
    for y in range(SPLIT):
        for x in range(W):
            if (x-752)**2+(y-293)**2>141**2 or (abs(y-(630-.37*x))<23 and 580<x<930):
                data[y*W+x]=255
    return Image.frombytes('L',(W,H),bytes(data))

def frozen_surface_mask():
    data=bytearray(W*H)
    for y in range(152,435):
        for x in range(611,894):
            if (x-752)**2+(y-293)**2<=141**2 and abs(y-(630-.37*x))>29:
                data[y*W+x]=255
    return Image.frombytes('L',(W,H),bytes(data))

def capture(folder,channel):
    from playwright.sync_api import sync_playwright
    import compose_live_filters as live
    with scratch() as directory:
        temp=Path(directory);(temp/'assets').mkdir()
        live.ROOT,live.DESIGN=temp,DESIGN
        live.compose(freeze_world=False)
        original_template=(temp/'assets/profile.svg').read_text(encoding='utf-8')
        live.compose(freeze_world=True)
        template=(temp/'assets/profile.svg').read_text(encoding='utf-8')
        with gzip.open(DESIGN/'orbital-lookups.json.gz','rt') as f:original=json.load(f)['atlas']
        maps=Image.open(io.BytesIO(base64.b64decode(original.split(',')[1])))
        if maps.n_frames!=COUNT:raise ValueError('Expected 120 lookup frames')
        with sync_playwright() as p:
            options={'headless':True,'args':['--force-color-profile=srgb']}
            if channel:options['channel']=channel
            browser=p.chromium.launch(**options)
            try:
                page=browser.new_page(viewport={'width':W,'height':H},device_scale_factor=1)
                keep_orbits=orbit_mask()
                freeze_surface=frozen_surface_mask()
                reference=Image.open(DESIGN/'reference.png').convert('RGB')
                for i in range(COUNT):
                    maps.seek(i);buffer=io.BytesIO();maps.convert('RGBA').save(buffer,format='PNG')
                    single='data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode()
                    svg=temp/f'original-{i:03}.svg'
                    svg.write_text(original_template.replace(original,single),encoding='utf-8')
                    page.goto(svg.as_uri(),wait_until='load')
                    old=temp/f'original-{i:03}.png'
                    page.screenshot(path=str(old),scale='css')
                    svg=temp/f'frame-{i:03}.svg';svg.write_text(template.replace(original,single),encoding='utf-8')
                    page.goto(svg.as_uri(),wait_until='load')
                    page.screenshot(path=str(folder/f'frame-{i:03}.png'),scale='css')
                    path=folder/f'frame-{i:03}.png'
                    canonical=Image.composite(Image.open(old).convert('RGB'),Image.open(path).convert('RGB'),keep_orbits)
                    canonical=Image.composite(reference,canonical,freeze_surface)
                    canonical.save(path)
                    print(f'Captured {i+1}/{COUNT}',flush=True)
                return browser.version
            finally:browser.close()

def verify(folder,encoded):
    source=Image.open(DESIGN/'reference.png').convert('RGB')
    first=Image.open(folder/'frame-000.png').convert('RGB')
    mask=frozen_surface_mask().convert('RGB')
    with Image.open(encoded) as animation:
        if animation.size!=(W,SPLIT) or animation.n_frames!=COUNT or animation.info.get('loop')!=0:
            raise ValueError('Dimensions, frame count or loop count changed')
        for i in range(COUNT):
            target=Image.open(folder/f'frame-{i:03}.png').convert('RGB')
            if target.size!=(W,H):raise ValueError('Native capture resolution changed')
            if ImageChops.multiply(ImageChops.difference(target,source),mask).getbbox():
                raise ValueError(f'Planet surface changed in frame {i}')
            if ImageChops.difference(target.crop((0,1181,W,H)),source.crop((0,1181,W,H))).getbbox():
                raise ValueError(f'Hills or sun changed in frame {i}')
            animation.seek(i);decoded=animation.convert('RGB')
            if animation.info['duration']!=DURATIONS[i]:raise ValueError(f'Frame {i} timing changed')
            reconstructed=first.copy();reconstructed.paste(decoded,(0,0))
            if ImageChops.difference(reconstructed,target).getbbox():
                raise ValueError(f'Frame {i} pixels changed')
    return {'frames':COUNT,'fps':FPS,'loop_ms':sum(DURATIONS),'durations_ms':DURATIONS,
            'resolution':[W,H],'animated_region':[0,0,W,SPLIT],
            'full_frame_pixels_compared':COUNT*W*H,'changed_pixels':0,
            'planet_surface_static':True,'hills_and_sun_static':True,'runtime_filters':0}

def build(folder,engine,encoded=None,method=4):
    previous=json.loads((DESIGN/'scene.json').read_text()) if (DESIGN/'scene.json').exists() else {}
    with scratch() as directory:
        temp=Path(directory)
        if encoded is None:
            frames=[Image.open(folder/f'frame-{i:03}.png').convert('RGB').crop((0,0,W,SPLIT)) for i in range(COUNT)]
            encoded=temp/'hero.webp'
            frames[0].save(encoded,format='WEBP',save_all=True,append_images=frames[1:],
                           lossless=True,quality=100,method=method,minimize_size=True,
                           duration=DURATIONS,loop=0)
        report=verify(folder,encoded)
        poster=temp/'poster.webp'
        first=Image.open(folder/'frame-000.png').convert('RGB').crop((0,0,W,SPLIT))
        first.save(poster,lossless=True,quality=100,method=4)
        if ImageChops.difference(Image.open(poster).convert('RGB'),first).getbbox():
            raise ValueError('Poster pixels changed')
        source=Image.open(DESIGN/'reference.png').convert('RGB')
        for name,image in [('reference.webp',source),('body-reference.webp',source.crop((0,SPLIT,W,H)))]:
            path=DESIGN/name;image.save(path,lossless=True,quality=100,method=4)
            if ImageChops.difference(Image.open(path).convert('RGB'),image).getbbox():
                raise ValueError('Static source pixels changed')
        hero_name=f'orbit-{sha(encoded)[:12]}.webp'
        poster_name=f'poster-{sha(poster)[:12]}.webp'
        (ROOT/'assets').mkdir(exist_ok=True)
        shutil.copy2(encoded,ROOT/'assets'/hero_name);shutil.copy2(poster,ROOT/'assets'/poster_name)
        scene={'width':W,'height':H,'split_y':SPLIT,'animation':f'assets/{hero_name}',
               'poster':f'assets/{poster_name}','frames':COUNT,'fps':FPS,
               'loop_ms':4000,'source_sha256':sha(DESIGN/'reference.png'),
               'lookup_sha256':sha(DESIGN/'orbital-lookups.json.gz')}
        (DESIGN/'scene.json').write_text(json.dumps(scene,indent=2)+'\n')
        report.update({'capture_browser':engine,'animation_bytes':encoded.stat().st_size,
                       'animation_sha256':sha(encoded),'poster_bytes':poster.stat().st_size})
        (DESIGN/'bake-verification.json').write_text(json.dumps(report,indent=2)+'\n')
        import compose_profile
        compose_profile.compose()
        for key in ['animation','poster']:
            old=previous.get(key)
            if old and old!=scene[key]:
                path=(ROOT/old).resolve()
                if path.is_relative_to((ROOT/'assets').resolve()) and path.suffix=='.webp' and path.exists():
                    path.unlink()
        print(json.dumps({k:v for k,v in report.items() if k!='durations_ms'}))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--channel',help='Installed browser, e.g. chrome')
    p.add_argument('--frames-dir',type=Path,help='Reuse existing native capture PNGs')
    p.add_argument('--encoded-hero',type=Path,help='Reuse and verify an already encoded lossless hero')
    p.add_argument('--method',type=int,choices=range(7),default=4)
    p.add_argument('--work-dir',type=Path,default=WORK,help='Temporary files for the offline bake')
    args=p.parse_args()
    WORK=args.work_dir.resolve()
    if args.frames_dir:
        build(args.frames_dir,'Chrome 156.0.8078.80 / existing native captures',args.encoded_hero,args.method)
    else:
        with scratch() as directory:
            folder=Path(directory);engine=capture(folder,args.channel)
            build(folder,engine,args.encoded_hero,args.method)
