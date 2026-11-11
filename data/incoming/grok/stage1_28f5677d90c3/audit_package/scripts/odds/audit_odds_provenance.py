"""Full provenance audit of odds records (1,470 original + 525 additional).
Read-only on all inputs. Writes only to /workspace/audit/odds/.
Re-extracts values from saved raw evidence with code paths independent of the original parsers."""
import csv,json,re,glob,gzip,collections,datetime as dt,os,unicodedata
from bs4 import BeautifulSoup
W='/workspace'; OUT=W+'/audit/odds'; DL=W+'/deliverables'; FP=W+'/final_package'
def nm(x): return (x or '').replace('\u2212','-').replace('–','-').replace('—','-').strip()
def ptok(x):
    x=nm(x)
    if x.upper() in ('EVEN','EV','PK'): return '+100'
    return x
def fnum(x):
    try: return float(nm(x).replace('+',''))
    except: return None
def textnorm(s): return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s).replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')).strip()
def iso(t):
    if not t or t=='null': return None
    return dt.datetime.fromisoformat(t.replace('Z','+00:00')).astimezone(dt.timezone.utc)
def ts14(t): return dt.datetime.strptime(t[:14],'%Y%m%d%H%M%S').replace(tzinfo=dt.timezone.utc)
# ------------------------------------------------------------------ inputs
O=list(csv.DictReader(open(W+'/ncaa_lacrosse_historical_odds_2025.csv')))
N=list(csv.DictReader(open(DL+'/ncaa_lacrosse_additional_odds_2023_2026.csv')))
C=list(csv.DictReader(open(DL+'/ncaa_lacrosse_odds_combined_normalized.csv')))
Corig={r['orig_record_id']:r for r in C if r['origin']=='original'}
Cnew=[r for r in C if r['origin']=='new']; assert len(Cnew)==len(N)==525 and len(O)==1470
X={r['odds_game_id']:r for r in csv.DictReader(open(FP+'/odds_game_to_ncaa_game_crosswalk.csv'))}
NG={}
for f in ['ncaa_lacrosse_games_2023.csv','ncaa_lacrosse_games_2024.csv','ncaa_lacrosse_game_index_2025.csv']:
    for g in csv.DictReader(open(FP+'/'+f)): NG[g['game_id']]=g
LIVE={l.split('\t')[0]:l.rstrip('\n').split('\t')[1:] for l in open(OUT+'/url_status_live.tsv')}
# team canonicalisation for orientation
AL={'ohio st.':'ohio state','penn st.':'penn state','penn st':'penn state','massachusetts':'umass','umass':'umass','ualbany':'albany','albany':'albany','loyola maryland':'loyola (md)','loyola md':'loyola (md)','loyola':'loyola (md)',
 'boston university':'boston u','boston u':'boston u','bu':'boston u',"st. joe's":"saint joseph's","saint josephs":"saint joseph's","st. joseph's":"saint joseph's","saint joseph's":"saint joseph's",'pennsylvania':'penn','unc':'north carolina','hopkins':'johns hopkins','jhu':'johns hopkins',
 'army west point':'army','mount st. mary\'s':"mount st. mary's",'mount saint marys':"mount st. mary's",'saint bonaventure':'st. bonaventure','st. bonaventure':'st. bonaventure',"st. john's - new york":"st. john's","st. john's (ny)":"st. john's",'umass lowell':'umass lowell','boston u.':'boston u','cleveland st.':'cleveland state','loyola maryland':'loyola (md)','richmond university':'richmond','boston university terriers':'boston u','detroit':'detroit mercy','lemoyne':'le moyne','liu post':'liu','long island':'liu'}
def ct(t):
    t=textnorm(t or '').lower(); t=re.sub(r'^(no\. ?|#)\d+ ','',t).strip(); return AL.get(t,t)
# ------------------------------------------------------------------ raw evidence loaders
def an_article(path):
    s=open(path,errors='ignore').read()
    m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',s,re.S)
    if not m: return None
    a=json.loads(m.group(1))['props']['pageProps'].get('article')
    return a
