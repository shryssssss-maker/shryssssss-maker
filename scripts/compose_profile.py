"""Compose small static profile sections; the lossless orbit asset is immutable."""
from pathlib import Path
import argparse,base64,json,re
import xml.etree.ElementTree as ET
from profile_data import refresh,activity

ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/'design'
NS='{http://www.w3.org/2000/svg}'

def bitmap(cache,existing,ident):
    path=DESIGN/cache
    if path.exists():
        return 'data:image/webp;base64,'+base64.b64encode(path.read_bytes()).decode()
    image=ET.parse(ROOT/'assets'/existing).find(f'.//{NS}image[@id="{ident}"]')
    if image is None:raise RuntimeError('Run bake_profile.py once before composing')
    return image.attrib['href']

def write_changed(path,text):
    if not path.exists() or path.read_text(encoding='utf-8')!=text:
        path.write_text(text,encoding='utf-8')

def compose():
    scene=json.loads((DESIGN/'scene.json').read_text())
    w,h,split=scene['width'],scene['height'],scene['split_y']
    for key in ['animation','poster']:
        path=(ROOT/scene[key]).resolve()
        if not path.is_relative_to((ROOT/'assets').resolve()) or not path.is_file():
            raise RuntimeError(f'Missing scene asset: {key}')
    full=bitmap('reference.webp','profile.svg','reference-full')
    body=bitmap('body-reference.webp','profile-body.svg','reference-body')
    title='Shreyas Singh — developer, builder and student'
    grid=activity()
    full_svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title"><title id="title">{title}</title><image id="reference-full" width="{w}" height="{h}" href="{full}"/>{grid}</svg>'
    body_svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h-split}" viewBox="0 {split} {w} {h-split}" role="img" aria-labelledby="title"><title id="title">Featured projects, tech stack, contribution activity and particle hills</title><image id="reference-body" y="{split}" width="{w}" height="{h-split}" href="{body}"/>{grid}</svg>'
    for name,text in [('profile.svg',full_svg),('profile-static.svg',full_svg),('profile-body.svg',body_svg)]:
        write_changed(ROOT/'assets'/name,text+'\n');ET.parse(ROOT/'assets'/name)
    start='<!-- profile-artwork:start -->';end='<!-- profile-artwork:end -->'
    alt='Shreyas Singh — building where systems, AI and real-world impact intersect. Particles orbit a still planet.'
    artwork=f'{start}\n<p><picture><source media="(prefers-reduced-motion: reduce)" srcset="{scene["poster"]}"><img src="{scene["animation"]}" width="100%" align="top" alt="{alt}"></picture><img src="assets/profile-body.svg" width="100%" align="top" alt="B.Tech ECE at Manipal University Jaipur, 2025–2029. JanSamadhan, NyayaAI, ARTERY and Cache Simulator. Tech stack, actual GitHub activity, and the original still hills and sun."></p>\n{end}'
    readme=ROOT/'README.md';content=readme.read_text(encoding='utf-8')
    if start in content:
        content=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:artwork,content,count=1,flags=re.S)
    else:
        content=artwork+'\n\n'+content[content.index('<details>'):]
    write_changed(readme,content)
    print(f'Lossless orbit: {(ROOT/scene["animation"]).stat().st_size:,} bytes; static body: {(ROOT/"assets/profile-body.svg").stat().st_size:,} bytes; no runtime filters')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--refresh-activity',action='store_true');args=p.parse_args()
    if args.refresh_activity:refresh()
    compose()
