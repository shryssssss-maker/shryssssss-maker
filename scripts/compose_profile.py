"""Compose the profile using cached lossless frames; no runtime SVG filters."""
from pathlib import Path
import argparse, base64
import xml.etree.ElementTree as ET
from profile_data import refresh, activity

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / 'design'

def uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()

def compose():
    source = uri(DESIGN / 'reference.png', 'image/png')
    cached = DESIGN / 'baked-orbits.webp'
    if cached.exists():
        animation = uri(cached, 'image/webp')
    else:
        # The checked-in SVG already contains the lossless animation. Reuse it
        # for daily refreshes instead of storing a second 30 MB binary in Git.
        tree = ET.parse(ROOT / 'assets/profile.svg')
        image = tree.find('.//{http://www.w3.org/2000/svg}image[@id="baked"]')
        if image is None:
            raise RuntimeError('Run bake_profile.py once before composing')
        animation = image.attrib['href']
    title = 'Shreyas Singh — developer, builder and student'
    output = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1136" height="1384" viewBox="0 0 1136 1384" role="img" aria-labelledby="title desc">
<title id="title">{title}</title>
<desc id="desc">The original particle planet, orbital dust, hills and sun. All 120 original frames are pre-rendered losslessly at 30 fps, with no live displacement filters. Featured projects, tech stack and actual public GitHub contribution activity. Project and contact links follow this image.</desc>
<defs>
<image id="baked" width="1136" height="624" href="{animation}"/>
<clipPath id="hero"><rect y="98" width="1136" height="417"/></clipPath>
<clipPath id="hills"><rect y="1177" width="1136" height="207"/></clipPath>
</defs>
<image width="1136" height="1384" href="{source}"/>
<g clip-path="url(#hero)"><use href="#baked" transform="translate(0 98)"/></g>
<g clip-path="url(#hills)"><use href="#baked" transform="translate(0 760)"/></g>
{activity()}
</svg>'''
    target = ROOT / 'assets/profile.svg'
    target.write_text(output, encoding='utf-8')
    ET.parse(target)
    static = f'<svg xmlns="http://www.w3.org/2000/svg" width="1136" height="1384" viewBox="0 0 1136 1384" role="img" aria-labelledby="title"><title id="title">{title}</title><image width="1136" height="1384" href="{source}"/>{activity()}</svg>'
    (ROOT / 'assets/profile-static.svg').write_text(static, encoding='utf-8')
    print(f'Lossless profile: {target.stat().st_size / 1024 / 1024:.2f} MiB; zero live filters')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh-activity', action='store_true')
    args = parser.parse_args()
    if args.refresh_activity:
        refresh()
    compose()