AN={}   # canonical url -> (file, article)
for f in glob.glob(W+'/an/a_*.html'):
    a=an_article(f)
    if not a: continue
    for u in {a.get('canonical_url'),a.get('url')}:
        if u: AN.setdefault(u.rstrip('/'),(f,a))
for l in open(W+'/an/map.txt'):
    f,u=l.split(); 
    if u.rstrip('/') not in AN:
        a=an_article(W+'/an/'+f)
        if a: AN[u.rstrip('/')]=(W+'/an/'+f,a)
def an_lookup(u):
    u=u.rstrip('/')
    for k in (u,u.replace('/lacrosse-lacrosse/','/lacrosse/'),u.replace('/lacrosse/','/lacrosse-lacrosse/')):
        if k in AN: return AN[k]
    slug=u.split('/')[-1]
    for k,v in AN.items():
        if k.split('/')[-1]==slug: return v
    return None
ANWB={os.path.basename(f)[:14]:f for f in glob.glob(W+'/an_wb/*.html')}
def tables_from_html(html,kind):
    """Generic re-extraction of odds tables -> list of dict(title, teams{label:(spread,price)}, total, book, text)."""
    soup=BeautifulSoup(html,'lxml'); out=[]
    for tab in soup.find_all('table'):
        trs=[[textnorm(td.get_text(' ',strip=True)) for td in tr.find_all(['td','th'])] for tr in tab.find_all('tr')]
        cells=[c for r in trs for c in r]
        h=tab.find_previous(['h2','h3','h4']); title=textnorm(h.get_text(' ',strip=True)) if h else ''
        book=None
        anchor=tab.find_parent('figure') or tab
        for sib in anchor.find_next_siblings(limit=3):
            st_=textnorm(sib.get_text(' ',strip=True))
            m2=re.search(r'Spread/moneyline odds via\s+(\w+)\s+and total via\s+(\w+)',st_,re.I)
            if m2: book={'moneyline':m2.group(1),'spread':m2.group(1),'total':m2.group(2)}; break
            m=re.search(r'Odds via\s+([^.]+)',st_)
            if m: book=m.group(1).strip(); break
            if sib.name in ('table','h2','h3','figure'): break
        if not book:
            for c in cells:
                m=re.search(r'Odds via\s+([^.]+)',c)
                if m: book=m.group(1).strip()
        teams={}; total=None
        if kind=='bol':
            for r in trs:
                if len(r)==2 and 'Moneyline' in r[0]:
                    lab=re.sub(r'\s*Moneyline\s*/\s*Spread.*','',r[0]).strip(); parts=[ptok(p) for p in r[1].split('/')]
                    teams[lab]=(parts[1] if len(parts)>1 else None, parts[0] if parts else None)
                if len(r)==2 and r[0]=='Total': total=nm(r[1])
        else:
            pairs=list(zip(cells[0::2],cells[1::2]))
            for k,v in pairs:
                if k in ('Total','Time','TV','Pick','Day/Time','Day · Time','Day ⋅ Time'):
                    if k=='Total': total=nm(v)
                    continue
                m=re.match(r'^(.*?)\s*(?:\(([+\-−–]?\d+(?:\.\d+)?)\))?\s*(?:Odds)?$',k)
                if not m: continue
                pm=re.search(r'([+\-−–]\d+|EVEN|Even|PK)',v)
                teams[m.group(1).strip()]=(nm(m.group(2)) if m.group(2) else None, ptok(pm.group(1)) if pm else None)
        if teams: out.append(dict(title=title,teams=teams,total=total,book=book))
    return out
def normbook(b,mk=None):
    if isinstance(b,dict): b=b.get(mk)
    if not b: return None
    b=re.sub(r'\s*Sportsbook\.?$','',b.strip()).strip().rstrip('.')
    return {'Caesars Sportsbook':'Caesars'}.get(b,b)
BOL={}
for f in glob.glob(W+'/bol/*.html'):
    s=open(f,errors='ignore').read(); m=re.search(r'<link rel="canonical" href="([^"]+)"',s)
    if m: BOL[m.group(1).rstrip('/')]=f
