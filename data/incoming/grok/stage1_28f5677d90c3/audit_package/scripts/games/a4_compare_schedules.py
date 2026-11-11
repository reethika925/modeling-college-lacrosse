"""Compare every game of each fetched official school schedule with our NCAA-derived game rows for that team-season."""
import sys, os, re, glob, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); from sidearm_parse import parse
FP = "/workspace/final_package"
HOST = {"highpointpanthers.com": "high-point", "navysports.com": "navy", "merrimackathletics.com": "merrimack", "brownbears.com": "brown", "gomarquette.com": "marquette",
        "gocrimson.com": "harvard", "umbcretrievers.com": "umbc", "mercerbears.com": "mercer", "guhoyas.com": "georgetown", "hopkinssports.com": "johns-hopkins",
        "gobobcats.com": "quinnipiac", "gojaspers.com": "manhattan", "ionagaels.com": "iona", "liuathletics.com": "long-island", "stonybrookathletics.com": "stony-brook",
        "fairfieldstags.com": "fairfield", "goriverhawks.com": "umass-lowell", "lemoynedolphins.com": "le-moyne", "binghamton": "binghamton",
        "goholycross.com": "holy-cross", "goprincetontigers.com": "princeton", "mountathletics.com": "mt-st-marys", "detroittitans.com": "detroit", "uvmathletics.com": "vermont", "friars.com": "providence", "hamptonpirates.com": "hampton", "cuse.com": "syracuse", "pennathletics.com": "penn"}
G = pd.concat([pd.read_csv(f"{FP}/ncaa_lacrosse_games_2023.csv"), pd.read_csv(f"{FP}/ncaa_lacrosse_games_2024.csv"), pd.read_csv(f"{FP}/ncaa_lacrosse_game_index_2025.csv")])
G["game_id"] = G.game_id.astype(str); al = pd.read_csv(f"{FP}/ncaa_lacrosse_team_aliases.csv").set_index("ncaa_seo")
STOP = {"university", "college", "of", "the", "at", "state", "u", "st.", "-"}
SYN = {"massachusetts": "umass", "pennsylvania": "penn", "albany": "ualbany", "connecticut": "uconn"}
def toks(s):
    w = {w for w in re.findall(r"[a-z]+", str(s).lower()) if w not in STOP}
    return w | {SYN[x] for x in w if x in SYN} | ({"umass"} if "umass" in str(s).lower() and "lowell" not in str(s).lower() else set())
out, unmatched_sched = [], []
for f in sorted(glob.glob("evidence/*_schedule.html")):
    host, season = re.match(r"evidence/(.+?)_(\d{4})_schedule.html", f).groups(); season = int(season)
    seo = HOST.get(host)
    if not seo: continue
    S = parse(f); S = S[S.score.notna()].copy()
    S["ts"] = S.score.str.split("-").str[0].astype(int); S["os"] = S.score.str.split("-").str[1].astype(int)
    a, b = S.ts.copy(), S.os.copy()  # orient by W/L so either "team-first" or "winner-first" display parses the same
    S["ts"] = a.where(((S.result == "W") & (a >= b)) | ((S.result == "L") & (a <= b)) | (S.result == "T"), b)
    S["os"] = b.where(S.ts == a, a)
    mine = G[(G.season == season) & ((G.home_team_seo == seo) | (G.away_team_seo == seo))]
    used = set()
    def _best(g):  # smallest |date gap| to a same-score school game, used to process exact-date games first
        home = g.home_team_seo == seo; ts, os_ = (g.home_score, g.away_score) if home else (g.away_score, g.home_score)
        d = (pd.to_datetime(S.date) - pd.to_datetime(g.game_date)).dt.days.abs()[(S.ts == ts) & (S.os == os_)]
        return d.min() if len(d) else 99
    mine = mine.assign(_b=mine.apply(_best, axis=1)).sort_values("_b")
    for _, g in mine.iterrows():
        home = g.home_team_seo == seo; opp_seo = g.away_team_seo if home else g.home_team_seo; opp = g.away_team if home else g.home_team
        ts, os_ = (g.home_score, g.away_score) if home else (g.away_score, g.home_score)
        ot = toks(opp) | toks(al.ncaa_full.get(opp_seo, "")) | toks(opp_seo)
        S["sim"] = S.opponent.map(lambda o: len(toks(o) & ot))
        S["dd"] = (pd.to_datetime(S.date) - pd.to_datetime(g.game_date)).dt.days
        c = S[(S.sim > 0) & (S.ts == ts) & (S.os == os_) & (S.dd.abs() <= 30) & ~S.index.isin(used)]
        if c.empty: c = S[(S.sim > 0) & (S.dd.abs() <= 3) & ~S.index.isin(used)]; how = "opponent+date (score differs)" if not c.empty else None
        else: how = "opponent+score"
        r = dict(season=season, school_page=f"https://{host}/sports/mens-lacrosse/schedule/{season}", evidence_file=f"evidence/{host}_{season}_schedule.html",
                 team=seo, game_id=g.game_id, our_date=g.game_date, our_home=g.home_team, our_away=g.away_team, our_score=f"{g.home_score}-{g.away_score}",
                 neutral=g.neutral_site, status=g.status)
        if c.empty: r.update(match="no match on school page"); out.append(r); continue
        k = c.dd.abs().idxmin(); s = S.loc[k]; used.add(k)
        r.update(match=how, school_date=s.date, school_opponent=s.opponent, school_marker=s.marker, school_result=f"{s.result} {s.score}", school_loc=s["loc"],
                 date_diff_days=int(s.dd), date_agrees=int(s.dd) == 0,
                 school_ha_class=s.ha_class,
                 homeaway_agrees=(s.ha_class == "neutral" and g.neutral_site == True) or (s.ha_class in (None, "") and s.marker == ("vs" if home else "at")) or (s.ha_class == ("home" if home else "away")) or (s.ha_class == "neutral" and not home), score_agrees=(s.ts == ts and s.os == os_))
        r["homeaway_status"] = "agree" if r["homeaway_agrees"] else ("neutral_or_nominal_home" if (s.marker == "vs" and not home) or (s.ha_class == "neutral") else "conflict")
        out.append(r)
    for k, s in S[~S.index.isin(used)].iterrows(): unmatched_sched.append(dict(season=season, team=seo, school_date=s.date, opponent=s.opponent, marker=s.marker, result=f"{s.result} {s.score}", evidence_file=f))
O = pd.DataFrame(out); O.to_csv("school_schedule_comparison.csv", index=False)
pd.DataFrame(unmatched_sched).to_csv("school_schedule_games_not_in_our_data.csv", index=False)
print(O.groupby(["season", "team"]).agg(n=("game_id", "size"), date_ok=("date_agrees", "sum"), score_ok=("score_agrees", "sum"), ha_ok=("homeaway_agrees", "sum")).to_string())
print(O[(O.date_agrees != True) | (O.score_agrees != True) | (O.homeaway_agrees != True)].drop(columns=["school_page", "evidence_file"]).to_string())
print(pd.DataFrame(unmatched_sched).to_string() if unmatched_sched else "all school games matched")
