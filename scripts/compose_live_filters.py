"""Compose the exact reference with GPU-generated orbital lookup animation."""
from pathlib import Path
import base64,gzip,json,argparse
import xml.etree.ElementTree as ET
from profile_data import refresh,activity

ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/'design'

def compose(freeze_world=True):
    source='data:image/png;base64,'+base64.b64encode((DESIGN/'reference.png').read_bytes()).decode()
    with gzip.open(DESIGN/'orbital-lookups.json.gz','rt',encoding='utf-8') as f:data=json.load(f)
    region='x="0" y="0" width="1136" height="1384"'
    hills='' if freeze_world else '<rect y="1184" width="1136" height="200"/>'
    world='' if freeze_world else '<g mask="url(#surface-only)"><g filter="url(#orbits)"><g mask="url(#surface-only)"><use href="#reference"/></g></g></g><g mask="url(#sun-only)"><g filter="url(#orbits)"><g mask="url(#sun-only)"><use href="#reference"/></g></g></g>'
    output=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1136" height="1384" viewBox="0 0 1136 1384" role="img" aria-labelledby="title desc">
<title id="title">Shreyas Singh — independently orbiting particle artwork</title>
<desc id="desc">Shreyas Singh — developer, builder and student. The reference's planet crescent, crossing dust ribbons, mountain folds and small sun, with grain travelling around the planet and wind following the hills. Featured projects: JanSamadhan, NyayaAI, ARTERY and Adaptive Cache Simulator. Activity uses actual GitHub contributions. Project and contact links follow the artwork.</desc>
<style>@media(prefers-reduced-motion:reduce){{.moving{{display:none}}}}</style>
<defs>
<image id="reference" width="1136" height="1384" href="{source}"/>
<filter id="orbits" x="0" y="0" width="3408" height="2768" filterUnits="userSpaceOnUse" primitiveUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
<feImage href="{data['atlas']}" x="0" y="0" width="3408" height="2768" preserveAspectRatio="none" result="atlas"/>
<feOffset in="atlas" dx="0" dy="0" {region} result="coarseA"/>
<feOffset in="atlas" dx="-1136" dy="0" {region} result="fineA"/>
<feOffset in="atlas" dx="0" dy="-1384" {region} result="coarseB"/>
<feOffset in="atlas" dx="-1136" dy="-1384" {region} result="fineB"/>
<feOffset in="atlas" dx="-2272" dy="0" {region} result="weightA"/>
<feOffset in="atlas" dx="-2272" dy="-1384" {region} result="weightB"/>
<feOffset in="SourceGraphic" dx="1" dy="1" {region} result="sourceCorrected"/>
<feDisplacementMap in="sourceCorrected" in2="coarseA" scale="510" xChannelSelector="R" yChannelSelector="G" {region} result="a0"/>
<feOffset in="a0" dx=".015625" dy=".015625" {region} result="a1"/>
<feDisplacementMap in="a1" in2="fineA" scale="7.96875" xChannelSelector="R" yChannelSelector="G" {region} result="a2"/>
<feDisplacementMap in="sourceCorrected" in2="coarseB" scale="510" xChannelSelector="R" yChannelSelector="G" {region} result="b0"/>
<feOffset in="b0" dx=".015625" dy=".015625" {region} result="b1"/>
<feDisplacementMap in="b1" in2="fineB" scale="7.96875" xChannelSelector="R" yChannelSelector="G" {region} result="b2"/>
<feColorMatrix in="weightA" type="luminanceToAlpha" {region} result="alphaA"/>
<feColorMatrix in="weightB" type="luminanceToAlpha" {region} result="alphaB"/>
<feComposite in="a2" in2="alphaA" operator="in" {region} result="litA"/>
<feComposite in="b2" in2="alphaB" operator="in" {region} result="litB"/>
<feComposite in="litA" in2="litB" operator="arithmetic" k2="1" k3="1" {region}/>
</filter>
<filter id="feather"><feGaussianBlur stdDeviation="3"/></filter>
<mask id="moving-regions" maskUnits="userSpaceOnUse"><g fill="white" filter="url(#feather)"><path d="M376 112 570 106 1136 106 1136 491 506 508 167 499 163 453 329 395 375 331Z"/>{hills}</g><g fill="black"><rect x="65" y="355" width="286" height="96"/><rect y="40" width="1136" height="67"/><rect y="509" width="1136" height="672"/><rect x="865" y="1260" width="246" height="64"/></g></mask>
<mask id="surface-only" maskUnits="userSpaceOnUse"><circle cx="752" cy="293" r="139" fill="white"/><path d="M450 463.5 1100 223" fill="none" stroke="black" stroke-width="50"/></mask>
<mask id="space-only" maskUnits="userSpaceOnUse"><rect width="1136" height="1384" fill="white"/><circle cx="752" cy="293" r="139" fill="black"/><path d="M450 463.5 1100 223" fill="none" stroke="white" stroke-width="50"/><circle cx="147" cy="1222" r="18" fill="black"/></mask>
<mask id="sun-only" maskUnits="userSpaceOnUse"><circle cx="147" cy="1222" r="14" fill="white"/></mask>
</defs>
<use href="#reference"/>
<g class="moving" mask="url(#moving-regions)">
<g mask="url(#space-only)"><g filter="url(#orbits)"><g mask="url(#moving-regions)"><g mask="url(#space-only)"><use href="#reference"/></g></g></g></g>
{world}
</g>
{activity()}
</svg>'''
    target=ROOT/'assets/profile.svg';target.write_text(output,encoding='utf-8');ET.parse(target)
    static=f'<svg xmlns="http://www.w3.org/2000/svg" width="1136" height="1384" viewBox="0 0 1136 1384" role="img" aria-labelledby="title"><title id="title">Shreyas Singh — developer, builder, student</title><image width="1136" height="1384" href="{source}"/>{activity()}</svg>'
    (ROOT/'assets/profile-static.svg').write_text(static,encoding='utf-8')
    print(f'GPU orbital profile: {target.stat().st_size/1024/1024:.2f} MiB')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--refresh-activity',action='store_true');args=p.parse_args()
    if args.refresh_activity:refresh()
    compose()
