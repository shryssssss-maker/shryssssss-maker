"""Build original, script-free SVG artwork for Shreyas's GitHub profile.

Python standard library only. Seeded particles make regeneration reproducible.
SMIL runs inside an <img>; no JavaScript, fonts, or external image services.
"""
from pathlib import Path
from math import sin, cos, sqrt, pi, exp
from random import Random
from html import escape
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
rng = Random(2611)
BG = '#08090b'
WHITE = '#e9e8e3'

def txt(x, y, text, size=14, fill='#a5a5a5', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{escape(text)}</text>'

def points(data, width=1):
    """Batch dots by luminance. Round non-scaling strokes survive projection."""
    buckets = [[] for _ in range(8)]
    for x,y,b in data:
        k = min(7, max(0, int(b*8)))
        # Chromium culls extremely short stroked subpaths. A .3-unit segment
        # remains a round speck at profile scale and survives image rendering.
        buckets[k].append(f'M{x:.1f},{y:.1f}h.3')
    return ''.join(f'<path d="{"".join(p)}" fill="none" stroke="{WHITE}" stroke-opacity="{(i+1)/8:.3f}" stroke-width="{width}" stroke-linecap="round" vector-effect="non-scaling-stroke"/>' for i,p in enumerate(buckets) if p)

def start(h, title, desc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1200" height="{h}" viewBox="0 0 1200 {h}" role="img" aria-labelledby="title desc">
<title id="title">{title}</title><desc id="desc">{desc}</desc>
<style>text{{font-family:Consolas,'Liberation Mono',monospace}} .serif{{font-family:Georgia,'Times New Roman',serif}} .still{{display:none}} @media(prefers-reduced-motion:reduce){{.motion,.orbit{{display:none}} .still{{display:inline}}}}</style>
<rect width="1200" height="{h}" fill="{BG}"/>
'''

def stars(w,h,n):
    data=[]
    for _ in range(n):
        x,y=rng.random()*w,rng.random()*h
        data.append((x,y,rng.uniform(.06,.35)))
    return points(data,.7)

def hero():
    s=[start(610,'Shreyas Singh — AI, systems and the web',
       'A monochrome particle planet with a rotating surface, counter-orbiting dust rings and crossing streams. Developer, builder and ECE student at Manipal University Jaipur.')]
    s.append('''<defs>
<radialGradient id="body" cx="29%" cy="21%" r="75%"><stop stop-color="#222426"/><stop offset=".48" stop-color="#0e1012"/><stop offset="1" stop-color="#08090b"/></radialGradient>
<radialGradient id="atmosphere"><stop offset=".82" stop-color="#d7d9dc" stop-opacity="0"/><stop offset=".95" stop-color="#d7d9dc" stop-opacity=".035"/><stop offset="1" stop-color="#d7d9dc" stop-opacity="0"/></radialGradient>
<clipPath id="front"><rect x="-520" y="0" width="1040" height="520"/></clipPath>
<clipPath id="globe"><circle r="160"/></clipPath>
''')
    # Three annular populations: thin inner fast ring, diffuse main ring,
    # and a slow outer veil. Clumps make rotation visible without strobing.
    for k,(n,lo,hi,duration) in enumerate([(1700,191,227,24),(4500,236,340,40),(2000,346,427,64)]):
        data=[]
        for j in range(n):
            theta=rng.uniform(0,2*pi)
            radius=rng.uniform(lo,hi)
            warp=2.5*sin(5*theta + radius*.06)
            b=rng.uniform(.08,.72)*(1 if k<2 else .40)
            # Density knots orbit like shoals of dust.
            if j<n//3:
                theta=rng.gauss(.5 if j%2 else 3.7,.25)
                radius=rng.gauss((lo+hi)/2,(hi-lo)*.19)
                b*=1.3
            data.append((radius*cos(theta),(radius+warp)*sin(theta),min(.98,b)))
        direction=360 if k!=1 else -360
        s.append(f'<g id="ring{k}">{points(data,.85 if k!=0 else 1)}<g class="motion"/></g>')
    s.append('</defs>')
    s.append(stars(1200,530,330))
    s.append(txt(45,43,'> shreyas@github:~$ whoami',13,'#b9b9b8'))
    s.append(txt(1155,43,'[ developer ]   [ builder ]   [ student ]',12,'#aaa', 'text-anchor="end"'))
    # Planet and back ring. Projection is on the outside of orbital rotation.
    s.append('<g transform="translate(835 278) rotate(-23)">')
    s.append('<circle r="180" fill="url(#atmosphere)"/>')
    for k,d in enumerate([24,40,64]):
        a=360 if k!=1 else -360
        s.append(f'<g transform="scale(1 .29)"><use class="still" xlink:href="#ring{k}"/><g class="orbit"><use xlink:href="#ring{k}"/><animateTransform attributeName="transform" type="rotate" from="0" to="{a}" dur="{d}s" repeatCount="indefinite"/></g></g>')
    s.append('<circle r="160" fill="url(#body)"/>')
    # A lit hemisphere, with physically projected points and soft limb dust.
    data=[]
    for _ in range(10500):
        z=rng.random()
        phi=rng.uniform(0,2*pi)
        q=sqrt(1-z*z)
        nx,ny=q*cos(phi),q*sin(phi)
        light=max(0, -.55*nx-.62*ny+.25*z)
        rim=(1-z)**4
        bands=.65+.35*sin(24*ny+sin(9*nx)*2)
        b=(.035+light*.83+rim*.35)*bands*rng.uniform(.35,1)
        data.append((160*nx,160*ny,min(1,b)))
    # Explicit circles preserve the luminous stippling on the sphere at
    # GitHub's downscaled profile width (tiny path strokes can disappear).
    s.append('<g fill="#e9e8e3">')
    for x,y,b in data:
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.45,.85):.2f}" opacity="{min(1,b*1.6):.2f}"/>')
    s.append('</g>')
    # Moving particles trace projected latitude ellipses. Opacity hides the
    # far hemisphere, so the surface rotates rather than sliding as a texture.
    s.append('<g class="motion" clip-path="url(#globe)">')
    for _ in range(460):
        lat=rng.uniform(-.97,.97)*160
        a=sqrt(160**2-lat**2)
        b=a*.19
        dur=32
        begin=-rng.random()*dur
        path=f'M{-a:.1f},{lat:.1f}a{a:.1f},{b:.1f} 0 1 0 {2*a:.1f},0a{a:.1f},{b:.1f} 0 1 0 {-2*a:.1f},0'
        s.append(f'<circle r="{rng.uniform(.45,.9):.2f}" fill="{WHITE}" opacity=".4"><animateMotion path="{path}" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".15;.7;.4;.08;0;0;.15" keyTimes="0;.15;.35;.5;.6;.9;1" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')
    s.append('</g>')
    # Foreground half of each ring is composited over the sphere.
    for k,d in enumerate([24,40,64]):
        a=360 if k!=1 else -360
        s.append(f'<g transform="scale(1 .29)" clip-path="url(#front)"><use class="still" xlink:href="#ring{k}"/><g class="orbit"><use xlink:href="#ring{k}"/><animateTransform attributeName="transform" type="rotate" from="0" to="{a}" dur="{d}s" repeatCount="indefinite"/></g></g>')
    # Two grazing streams cross and disperse around the orbital plane.
    s.append('<g class="motion">')
    for j in range(70):
        dy=rng.gauss(0,10)
        path=f'M-425,{80+dy:.1f}C-190,{-145+dy:.1f} 180,{145+dy:.1f} 440,{-90+dy:.1f}'
        dur=8 if j%2 else 12
        begin=-rng.random()*dur
        s.append(f'<circle r="{rng.uniform(.45,1):.2f}" fill="#f7f7f4"><animateMotion path="{path}" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;.6;.3;.75;0" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')
    s.append('</g></g>')
    # Text remains deliberately separate from the dust field.
    s.append(txt(48,183,'Shreyas',91,WHITE,'class="serif" letter-spacing="-4"'))
    s.append(txt(48,269,'Singh',96,WHITE,'class="serif" font-style="italic" letter-spacing="-4"'))
    s.append('<path d="M287 280h30" stroke="#d9d9d3" stroke-width="2"><animate attributeName="opacity" values="1;1;.2;1" dur="3s" repeatCount="indefinite"/></path>')
    s.append(txt(51,337,'Building where',18,'#bfc0bf'))
    s.append(txt(51,366,'systems, AI and real-world',18,'#bfc0bf'))
    s.append(txt(51,395,'impact intersect.',18,'#bfc0bf'))
    s.append(txt(52,459,'CURIOUS BY DEFAULT. BUILDER BY CHOICE.',10,'#747777','letter-spacing="1.3"'))
    s.append('<path d="M48 505H1152" stroke="#333537" stroke-width=".8"/>')
    for x in [347,651,940]:
        s.append(f'<path d="M{x} 532v43" stroke="#3e4042" stroke-width=".8"/>')
    for x,label,line1,line2 in [(51,'01 / EDUCATION','B.Tech · ECE','Manipal University Jaipur'),(376,'02 / EXPLORING','AI · Systems · Full Stack','Research meets product'),(680,'03 / BASED IN','Delhi / Jaipur','India · UTC +05:30'),(969,'04 / FUEL','Coffee × Code','Often in that order')]:
        s.append(txt(x,533,label,10,'#727779','letter-spacing="1"'))
        s.append(txt(x,555,line1,13,'#d4d4ce'))
        s.append(txt(x,575,line2,11,'#9a9d9d'))
    s.append('</svg>')
    (ASSETS/'orbital-hero.svg').write_text(''.join(s),encoding='utf-8')

def hills():
    s=[start(295,'Particle hills — keep building, stay curious',
       'Layered monochrome hills made of fine particles. Gentle ribbons of wind sweep along the ridgelines in a continuous loop.')]
    s.append(stars(1200,240,140))
    s.append(txt(46,40,'THERE IS ALWAYS MORE TO EXPLORE.',10,'#808688','letter-spacing="2.6"'))
    s.append(txt(1154,40,'keep building_',12,'#b4b8b8','text-anchor="end"'))
    # A small particle moon above the horizon.
    data=[]
    for _ in range(280):
        a=rng.uniform(0,2*pi); r=sqrt(rng.random())*12
        data.append((103+cos(a)*r,100+sin(a)*r,rng.uniform(.1,.65)))
    s.append(points(data,.7))
    data=[]
    for layer in range(4):
        for _ in range(5800):
            x=rng.uniform(-40,1240)
            z=rng.random()
            peaks=(74*exp(-((x-230-layer*18)/118)**2)+44*exp(-((x-496+layer*25)/111)**2)+33*exp(-((x-756-layer*32)/102)**2))
            base=208+layer*16
            y=base-peaks*(1-z*.7)+z*65
            y+=sin(x*.045+z*7+layer)*3 + rng.gauss(0,1.2)
            b=(1-z)**1.35*rng.uniform(.3,1)*(1-layer*.10)
            data.append((x,y,b))
    s.append(points(data,1.05))
    # Fine ridge lines carry no solid fill, preserving the airborne feeling.
    for k in range(5):
        path=f'M-50,{228+k*4} C140,{205+k*4} 150,{125+k*4} 285,{166+k*4} S495,{225+k*4} 640,{201+k*4} S930,{261+k*3} 1250,{252+k*3}'
        s.append(f'<path d="{path}" fill="none" stroke="#e5e6e1" stroke-opacity=".06" stroke-width=".6"/>')
    # Long, organic streamlines with travelling highlights, and dust motes
    # on nearby paths. All begin out of phase to avoid a synchronized reset.
    s.append('<g class="motion">')
    for k in range(7):
        offset=k*5
        path=f'M-90,{235+offset} C110,{209+offset} 154,{127+offset} 312,{177+offset} S540,{201+offset} 709,{223+offset} S1020,{278+offset} 1290,{234+offset}'
        s.append(f'<path d="{path}" fill="none" stroke="#e6e8e3" stroke-opacity="{.16-k*.016:.2f}" stroke-width=".7" stroke-dasharray="40 110 6 260 18 700"><animate attributeName="stroke-dashoffset" from="1200" to="0" dur="{16+k*2}s" repeatCount="indefinite"/></path>')
    for j in range(160):
        dy=rng.gauss(0,13)
        path=f'M-40,{232+dy:.1f} C150,{211+dy:.1f} 157,{127+dy:.1f} 312,{173+dy:.1f} S540,{202+dy:.1f} 709,{218+dy:.1f} S1020,{273+dy:.1f} 1240,{237+dy:.1f}'
        dur=rng.uniform(10,24); begin=-rng.uniform(0,dur)
        s.append(f'<circle r="{rng.uniform(.35,.95):.2f}" fill="#f0f0e8" opacity=".5"><animateMotion path="{path}" dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;.4;.75;.35;0" dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')
    s.append('</g></svg>')
    (ASSETS/'particle-hills.svg').write_text(''.join(s),encoding='utf-8')

def mobile():
    """Recompose, rather than shrink, the same hero for narrow profiles."""
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    root=ET.fromstring((ASSETS/'orbital-hero.svg').read_text(encoding='utf-8'))
    root.set('width','640'); root.set('height','870'); root.set('viewBox','0 0 640 870')
    ns='{http://www.w3.org/2000/svg}'
    for e in list(root):
        if e.tag==ns+'rect':
            e.set('width','640'); e.set('height','870')
        if e.tag==ns+'g' and e.get('transform')=='translate(835 278) rotate(-23)':
            e.set('transform','translate(340 495) rotate(-23) scale(.86)')
        if e.tag==ns+'path':
            d=e.get('d','')
            if d.startswith('M287'):
                e.set('d','M223 215h27')
            elif d.startswith('M48 505'):
                e.set('d','M32 703H608')
            elif d.startswith(('M347','M651','M940')):
                root.remove(e)
        if e.tag!=ns+'text':
            continue
        value=''.join(e.itertext())
        if value.startswith('> shreyas'):
            e.set('x','32');e.set('y','34');e.set('font-size','13')
        elif value.startswith('[ developer'):
            e.set('x','32');e.set('y','64');e.set('text-anchor','start');e.set('font-size','12')
        elif value=='Shreyas':
            e.set('x','32');e.set('y','143');e.set('font-size','76')
        elif value=='Singh':
            e.set('x','32');e.set('y','211');e.set('font-size','80')
        elif value in ['Building where','systems, AI and real-world','impact intersect.']:
            e.set('x','34');e.set('y',str(258+['Building where','systems, AI and real-world','impact intersect.'].index(value)*23));e.set('font-size','17')
        elif value.startswith('CURIOUS BY'):
            root.remove(e)
        elif float(e.get('y','0'))>=530:
            oldx=float(e.get('x'));oldy=float(e.get('y'))
            col=0 if oldx<350 else 1 if oldx<650 else 2 if oldx<940 else 3
            e.set('x',str(34+(col%2)*306))
            e.set('y',str(int(729+(col//2)*73+(oldy-533))))
            e.set('font-size',str(int(e.get('font-size'))+2))
    (ASSETS/'orbital-hero-mobile.svg').write_text(ET.tostring(root,encoding='unicode'),encoding='utf-8')

def stack():
    s=[start(146,'Tools I build with','Next.js, React, TypeScript, Python, FastAPI, PostgreSQL, Supabase, Docker, PyTorch and AWS.')]
    items=[('N','Next.js'),('◉','React'),('TS','TypeScript'),('Py','Python'),('ϟ','FastAPI'),('pg','PostgreSQL'),('↯','Supabase'),('▤','Docker'),('◒','PyTorch'),('aws','AWS')]
    for i,(glyph,label) in enumerate(items):
        x=30+i*116
        s.append(f'<rect x="{x+13}" y="18" width="76" height="69" rx="13" fill="#0e1012" stroke="#373a3c" stroke-width=".9"/>')
        s.append(txt(x+51,62,glyph,25,'#e6e5df','text-anchor="middle"'))
        s.append(txt(x+51,116,label,11,'#a8acad','text-anchor="middle"'))
    s.append('</svg>')
    (ASSETS/'stack.svg').write_text(''.join(s),encoding='utf-8')

hero()
mobile()
hills()
stack()
for path in ASSETS.glob('*.svg'):
    print(path.name, f'{path.stat().st_size/1024:.1f} KiB')