BOLWB=DL+'/raw_new/bol_wb/week4sat_20250301181913.html'
LSB=DL+'/raw_new/lsb_article.html'
DKSNAP={os.path.basename(f)[3:17]:f for f in glob.glob(W+'/wb/dk_*.html')}
_dkcache={}
def dk_offer(ts,oid,eid):
    if ts not in _dkcache: _dkcache[ts]=open(DKSNAP[ts],errors='ignore').read() if ts in DKSNAP else None
    s=_dkcache[ts]
    if s is None: return None,None
    D=json.JSONDecoder(); off=ev=None
    for m in re.finditer(re.escape('{"providerOfferId":"%s"'%oid),s):
        try: off,_=D.raw_decode(s[m.start():]); break
        except: pass
    for m in re.finditer(re.escape('{"eventId":"%s"'%eid),s):
        try:
            o,_=D.raw_decode(s[m.start():])
            if 'startDate' in o: ev=o; break
        except: pass
    return off,ev
NASH={}
for f in glob.glob(DL+'/raw_new/dknash_*.json'):
    b=open(f,'rb').read()
    try: b=gzip.decompress(b)
    except OSError: pass
    j=json.loads(b); ts=os.path.basename(f)[7:21]
    NASH[ts]=(f,{s['id']:s for s in j['selections']},{m['id']:m for m in j['markets']},{e['id']:e for e in j['events']})
MGM={}
for l in open(DL+'/raw_new/mgm/map.txt'):
    ts,u=l.split()[:2]
    fs=glob.glob(DL+f'/raw_new/mgm/mgm_{ts}*.html')
    if fs: MGM.setdefault(ts,[]).extend(fs)
for f in glob.glob(DL+'/raw_new/mgm/mgm_*.html'):
    ts=os.path.basename(f)[4:18]; MGM.setdefault(ts,[]); 
    if f not in MGM[ts]: MGM[ts].append(f)
_mgmcache={}
def mgm_event_groups(ts,eid):
    for f in MGM.get(ts,[]):
        if f not in _mgmcache: _mgmcache[f]=open(f,errors='ignore').read()
        s=_mgmcache[f]; i=s.find(f'-{eid}"')
        if i<0: continue
        st=s.rfind('<ms-six-pack-event',0,i); en=s.find('<ms-six-pack-event',i); blk=s[st:en if en>0 else st+40000]
        names=[textnorm(re.sub(r'<[^>]+>','',x)) for x in re.findall(r'<div class="participant[^"]*">(.*?)<span',blk,re.S)]
        groups=[]
        for g in re.findall(r'<ms-option-group.*?</ms-option-group>',blk,re.S):
            opts=[]
            for o in re.findall(r'<ms-option .*?</ms-option>',g,re.S):
                a=re.search(r'option-attribute[^>]*>(.*?)</div>',o,re.S); v=re.search(r'option-value[^>]*>(?:<[^>]+>)*\s*([^<]+?)\s*<',o,re.S)
                opts.append((textnorm(a.group(1)) if a else None, textnorm(v.group(1)) if v else None))
            groups.append(opts)
        return f,names,groups
    return None,None,None
LAS={}
for f in glob.glob(DL+'/raw_new/las/*.html'): LAS['https://laxallstars.com/articles/'+os.path.basename(f)[:-5]]=f
_txt={}
def text_of(f):
    if f not in _txt: _txt[f]=textnorm(BeautifulSoup(open(f,errors='ignore').read(),'lxml').get_text(' ',strip=True))
    return _txt[f]
# ------------------------------------------------------------------ table matching helpers
def pick_table(tabs,title,labels):
    labs={ct(l) for l in labels if l and l not in ('Over','Under','Over/Under')}
    for t in tabs:
        if title and textnorm(title)==t['title']: return t
    for t in tabs:
        if labs and labs<= {ct(k) for k in t['teams']}: return t
    return None
