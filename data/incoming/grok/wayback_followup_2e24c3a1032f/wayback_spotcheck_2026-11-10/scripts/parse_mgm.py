import re,json,sys
def clean(s): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s)).strip()
def parse(fn):
    h=open(fn,encoding='utf-8',errors='replace').read()
    h=re.sub(r'<!---->','',h); h=re.sub(r' _ngcontent-[^ >=]*=""','',h); h=re.sub(r' _nghost-[^ >=]*=""','',h)
    starts={}
    for m in re.finditer(r'"@type":"SportsEvent","name":"([^"]+)","@context":"http://schema.org","startDate":"([^"]+)","url":"[^"]*-(\d+)"',h):
        starts[m.group(3)]=(m.group(1),m.group(2))
    out={}
    pos=[(m.start(),m.group(1)) for m in re.finditer(r'(\d{8})"><ms-event-detail',h)]
    for k,(p,eid) in enumerate(pos):
        end=pos[k+1][0] if k+1<len(pos) else p+20000
        s=h[p:end]
        parts=[x.strip() for x in re.findall(r'<div class="participant ng-star-inserted">([^<]*)<',s)]
        timer=re.search(r'<ms-prematch-timer[^>]*>([^<]*)<',s)
        groups=re.findall(r'<ms-option-group class="([^"]*)"[^>]*>(.*?)</ms-option-group>',s,re.S)
        gs=[]
        for cls,g in groups:
            opts=re.findall(r'<ms-option [^>]*>(.*?)</ms-option>',g,re.S)
            o=[]
            for op in opts:
                attr=re.search(r'option-attribute[^>]*>([^<]*)<',op)
                val=re.search(r'custom-odds-value-style[^>]*>([^<]*)<',op)
                o.append(((attr.group(1).strip() if attr else None),(val.group(1).strip() if val else None)))
            gs.append(o)
        # snippet: participant names + ML values as rendered text
        out[eid]=dict(participants=parts,timer=timer.group(1).strip() if timer else None,groups=gs,start=starts.get(eid))
    return out
if __name__=='__main__':
    for eid,v in parse(sys.argv[1]).items(): print(eid,v['participants'],v['timer'],v['start'],[g for g in v['groups']])
