"""Public GitHub contribution data for the profile artwork."""
from pathlib import Path
from datetime import date,timedelta
from html.parser import HTMLParser
from urllib.request import Request,urlopen
import base64,gzip,json,hashlib,argparse
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/'design'

def refresh():
    class Calendar(HTMLParser):
        def __init__(self):super().__init__();self.days=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if tag=='td' and 'data-date' in a and 'data-level' in a:
                self.days.append({'date':a['data-date'],'level':int(a['data-level'])})
    now=date.today()
    req=Request(f'https://github.com/users/shryssssss-maker/contributions?from={now.year}-01-01&to={now.isoformat()}',headers={'User-Agent':'shreyas-profile-artwork'})
    with urlopen(req,timeout=30) as r:body=r.read().decode()
    c=Calendar();c.feed(body)
    if not c.days:raise RuntimeError('No contribution days returned; saved data was kept.')
    (DESIGN/'activity.json').write_text(json.dumps({'user':'shryssssss-maker','as_of':now.isoformat(),'days':sorted(c.days,key=lambda d:d['date'])},indent=2)+'\n',encoding='utf-8')

def activity():
    # Preserve the artwork; replace only the example activity cells with the
    # owner's actual public activity, in the same panel and monochrome palette.
    c=json.loads((DESIGN/'activity.json').read_text(encoding='utf-8'))
    end=date.fromisoformat(c['as_of']);first=date(end.year,1,1)
    origin=first-timedelta(days=(first.weekday()+1)%7)
    cols=(end-origin).days//7+1;step=594/cols;cell=min(11,step-2.5)
    lookup={d['date']:d['level'] for d in c['days']}
    colors=['#242625','#525551','#81847e','#b5b8b0','#e8e9e0']
    out=['<g aria-label="Actual public GitHub contribution activity"><rect x="486" y="982" width="606" height="151" fill="#080909"/>']
    for month in range(1,end.month+1):
        day=date(end.year,month,1);x=496+((day-origin).days//7)*step
        out.append(f'<text x="{x:.2f}" y="998" font-family="Consolas,monospace" font-size="11" fill="#deded9">{day:%b}</text>')
    for col in range(cols):
        for row in range(7):
            day=origin+timedelta(days=col*7+row)
            if day<first or day>end:continue
            level=lookup.get(day.isoformat(),0)
            out.append(f'<rect x="{489+col*step:.2f}" y="{1013+row*14.5:.1f}" width="{cell:.2f}" height="11" rx="2.4" fill="{colors[level]}"><title>{day}: level {level} of 4</title></rect>')
    out.append('</g>')
    return ''.join(out)