def check_table(t,market,side,line,price):
    """returns (line_ok, price_ok, detail)"""
    if t is None: return False,False,'table not found'
    if market=='total':
        tot=t['total'] or ''; m=re.match(r'^(\d+(?:\.\d+)?)\s*(?:\(([+\-]\d+)\))?',tot)
        lok= bool(m) and fnum(m.group(1))==fnum(line)
        pok= (price is None) or (m and m.group(2)==price)
        return lok,pok,f'Total cell "{tot}"'
    lab=None
    for k in t['teams']:
        if k==side or ct(k)==ct(side): lab=k
    if lab is None: return False,False,f'side {side} not in table teams {list(t["teams"])}'
    sp,pr=t['teams'][lab]
    if market=='moneyline': return True,(pr==price),f'{lab}: price cell {pr}'
    if market=='spread':
        lok = sp is not None and fnum(sp)==fnum(line)
        if sp is None:  # header form "Fav (-x) vs. Dog"
            hm=re.match(r'^(?:No\. \d+ )?(.+?)\s*(?:\(([+\-]?\d+(?:\.\d+)?)\))?\s+(?:vs\.?|at)\s+(?:No\. \d+ )?(.+?)\s*(?:\(([+\-]?\d+(?:\.\d+)?)\))?(?:\s+Odds)?$',t['title'])
            if hm and (hm.group(2) or hm.group(4)):
                fav,ln=(hm.group(1),hm.group(2)) if hm.group(2) else (hm.group(3),hm.group(4))
                if ct(fav)==ct(lab): lok=fnum(ln)==fnum(line); return lok,(price is None),f'header "{t["title"]}" printed line {ln} for {fav}'
                return False,(price is None),f'IMPLIED: header "{t["title"]}" prints only {fav} {ln}; this side is a negation (not printed)'
        return lok,(price is None or pr==price),f'{lab}: spread cell {sp}'
    return False,False,'unknown market'
