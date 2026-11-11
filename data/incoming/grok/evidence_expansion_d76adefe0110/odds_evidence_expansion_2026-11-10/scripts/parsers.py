"""Independent parsers for archived pages (no page content is redistributed)."""
import re,html
from parse_mgm import parse as parse_mgm
def text(fn):
    t=open(fn,encoding='utf-8',errors='replace').read()
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
    t=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' | ',t)))
    return re.sub(r'(\|\s*)+','| ',t)
def meta_times(fn):
    h=open(fn,encoding='utf-8',errors='replace').read()
    p=re.search(r'article:published_time" content="([^"]+)"',h) or re.search(r'"datePublished":"([^"]+)"',h)
    m=re.search(r'article:modified_time" content="([^"]+)"',h) or re.search(r'"dateModified":"([^"]+)"',h)
    return (p.group(1) if p else None),(m.group(1) if m else None)
def parse_an(fn):
    """Action Network article odds boxes: '<A> (<line>) vs. <B> | <X> Odds | p | <Y> Odds | p | Total | t | ... Time | T | ... Odds [|] via | Book'"""
    t=text(fn); out=[]
    for m in re.finditer(r'\| ([^|]{3,60}?) vs\. ([^|]{3,60}?) \| ([^|]{2,40}?) Odds \| ([^|]+?) \| ([^|]{2,40}?) Odds \| ([^|]+?) \| Total \| ([^|]+?) \| (?:Day ⋅ )?Time \| ([^|]+?) \|(.{0,80}?)Odds \|? ?via \| ([^|]+)',t):
        out.append(dict(matchup=f"{m.group(1).strip()} vs. {m.group(2).strip()}",t1=m.group(3).strip(),p1=m.group(4).strip(),t2=m.group(5).strip(),p2=m.group(6).strip(),total=m.group(7).strip(),time=m.group(8).strip(),book=m.group(10).strip().rstrip('.'),snippet=m.group(0)[2:]))
    return out
def parse_bol(fn):
    t=text(fn); out=[]
    for m in re.finditer(r'\| ([^|]{3,40}?) at ([^|]{3,40}?) \| ([^|]{2,40}?) \|? ?Moneyline/Spread \| ([^|/]+?) / ([^|]+?) \| ([^|]{2,40}?) Moneyline/Spread \| ([^|/]+?) / ([^|]+?) \| Total \| ([^|]+?) \| Time \| ([^|]+?) \|(.{0,80}?)Odds via \| ([^|]+)',t):
        out.append(dict(away=m.group(1).strip(),home=m.group(2).strip(),t1=m.group(3).strip(),p1=m.group(4).strip(),t2=m.group(6).strip(),p2=m.group(7).strip(),time=m.group(10).strip(),book=m.group(12).strip(),snippet=m.group(0)[2:]))
    return out
def parse_dk(fn):
    h=open(fn,encoding='utf-8',errors='replace').read()
    ev={}
    for m in re.finditer(r'"eventId":"(\d+)","displayGroupId":"\d+","eventGroupId":"204466","eventGroupName":"[^"]*","name":"([^"]+)","nameIdentifier":"[^"]*","startDate":"([^"]+)"',h):
        ev[m.group(1)]=dict(name=m.group(2),start=m.group(3))
    offers={}
    pos=[m for m in re.finditer(r'"providerOfferId":"([^"]+)","eventId":"(\d+)"',h)]
    for k,m in enumerate(pos):
        seg=h[m.start():(pos[k+1].start() if k+1<len(pos) else m.start()+5000)]
        lab=re.search(r'"label":"([^"]+)"',seg)
        if not lab or m.group(1) in offers: continue
        outs=[]
        for o in seg.split('{"providerOutcomeId"')[1:]:
            l=re.search(r'"label":"([^"]+)"',o); a=re.search(r'"oddsAmerican":"([^"]+)"',o); ln=re.search(r'"line":(-?[\d.]+)',o)
            if l and a: outs.append((l.group(1),a.group(1).replace('−','-'),ln.group(1) if ln else None))
        offers[m.group(1)]=dict(event=m.group(2),label=lab.group(1),outcomes=outs)
    return ev,offers
