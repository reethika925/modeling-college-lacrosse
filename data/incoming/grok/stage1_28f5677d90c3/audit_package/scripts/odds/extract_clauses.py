import sys,re
from bs4 import BeautifulSoup
KW=re.compile(r'scrap|robot|spider|crawl|automated|data min|harvest|bot\b|reproduc|redistribut|non-?commercial|personal use|research|copy,|extract',re.I)
for f in sys.argv[1:]:
    t=BeautifulSoup(open(f,errors='ignore').read(),'lxml').get_text(' ',strip=True)
    sents=re.split(r'(?<=[.;])\s+',t)
    hits=[s for s in sents if KW.search(s)]
    print('=====',f,len(t),len(hits))
    for s in hits[:14]: print(' -',s[:420])