# ------------------------------------------------------------------ verification per record
def verify(rec):
    """rec: dict with unified fields + 'kind'. Returns dict(verified_in_raw, book_supported, detail, evidence_file, archive_match)"""
    k=rec['kind']; side=rec['selection']; mk=rec['market']; line=rec['line']; price=rec['price']; book=rec['book']
    R=dict(verified_in_raw=False,book_supported=False,detail='',evidence_file=None,archive_match=None,implied=False)
    if k=='dk_snapshot':
        ts=rec['archive_url'].split('/web/')[1][:14]; oid=re.search(r'offerId (\S+?);',rec['notes']).group(1); eid=re.search(r'DK eventId (\d+)',rec['notes']).group(1)
        off,ev=dk_offer(ts,oid,eid); R['evidence_file']=DKSNAP.get(ts)
        if off:
            hit=[o for o in off['outcomes'] if o.get('label')==side and ptok(o.get('oddsAmerican'))==price and (line is None or (o.get('line') is not None and abs(float(o['line'])-fnum(line))<1e-9))]
            R['verified_in_raw']=bool(hit); R['book_supported']=True
            R['detail']=f"DK offer {oid} (eventGroupId {off.get('eventGroupId')}) outcomes: "+'; '.join(f"{o.get('label')} {o.get('line','')} {ptok(o.get('oddsAmerican'))}" for o in off['outcomes'])
            if ev: R['detail']+=f" | event '{ev.get('name')}' start {ev.get('startDate')} teamName1={ev.get('teamName1')} teamName2={ev.get('teamName2')}"
        else: R['detail']='offer id not found in raw snapshot'
    elif k in ('an_article','an_archive'):
        if k=='an_archive':
            ts=rec['archive_url'].split('/web/')[1][:14]; f=ANWB.get(ts); a=an_article(f) if f else None
        else:
            v=an_lookup(rec['source_url']); f,a=(v if v else (None,None))
        R['evidence_file']=f
        if not a: R['detail']='raw article not found'; return R
        if rec['is_opening']:
            q=re.search(r'"(.+?)"\.? ?quote_timestamp|: "(.+)"\. quote',rec['notes'])
            q=re.search(r'\(not a snapshot\): "(.*?)"\. quote_timestamp',rec['notes']).group(1)
            t=textnorm(BeautifulSoup(a['html'],'lxml').get_text(' ',strip=True)); qn=textnorm(q)
            R['verified_in_raw']= qn in t or qn.replace('"','') in t.replace('"','')
            R['book_supported']= bool(book) and book.lower() in qn.lower()
            R['detail']=f'opening quote {"found" if R["verified_in_raw"] else "NOT found"} in article text: {q[:150]}'
            return R
        tabs=tables_from_html(a['html'],'an'); t=pick_table(tabs,rec['event_name'],[rec['home_team'],rec['away_team'],side])
        lok,pok,d=check_table(t,mk,side,line,price)
        R['implied']='IMPLIED' in d
        R['verified_in_raw']= lok and pok if mk!='moneyline' else pok
        tb=normbook(t['book'],mk) if t else None
        R['book_supported']= bool(book) and tb==book
        R['detail']=f"table '{t['title'] if t else None}' book='{tb}'; {d}"
        if rec['archive_url'] and k=='an_article':
            ts=rec['archive_url'].split('/web/')[1][:14]; fw=ANWB.get(ts); aw=an_article(fw) if fw else None
            if aw:
                tw=pick_table(tables_from_html(aw['html'],'an'),rec['event_name'],[rec['home_team'],rec['away_team'],side])
                l2,p2,d2=check_table(tw,mk,side,line,price)
                R['archive_match']= (l2 and p2 if mk!='moneyline' else p2) and (normbook(tw['book'],mk) if tw else None)==book
                R['detail']+=f" | archive {ts}: {d2}; book='{normbook(tw['book'],mk) if tw else None}'"
            R['archive_file']=fw
    elif k=='bol':
        f=BOL.get(rec['source_url'].rstrip('/')); R['evidence_file']=f
        if not f: R['detail']='raw article not found'; return R
        html=open(f,errors='ignore').read()
        if rec['is_opening']:
            q=re.search(r'\(not a snapshot\): "(.*?)"\. quote_timestamp',rec['notes']).group(1); t=text_of(f)
            R['verified_in_raw']=textnorm(q) in t; R['book_supported']=bool(book) and book.lower() in q.lower()
            R['detail']=f'opening quote {"found" if R["verified_in_raw"] else "NOT found"}: {q[:150]}'; return R
        t=pick_table(tables_from_html(html,'bol'),rec['event_name'],[rec['home_team'],rec['away_team'],side])
        lok,pok,d=check_table(t,mk,side,line,price)
        R['verified_in_raw']= lok and pok if mk!='moneyline' else pok
        tb=normbook(t['book'],mk) if t else None; R['book_supported']=bool(book) and tb==book
        R['detail']=f"table '{t['title'] if t else None}' book='{tb}'; {d}"
        if rec.get('archive_url') and '20250301181913' in rec['archive_url']:
            tw=pick_table(tables_from_html(open(BOLWB,errors='ignore').read(),'bol'),rec['event_name'],[rec['home_team'],rec['away_team'],side])
            l2,p2,d2=check_table(tw,mk,side,line,price); R['archive_match']=(l2 and p2 if mk!='moneyline' else p2); R['archive_file']=BOLWB
            R['detail']+=f' | archive 20250301181913: {d2}'
    elif k=='lsb':
        f=LSB; R['evidence_file']=f; t=text_of(f); i=t.find('Game Odds'); seg=t[i:i+200]
        pat={('spread','North Carolina'):r'UNC \+1\.5 \(-144\)',('spread','Notre Dame'):r'Notre Dame -1\.5 \(\+118\)',('moneyline','North Carolina'):r'\(-144\) \+100',('moneyline','Notre Dame'):r'\(\+118\) -122',('total','Over'):r'O 22\.5 \(-105\)',('total','Under'):r'U 22\.5 \(-115\)'}.get((mk,side))
        ok=bool(pat and re.search(pat,seg)); exp={('spread','North Carolina'):('+1.5','-144'),('spread','Notre Dame'):('-1.5','+118'),('moneyline','North Carolina'):(None,'+100'),('moneyline','Notre Dame'):(None,'-122'),('total','Over'):('22.5','-105'),('total','Under'):('22.5','-115')}.get((mk,side))
        R['verified_in_raw']=ok and exp==(line,price); R['book_supported']=False; R['detail']=f'LSB "Game Odds" table: {seg[:160]} (no sportsbook named; page re-fetched live 2026-11-10)'
    elif k=='dk_nash':
        ts=rec['archive_url'].split('/web/')[1][:14]; f,S,M,E=NASH[ts]; R['evidence_file']=f
        sid=re.search(r'selection id ([^;]+);',rec['notes']).group(1).strip(); s=S.get(sid)
        if s:
            m=M[s['marketId']]; e=E[m['eventId']]; pts=s.get('points')
            okp=ptok(s['displayOdds']['american'])==price; okl=(line is None and pts is None) or (pts is not None and fnum(line)==float(pts))
            R['verified_in_raw']=okp and okl and s['label']==side; R['book_supported']=True
            R['detail']=f"DK selection {sid} label={s['label']} points={pts} american={ptok(s['displayOdds']['american'])} event {e['name']} {e['startEventDate']} status={e['status']}"
        else: R['detail']='selection id not found'
    elif k=='betmgm':
        ts=rec['archive_url'].split('/web/')[1][:14]; f,names,groups=mgm_event_groups(ts,rec['event_id']); R['evidence_file']=f
        if not groups: R['detail']='event block not found'; return R
        gi={'spread':0,'total':1,'moneyline':2}[mk]
        if len(groups)<3: R['detail']=f'only {len(groups)} option groups'; return R
        idx=None
        if mk=='total': idx=0 if side=='Over' else 1
        else:
            if names and ct(side)==ct(names[0]): idx=0
            elif names and len(names)>1 and ct(side)==ct(names[1]): idx=1
        opts=groups[gi]
        if idx is None or idx>=len(opts): R['detail']=f'selection not mapped; names={names}'; return R
        attr,val=opts[idx]
        want=rec['price_displayed']
        lok=(line is None) or (attr is not None and fnum(re.sub(r'^[OU]\s*','',attr))==fnum(line))
        R['verified_in_raw']= lok and val is not None and nm(val)==nm(str(want)); R['book_supported']=True
        R['detail']=f"BetMGM event {rec['event_id']} names={names} group[{gi}] option[{idx}] attr='{attr}' value='{val}' (row displayed={want}, american={price})"
    elif k=='las':
        f=LAS.get(rec['source_url']); R['evidence_file']=f
        q=re.search(r'printed text: "(.*?)"; quote time',rec['notes']).group(1); t=text_of(f)
        parts=[p.strip() for p in q.split('...')]
        R['verified_in_raw']=all(textnorm(p) in t for p in parts)
        R['book_supported']= bool(book) and ('DraftKings' in t)
        R['detail']=f'printed text {"found" if R["verified_in_raw"] else "NOT found"}: {q[:150]}'+('; article states DraftKings as odds source' if R['book_supported'] else '')
    return R
