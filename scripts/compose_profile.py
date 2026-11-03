"""Reproduce the supplied 1136 x 1384 composition as an animated SVG.

Standard library only. All artwork, type, logos and motion are self-contained.
GitHub contribution levels are real public data, never random decoration.
"""
from pathlib import Path
from math import sin, cos, sqrt, pi, exp
from random import Random
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
from urllib.request import Request, urlopen
import argparse
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
DESIGN=ROOT/'design'
ASSETS.mkdir(exist_ok=True)
R=Random(261104)
BG='#080909'
INK='#e8e7e2'
NS='{http://www.w3.org/2000/svg}'

def text(x,y,value,size=14,fill=INK,extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{escape(value)}</text>'

def line(x1,y1,x2,y2,color='#6b6a65',width=.8):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{color}" stroke-width="{width}"/>' if y1==y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="{width}"/>'

def dots(data,width=.9):
    buckets=[[] for _ in range(8)]
    for x,y,b in data:
        k=min(7,max(0,int(b*8)))
        buckets[k].append(f'M{x:.1f},{y:.1f}h.3')
    return ''.join(f'<path d="{"".join(p)}" fill="none" stroke="{INK}" stroke-opacity="{(k+1)/8:.3f}" stroke-width="{width}" stroke-linecap="round" vector-effect="non-scaling-stroke"/>' for k,p in enumerate(buckets) if p)

def sphere_dots(data):
    # Actual circles keep the light crescent luminous when the planet is
    # rotated and the complete composition is downsampled inside GitHub.
    buckets=[[] for _ in range(8)]
    for x,y,b in data:
        k=min(7,max(0,int(b*8)))
        buckets[k].append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r=".72"/>')
    return ''.join(f'<g fill="{INK}" opacity="{(k+1)/8:.3f}">{"".join(p)}</g>' for k,p in enumerate(buckets) if p)

def outline(name,x,y,size=28):
    paths={
      'layers':'<path d="m2 8 12-6 12 6-12 6Z M2 14l12 6 12-6 M2 20l12 6 12-6"/>',
      'copy':'<rect x="3" y="7" width="19" height="19" rx="3"/><path d="M9 7V4q0-2 2-2h13q3 0 3 3v14q0 2-2 2h-3"/>',
      'scales':'<path d="M14 2v25 M5 27h18 M4 6h20 M6 5 1 17h10L6 5 M22 5l-5 12h10L22 5"/>',
      'art':'<rect x="2" y="2" width="25" height="25" rx="3"/><circle cx="9" cy="9" r="2"/><path d="m3 22 7-8 5 5 5-7 7 9"/>',
      'grad':'<path d="m1 10 14-7 14 7-14 7Z M7 14v9q8 6 16 0v-9 M29 10v14"/>',
      'code':'<path d="m10 5-8 9 8 9 M20 5l8 9-8 9"/>',
      'pin':'<path d="M25 11c0 8-10 18-10 18S5 19 5 11a10 10 0 0 1 20 0Z"/><circle cx="15" cy="11" r="3.5"/>',
      'coffee':'<path d="M4 10h19v12q0 5-5 5H9q-5 0-5-5Z M23 12h3q7 0 3 8h-6 M1 28h27 M9 1v5 M14 0v6 M19 1v5"/>',
      'external':'<path d="M13 4h12v12 M25 4 10 19 M19 2H5q-3 0-3 3v20q0 3 3 3h19q3 0 3-3v-9"/>',
    }
    return f'<g transform="translate({x} {y}) scale({size/30:.4f})" stroke="{INK}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round" fill="none">{paths[name]}</g>'

def logo(name,x,y,size):
    if name=='vercel':
        return f'<g transform="translate({x} {y}) scale({size/24:.5f})" fill="none" stroke="{INK}" stroke-width="1.1" stroke-linejoin="round"><path d="M12 2 23 22H1Z M12 7 5.5 19h13Z"/></g>'
    if name=='fastapi':
        return f'<g transform="translate({x} {y}) scale({size/24:.5f})" fill="none" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"><path d="m14 1-2 8h6L8 23l3-10H5Z"/></g>'
    svg=ET.parse(DESIGN/'icons'/f'{name}.svg').getroot()
    paths=''.join(ET.tostring(e,encoding='unicode').replace('ns0:','').replace(':ns0','') for e in svg if e.tag!=NS+'title')
    return f'<g transform="translate({x} {y}) scale({size/24:.5f})" fill="{INK}">{paths}</g>'

def refresh_activity():
    class Calendar(HTMLParser):
        def __init__(self):
            super().__init__();self.days=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if tag=='td' and 'data-date' in a and 'data-level' in a:
                self.days.append({'date':a['data-date'],'level':int(a['data-level'])})
    today=date.today()
    req=Request(f'https://github.com/users/shryssssss-maker/contributions?from={today.year}-01-01&to={today.isoformat()}',headers={'User-Agent':'shreyas-profile-artwork'})
    with urlopen(req,timeout=30) as response:
        content=response.read().decode()
    cal=Calendar();cal.feed(content)
    if not cal.days:
        raise RuntimeError('GitHub returned no contribution data; refusing to overwrite the saved snapshot.')
    (DESIGN/'activity.json').write_text(json.dumps({'user':'shryssssss-maker','as_of':today.isoformat(),'days':sorted(cal.days,key=lambda d:d['date'])},indent=2)+'\n',encoding='utf-8')

def planet():
    p=['<defs><clipPath id="front"><rect x="-620" y="0" width="1240" height="620"/></clipPath><clipPath id="globe"><circle r="140"/></clipPath>']
    p.append(f'<radialGradient id="body" cx="28%" cy="16%" r="78%"><stop stop-color="#151717"/><stop offset=".65" stop-color="{BG}"/><stop offset="1" stop-color="{BG}"/></radialGradient>')
    for k,(n,lo,hi) in enumerate([(1800,170,215),(5600,224,373),(3400,375,526)]):
        data=[]
        for j in range(n):
            angle=R.uniform(0,2*pi)
            radius=R.uniform(lo,hi)
            # Narrow orbital filaments sit within the diffuse dust veil.
            if k==0 and j%3:radius=R.gauss(195,3)
            if k==1 and j%3:radius=R.gauss(307,6)
            if j<n//4:
                angle=R.gauss(.4 if j%2 else 3.6,.32)
                if k==2:radius=R.gauss((lo+hi)/2,(hi-lo)*.20)
            b=R.uniform(.15,.95)*(1 if k<2 else .45)
            data.append((radius*cos(angle),(radius+3*sin(angle*5))*sin(angle),b))
        p.append(f'<g id="r{k}">{dots(data,.85)}</g>')
    p.append('</defs><g transform="translate(752 288) rotate(-23)">')
    for k,d in enumerate([30,48,72]):
        direction=-360 if k==1 else 360
        p.append(f'<g transform="scale(1 .26)"><use class="still" xlink:href="#r{k}"/><g class="orbit"><use xlink:href="#r{k}"/><animateTransform attributeName="transform" type="rotate" from="0" to="{direction}" dur="{d}s" repeatCount="indefinite"/></g></g>')
    p.append('<circle r="140" fill="url(#body)"/>')
    data=[]
    for _ in range(7600):
        z=R.random();a=R.uniform(0,2*pi);q=sqrt(1-z*z)
        x,y=q*cos(a),q*sin(a)
        lighting=max(0,-.52*x-.82*y+.12*z)
        rim=(1-z)**5
        b=(.015+lighting*1.65+rim*.75)*R.uniform(.4,1)
        data.append((140*x,140*y,min(1,b)))
    p.append(sphere_dots(data))
    p.append('<g class="motion" clip-path="url(#globe)">')
    for _ in range(380):
        lat=R.uniform(-.97,.97)*140;a=sqrt(140**2-lat**2);b=a*.18
        begin=-R.random()*36
        path=f'M{-a:.1f},{lat:.1f}a{a:.1f},{b:.1f} 0 1 0 {2*a:.1f},0a{a:.1f},{b:.1f} 0 1 0 {-2*a:.1f},0'
        p.append(f'<circle r="{R.uniform(.4,.8):.2f}" fill="{INK}" opacity=".4"><animateMotion path="{path}" dur="36s" begin="{begin:.2f}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".1;.6;.35;.05;0;0;.1" keyTimes="0;.15;.35;.5;.6;.9;1" dur="36s" begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')
    p.append('</g>')
    for k,d in enumerate([30,48,72]):
        direction=-360 if k==1 else 360
        p.append(f'<g transform="scale(1 .26)" clip-path="url(#front)"><use class="still" xlink:href="#r{k}"/><g class="orbit"><use xlink:href="#r{k}"/><animateTransform attributeName="transform" type="rotate" from="0" to="{direction}" dur="{d}s" repeatCount="indefinite"/></g></g>')
    # Project the narrow foreground filament numerically so its round specks
    # keep their brightness across browsers' differing <use> stroke scaling.
    foreground=[]
    for j in range(1550):
        a=R.uniform(0,pi);radius=R.gauss(307 if j<1250 else 195,3.2)
        foreground.append((radius*cos(a),.26*radius*sin(a),R.uniform(.25,.95)))
    p.append(dots(foreground,1.3))
    # Grazing particles cross the orbital plane and disperse in long arcs.
    p.append('<g class="motion">')
    for j in range(85):
        dy=R.gauss(0,11);d=12 if j%2 else 17;begin=-R.random()*d
        path=f'M-540,{62+dy:.1f}C-260,{-106+dy:.1f} 124,{112+dy:.1f} 510,{-74+dy:.1f}'
        p.append(f'<circle r="{R.uniform(.4,.9):.2f}" fill="{INK}"><animateMotion path="{path}" dur="{d}s" begin="{begin:.2f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;.5;.8;.4;0" dur="{d}s" begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')
    p.append('</g></g>')
    return ''.join(p)

def header():
    s=[text(117,70,'> shreyas@github:~$ whoami',13),text(117,96,'> Shreyas Singh',13)]
    s.append('<circle cx="62" cy="69" r="1.7" fill="#eee"/>')
    s.append(text(1078,70,'[ developer ]    [ builder ]    [ student ]',12.5,extra='text-anchor="end"'))
    s.append(text(74,245,'Shreyas',80,extra='class="serif" letter-spacing="-2"'))
    s.append(text(74,319,'Singh',86,extra='class="serif" font-style="italic" letter-spacing="-2"'))
    s.append('<path d="M280 319h27" stroke="#e8e7e2" stroke-width="2"/>')
    for i,value in enumerate(['Building where','systems, AI and real-world','impact intersect.']):
        s.append(text(76,387+i*27,value,18,'#c6c6c1',extra='class="body"'))
    s.append(outline('grad',69,518,29))
    for i,value in enumerate(['B.Tech ECE','Manipal University Jaipur','(2025 – 2029)']):s.append(text(121,524+i*20,value,13))
    s.append(line(340,519,340,561))
    s.append(outline('code',376,517,28))
    s.append(text(426,533,'AI · Systems · Full Stack',13))
    s.append(text(426,553,'Research · Product',13))
    s.append(line(636,519,636,561))
    s.append(outline('pin',677,518,25))
    s.append(text(720,532,'Delhi / Jaipur',13));s.append(text(720,552,'India',13))
    s.append(line(868,519,868,561))
    s.append(outline('coffee',912,515,29))
    s.append(text(962,532,'Coffee × Code',13));s.append(text(962,550,'(often in that order)',10.5))
    return ''.join(s)

def projects():
    s=['<rect x="50" y="622" width="8" height="8" fill="#deded9"/>',text(77,632,'Featured Projects',19)]
    s.append(line(293,627,960,627))
    s.append(text(1092,629,'[ view all → ]',12,extra='text-anchor="end"'))
    cards=[(50,248,'copy','JanSamadhan',['Civic complaint platform','with maps & authority','dashboard.'],['Next.js','FastAPI','Supabase']),
           (320,241,'scales','NyayaAI',['Multi-agent legal assistant','for instant guidance &','document drafting.'],['Python','LangGraph','OpenAI']),
           (583,240,'art','ARTERY',['AI art marketplace','connecting artists and','patrons.'],['Next.js','AWS','Bedrock']),
           (844,242,'layers','Cache Simulator',['RL-based cache replacement','with DQN. Compared against','LRU/LFU/Belady.'],['Python','PyTorch','DQN'])]
    for x,w,ico,title,description,tags in cards:
        s.append(f'<rect x="{x}" y="668" width="{w}" height="212" rx="12" fill="none" stroke="#565651" stroke-width=".9"/>')
        s.append(outline(ico,x+23,689,28))
        size=17 if title=='Cache Simulator' else 18
        s.append(text(x+23,748,title,size,extra='font-weight="bold" letter-spacing="-.6"'))
        if title!='Cache Simulator':
            tx=x+23+len(title)*10.2+15
            s.append(text(round(tx),748,'↗',18))
        for i,value in enumerate(description):s.append(text(x+23,781+i*20,value,13.5,'#d3d3cf',extra='letter-spacing="-.25"'))
        tx=x+23
        for tag in tags:
            tw=len(tag)*6.2+17
            s.append(f'<rect x="{tx}" y="841" width="{tw:.1f}" height="22" rx="5" fill="#232424"/>')
            s.append(text(tx+tw/2,856,tag,10.5,extra='text-anchor="middle"'))
            tx+=tw+8
    return ''.join(s)

def stack_activity():
    s=['<rect x="55" y="944" width="8" height="8" fill="#deded9"/>',text(80,954,'Tech Stack',19),line(218,949,424,949),line(460,942,460,1131)]
    s.extend(['<rect x="495" y="944" width="8" height="8" fill="#deded9"/>',text(520,954,'Activity',19),line(638,949,1085,949)])
    names=['nextdotjs','react','python','typescript','vercel','fastapi','postgresql','supabase','docker','amazonwebservices']
    for i,name in enumerate(names):
        x=56+(i%5)*77;y=987+(i//5)*81
        s.append(f'<rect x="{x}" y="{y}" width="64" height="66" rx="12" fill="none" stroke="#4f504c" stroke-width=".9"/>')
        size=34 if name!='amazonwebservices' else 36
        s.append(logo(name,x+(64-size)/2,y+(66-size)/2,size))
    activity=json.loads((DESIGN/'activity.json').read_text(encoding='utf-8'))
    end=date.fromisoformat(activity['as_of']);first=date(end.year,1,1)
    origin=first-timedelta(days=(first.weekday()+1)%7)
    weeks=(end-origin).days//7+1
    step=594/weeks;cell=min(11,step-2.5)
    lookup={d['date']:d['level'] for d in activity['days']}
    colors=['#242625','#525551','#81847e','#b5b8b0','#e8e9e0']
    for month in range(1,end.month+1):
        day=date(end.year,month,1);col=(day-origin).days//7
        s.append(text(round(496+col*step,2),998,day.strftime('%b'),11))
    s.append(f'<g aria-label="Actual public GitHub contribution levels, through {end.isoformat()}">')
    for col in range(weeks):
        for row in range(7):
            day=origin+timedelta(days=col*7+row)
            if day<first or day>end:continue
            level=lookup.get(day.isoformat(),0)
            x=489+col*step;y=1013+row*14.5
            s.append(f'<rect x="{x:.2f}" y="{y:.1f}" width="{cell:.2f}" height="11" rx="2.4" fill="{colors[level]}"><title>{day}: contribution level {level} of 4</title></rect>')
    s.append('</g>')
    return ''.join(s)

def terrain():
    s=[]
    # Three distinct ridgelines, rather than a flat rectangular particle band.
    data=[]
    for layer in range(3):
        for _ in range(5100):
            x=R.uniform(-20,1156);z=R.random()
            hill=(72*exp(-((x-247-layer*15)/105)**2)+38*exp(-((x-440+layer*19)/75)**2)+29*exp(-((x-661-layer*24)/88)**2)+25*exp(-((x-81-layer*8)/58)**2))
            base=1308+layer*16+x*.035
            y=base-hill*(1-z*.5)+z*50
            y+=sin(x*.055+layer+z*5)*3+R.gauss(0,.9)
            opacity=R.uniform(.3,1)*(1-z)**1.1*max(.1,1-x/1380)*(1-layer*.13)*2.1
            data.append((x,y,opacity))
        for j in range(260):
            x=R.uniform(-20,1136)
            hill=(72*exp(-((x-247-layer*15)/105)**2)+38*exp(-((x-440+layer*19)/75)**2)+29*exp(-((x-661-layer*24)/88)**2)+25*exp(-((x-81-layer*8)/58)**2))
            y=1308+layer*16+x*.035-hill+sin(x*.055+layer)*3+R.gauss(0,.75)
            data.append((x,y,R.uniform(.4,.9)*max(.1,1-x/1380)))
    s.append(dots(data,1.15))
    moon=[]
    for _ in range(230):
        a=R.uniform(0,2*pi);r=sqrt(R.random())*12
        moon.append((148+r*cos(a),1222+r*sin(a),R.uniform(.2,.95)))
    s.append(dots(moon,1))
    s.append('<g class="motion">')
    for j in range(115):
        dy=R.gauss(0,8);duration=R.uniform(13,28);begin=-R.uniform(0,duration)
        path=f'M-40,{1321+dy:.1f}C100,{1305+dy:.1f} 157,{1220+dy:.1f} 306,{1273+dy:.1f}S512,{1300+dy:.1f} 674,{1325+dy:.1f}S967,{1383+dy:.1f} 1190,{1355+dy:.1f}'
        s.append(f'<circle r="{R.uniform(.3,.8):.2f}" fill="{INK}"><animateMotion path="{path}" dur="{duration:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;.5;.7;.25;0" dur="{duration:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')
    for k in range(4):
        off=k*5
        path=f'M-20,{1320+off}C100,{1300+off} 157,{1220+off} 306,{1273+off}S512,{1300+off} 674,{1325+off}S967,{1383+off} 1190,{1355+off}'
        s.append(f'<path d="{path}" fill="none" stroke="{INK}" stroke-width=".5" stroke-opacity=".12" stroke-dasharray="27 90 4 200 12 900"><animate attributeName="stroke-dashoffset" from="1233" to="0" dur="{19+k*3}s" repeatCount="indefinite"/></path>')
    s.append('</g>')
    s.append(line(881,1279,881,1308,'#5d5f5b',.8))
    s.append(logo('github',919,1283,19));s.append(logo('linkedin',969,1284,17));s.append(logo('x',1018,1284,17));s.append(outline('external',1066,1282,18))
    return ''.join(s)

def compose():
    s=[f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1136" height="1384" viewBox="0 0 1136 1384" role="img" aria-labelledby="title desc">
<title id="title">Shreyas Singh — developer, builder, student</title><desc id="desc">Building where systems, AI and real-world impact intersect. B.Tech ECE, Manipal University Jaipur, 2025–2029. Delhi and Jaipur, India. Featured projects: JanSamadhan, NyayaAI, ARTERY, Adaptive Cache Simulator. Tech stack and actual GitHub contribution activity. A rotating particle planet above; drifting wind over particle hills below. Project and contact links are below the artwork.</desc>
<style>text{{font-family:Consolas,'Liberation Mono',monospace}}.serif{{font-family:Georgia,'Times New Roman',serif}}.body{{font-family:'Segoe UI',Arial,sans-serif;letter-spacing:.4px}}.still{{display:none}}@media(prefers-reduced-motion:reduce){{.motion,.orbit{{display:none}}.still{{display:inline}}}}</style>
<rect width="1136" height="1384" fill="{BG}"/>
''']
    # Very fine grain keeps the uninterrupted black canvas from looking flat.
    grain=[(R.uniform(0,1136),R.uniform(0,1384),R.uniform(.015,.055)) for _ in range(700)]
    s.append(dots(grain,.35))
    stars=[(R.uniform(0,1136),R.uniform(0,1384),R.uniform(.08,.35)) for _ in range(180)]
    s.append(dots(stars,.65))
    s.extend([planet(),header(),projects(),stack_activity(),terrain(),'</svg>'])
    path=ASSETS/'profile.svg'
    path.write_text(''.join(s),encoding='utf-8')
    ET.parse(path)
    print(f'{path.name}: {path.stat().st_size/1024:.1f} KiB; valid self-contained SVG')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--refresh-activity',action='store_true')
    args=parser.parse_args()
    if args.refresh_activity:refresh_activity()
    compose()
