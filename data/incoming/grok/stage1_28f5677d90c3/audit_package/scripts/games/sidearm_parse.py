"""Parse a saved Sidearm schedule HTML (classic 'sidearm-schedule-game' list or next-gen 's-game-card' template) into rows:
date, marker (vs/at, home/away/neutral class when present), opponent, result W/L/T, score as shown (winner first), ot flag, location."""
import re, sys, html as H, pandas as pd
from bs4 import BeautifulSoup as B
MON = "Jan Feb Mar Apr May Jun".split()
def _date(s, season):
    m = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun)[a-z]*\.? (\d{1,2})\b", s)
    return f"{season}-{MON.index(m.group(1)) + 1:02d}-{int(m.group(2)):02d}" if m else None
def _res(s):
    m = re.search(r"\b(W|L|T)\s*,\s*(\d+)\s*-\s*(\d+)(\s*\(?\s*(\d?OT)\s*\)?)?", s)
    return (m.group(1), f"{m.group(2)}-{m.group(3)}", bool(m.group(5))) if m else (None, None, False)
def text(h):  # kept for evidence .txt
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    t = H.unescape(re.sub(r"<[^>]+>", "\n", t)); return [l.strip() for l in t.split("\n") if l.strip()]
def parse(path, season=None):
    season = season or int(re.search(r"(20\d\d)", path.split("/")[-1]).group(1))
    s = B(open(path, encoding="utf-8", errors="ignore").read(), "html.parser"); rows = []
    for li in s.select("li.sidearm-schedule-game"):
        cls = li.get("class"); g = lambda c: (li.select_one(c).get_text(" ", strip=True) if li.select_one(c) else "")
        r, sc, ot = _res(g(".sidearm-schedule-game-result"))
        ha = "home" if "sidearm-schedule-home-game" in cls else "away" if "sidearm-schedule-away-game" in cls else "neutral" if "sidearm-schedule-neutral-game" in cls else None
        rows.append(dict(date=_date(g(".sidearm-schedule-game-opponent-date"), season), opponent=g(".sidearm-schedule-game-opponent-name"),
                         marker=g(".sidearm-schedule-game-home") or g(".sidearm-schedule-game-away") or None, ha_class=ha, result=r, score=sc, ot=ot,
                         loc=g(".sidearm-schedule-game-location"), template="classic"))
    for c in s.select("div.s-game-card"):
        t = c.get_text("\n", strip=True); one = " ".join(t.split("\n"))
        st = c.select_one(".s-stamp__text"); op = c.select_one('[data-test-id="s-game-card-standard__header-team-opponent-link"]') or c.select_one('[data-test-id*="opponent-name"]')
        r, sc, ot = _res(one)
        loc = c.select_one('[data-test-id*="location"]')
        rows.append(dict(date=_date(one, season), opponent=op.get_text(" ", strip=True) if op else None, marker=st.get_text(strip=True) if st else None, ha_class=None,
                         result=r, score=sc, ot=ot, loc=loc.get_text(" ", strip=True) if loc else None, template="nextgen"))
    return pd.DataFrame(rows, columns=["date", "opponent", "marker", "ha_class", "result", "score", "ot", "loc", "template"])
if __name__ == "__main__":
    print(parse(sys.argv[1]).to_string())