# ------------------------------------------------------------------ build unified records
recs=[]
for r in O:
    dom=r['source_url'].split('/')[2]; c=Corig[r['record_id']]
    if dom=='sportsbook.draftkings.com': kind='dk_snapshot'
    elif dom=='www.actionnetwork.com': kind='an_archive' if r['source_type']=='archive_snapshot' else 'an_article'
    elif dom=='betonlacrosse.com': kind='bol'
    else: kind='lsb'
    recs.append(dict(record_id='O%04d'%int(r['record_id']),orig_record_id=r['record_id'],dataset='original',kind=kind,game_id=c['game_id'],orig_game_id=r['game_id'],season=r['season'],
        book=r['sportsbook'] or None,market=r['market'],selection=r['side'],line=r['line'] or None,price=r['price_american'] or None,is_opening=r['opening_or_closing']=='opening',
        source_url=r['source_url'],archive_url=(c['archive_url'] if c['archive_url']!='null' else None),event_name=r['event_name'],home_team=r['home_team'],away_team=r['away_team'],notes=r['notes'],
        quote_capture_timestamp=c['quote_capture_timestamp'] if c['quote_capture_timestamp']!='null' else None,article_published_at=c['article_published_at'] if c['article_published_at']!='null' else None,
        article_modified_at=c['article_modified_at'] if c['article_modified_at']!='null' else None,archive_capture_timestamp=c['archive_capture_timestamp'] if c['archive_capture_timestamp']!='null' else None,
        source_start=r['game_start_time'] or None,grade_original=r['evidence_quality'],event_id=None,price_displayed=None))
