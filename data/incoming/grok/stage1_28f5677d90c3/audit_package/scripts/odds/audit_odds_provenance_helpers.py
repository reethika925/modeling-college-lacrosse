import re,unicodedata
def textnorm(s): return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",s).replace("’","'").replace("‘","'").replace("“",'"').replace("”",'"')).strip()
AL={'ohio st.':'ohio state','penn st.':'penn state','penn st':'penn state','massachusetts':'umass','umass':'umass','ualbany':'albany','albany':'albany','loyola maryland':'loyola (md)','loyola md':'loyola (md)','loyola':'loyola (md)',
 'boston university':'boston u','boston u':'boston u','bu':'boston u',"st. joe's":"saint joseph's","saint josephs":"saint joseph's","st. joseph's":"saint joseph's","saint joseph's":"saint joseph's",'pennsylvania':'penn','unc':'north carolina','hopkins':'johns hopkins','jhu':'johns hopkins',
 'army west point':'army','mount st. mary\'s':"mount st. mary's",'mount saint marys':"mount st. mary's",'saint bonaventure':'st. bonaventure','st. bonaventure':'st. bonaventure',"st. john's - new york":"st. john's","st. john's (ny)":"st. john's",'umass lowell':'umass lowell','boston u.':'boston u','cleveland st.':'cleveland state','loyola maryland':'loyola (md)','richmond university':'richmond','boston university terriers':'boston u','detroit':'detroit mercy','lemoyne':'le moyne','liu post':'liu','long island':'liu'}
def ct(t):
    t=textnorm(t or '').lower(); t=re.sub(r'^(no\. ?|#)\d+ ','',t).strip(); return AL.get(t,t)
