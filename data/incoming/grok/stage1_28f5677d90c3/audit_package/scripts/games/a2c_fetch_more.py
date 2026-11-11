"""Politely fetch official school schedule pages (Sidearm) used as evidence. robots.txt checked per host; 31 s between requests.
Saved untouched to evidence/<host>_<season>_schedule.html; fetch log in evidence/fetch_log.tsv."""
import os, time, urllib.request, urllib.robotparser, datetime as dt
UA = "Mozilla/5.0 (academic research; SBU CSE519 lacrosse project)"
T = [("goprincetontigers.com", 2024), ("mountathletics.com", 2023)]
os.makedirs("evidence", exist_ok=True); log = open("evidence/fetch_log.tsv", "a")
for host, s in T:
    fn = f"evidence/{host}_{s}_schedule.html"
    if os.path.exists(fn): continue
    url = f"https://{host}/sports/mens-lacrosse/schedule/{s}"
    rp = urllib.robotparser.RobotFileParser(f"https://{host}/robots.txt")
    try: rp.read(); allowed = rp.can_fetch(UA, url)
    except Exception as e: allowed = None
    if allowed is False: log.write(f"{dt.datetime.now().isoformat()}\t{url}\tROBOTS_DISALLOW\n"); continue
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40) as r:
            open(fn, "wb").write(r.read()); code = r.status
    except Exception as e: code = getattr(e, "code", str(e))
    log.write(f"{dt.datetime.now().isoformat()}\t{url}\t{code}\trobots_allowed={allowed}\n"); log.flush(); print(host, s, code, flush=True)
    time.sleep(31)