mgm={}
for x in json.load(open(DL+'/raw_new/mgm/mgm_rows.json')): mgm[(x['bookmaker_event_id'],x['market'],x['selection'],x['archive_capture_timestamp'])]=x
for i,(r,c) in enumerate(zip(N,Cnew),1):
    d=r['source_url'].split('/')[2]; kind={'sportsbook-nash.draftkings.com':'dk_nash','sports.betmgm.com':'betmgm','laxallstars.com':'las'}[d]
    g=lambda k:(None if r[k]=='null' else r[k])
    pdsp=None
    if kind=='betmgm': pdsp=mgm[(r['bookmaker_event_id'],r['market'],r['selection'],r['archive_capture_timestamp'])]['price_as_displayed']
    recs.append(dict(record_id='N%04d'%i,orig_record_id=None,dataset='additional',kind=kind,game_id=r['game_id'],orig_game_id=r['game_id'],season=r['season'],book=g('sportsbook'),market=r['market'],selection=r['selection'],
        line=g('line'),price=g('american_odds'),is_opening=r['is_opening']=='True',source_url=r['source_url'],archive_url=g('archive_url'),event_name=None,home_team=g('home_team'),away_team=g('away_team'),notes=r['notes'],
        quote_capture_timestamp=g('quote_capture_timestamp'),article_published_at=g('article_published_at'),article_modified_at=g('article_modified_at'),archive_capture_timestamp=g('archive_capture_timestamp'),
        source_start=g('scheduled_start_time'),grade_original=r['evidence_grade'],event_id=g('bookmaker_event_id'),price_displayed=pdsp))
# ------------------------------------------------------------------ run verification
for rec in recs: rec.update(verify(rec))
# ------------------------------------------------------------------ NCAA crosswalk / orientation / start time
def ncaa_start(g):
    if not g: return None
    s=g.get('start_time_utc') or ''
    if not s or g.get('start_time_is_tba')=='True': return None
    t=iso(s)
    if 4<=t.hour<=10 and t.minute==0: return None   # midnight-local placeholder, not a real start time
    return t
for rec in recs:
    x=X.get(rec['game_id']); rec['crosswalk_status']=x['match_status'] if x else 'not_in_crosswalk'
    rec['ncaa_game_id']=x['ncaa_game_id'] if x and x['ncaa_game_id'] else None
    g=NG.get(rec['ncaa_game_id']) if rec['ncaa_game_id'] else None
    rec['ncaa_game_date']=g['game_date'] if g else None; rec['ncaa_home']=g['home_team'] if g else None; rec['ncaa_away']=g['away_team'] if g else None
    rec['neutral_site']=(g.get('neutral_site') or None) if g else None
    # orientation of selection
    sel=ct(rec['selection'])
    if rec['market']=='total' or rec['selection'] in ('Over','Under') or 'Over/Under' in (rec['selection'] or ''): rec['selection_role']='n/a (total)'; rec['orientation_source']='n/a'
    elif g:
        h,a=ct(g['home_team']),ct(g['away_team'])
        rec['selection_role']='home' if sel==h else ('away' if sel==a else 'UNMATCHED_TEAM_LABEL'); rec['orientation_source']='ncaa_crosswalk'+(' (neutral site)' if rec['neutral_site'] in ('True','true') else '')
    elif rec['kind']=='dk_nash':
        rec['selection_role']='home' if sel==ct(rec['home_team']) else ('away' if sel==ct(rec['away_team']) else 'UNMATCHED_TEAM_LABEL'); rec['orientation_source']='draftkings_venueRole (no NCAA file for 2026)'
    else: rec['selection_role']='unknown'; rec['orientation_source']='unknown (no NCAA match)'
    st=ncaa_start(g); rec['start_basis']='ncaa_start_time' if st else ('source_listed_start' if rec['source_start'] else 'none')
    rec['start_utc']=st or iso(rec['source_start'])
    if g and rec['source_start'] and iso(rec['source_start']):
        from zoneinfo import ZoneInfo
        sd=iso(rec['source_start']).astimezone(ZoneInfo('America/New_York')).date().isoformat()
        rec['date_vs_ncaa']='same' if sd==g['game_date'] else f'DIFFERS: source {sd} vs NCAA {g["game_date"]}'
    else: rec['date_vs_ncaa']=None
# ------------------------------------------------------------------ grade re-justification & line type
STALE='2025-02-16T18:09:23Z'
for rec in recs:
    st=rec['start_utc']; reasons=[]
    cap = iso(rec['quote_capture_timestamp']) if rec['kind'] in ('dk_snapshot','dk_nash','betmgm') else None
    arc = iso(rec['archive_capture_timestamp']) if rec['kind'] in ('an_article','an_archive','bol') and rec['archive_url'] else None
    pub = iso(rec['article_published_at'])
    ok = rec['verified_in_raw'] and rec['book_supported']
    if rec['kind']=='an_archive': arc=iso(rec['archive_capture_timestamp']); rec['archive_match']=rec['verified_in_raw']
    indep_pre = False
    if cap and st and cap<st: indep_pre=True; reasons.append(f'sportsbook snapshot {cap:%Y-%m-%dT%H:%MZ} < start {st:%Y-%m-%dT%H:%MZ} ({rec["start_basis"]})')
    if arc and st and arc<st and rec.get('archive_match'): indep_pre=True; reasons.append(f'archive capture {arc:%Y-%m-%dT%H:%MZ} < start and shows same value')
    if arc and rec.get('archive_match') is False: reasons.append('archive capture does NOT show the same value')
    stale = rec['kind']=='betmgm' and rec['archive_capture_timestamp']==STALE
    pub_pre = bool(pub and st and pub<st)
    if rec['kind']=='betmgm' and 'countdown' in rec['notes']: pass
    if not rec['verified_in_raw']: g='C'; reasons.insert(0,'value not verified in raw evidence')
    elif not rec['book_supported']: g='C'; reasons.insert(0,'sportsbook not named/supported by source')
    elif indep_pre and not stale: g='A'
    elif stale: g='B'; reasons.append('stale BetMGM render: pre-game per BetMGM countdown text, capture time not the render time')
    elif pub_pre: g='B'; reasons.append(f'article published {pub:%Y-%m-%dT%H:%MZ} before start; no independent capture')
    else:
        g='C'; reasons.append('pre-game status not established (start time unknown or publication not before start)' if not pub_pre else '')
    if rec['kind']=='dk_snapshot' and 'event_state_at_capture=STARTED' in rec['notes']: g='C'; reasons.append('event state STARTED at capture')
    rec['grade_audited']=g; rec['grade_reason']='; '.join(x for x in reasons if x)
    rec['pre_game_published']= pub_pre if pub else None
    rec['independent_capture_pre_game']=indep_pre and not stale
    if rec['is_opening'] and rec['verified_in_raw']: rec['line_type']='opening (source text explicitly says opened)'
    elif g in ('A','B'): rec['line_type']='unspecified pre-game'
    else: rec['line_type']='unknown'
    rec['is_closing']=False
json.dump(recs,open(OUT+'/_recs_stage1.json','w'),default=str)
print('stage1',len(recs),collections.Counter((r['kind'],r['verified_in_raw'],r['book_supported']) for r in recs))
