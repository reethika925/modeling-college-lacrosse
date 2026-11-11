"""Stage 2 offline games/statistics audit. No downloads or source-file writes.

School pages are parsed independently; supplier comparison/status tables are not
used as corroboration. New outputs are review artifacts, never cleared imports.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from src.research_integrity import assert_research_snapshot

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "data/incoming/grok/stage1_28f5677d90c3/audit_package"
EXCLUDE_GAMES = {"6444405": "duplicate Hampton-Fairfield result; retain 6386334", "6455124": "misdated duplicate of the genuine 2024-04-20 game 6270089"}
ALIASES = {
    "pennsylvania": "penn", "pennsylvaniastate": "pennst", "pennstate": "pennst",
    "queens": "queensnc", "massachusetts": "umass", "massachusettslowell": "umasslowell",
    "masslowell": "umasslowell", "loyola": "loyolamaryland", "loyolamd": "loyolamaryland",
    "mountstmarysmd": "mountstmarys", "stmarysmd": "mountstmarys", "atalbany": "ualbany",
    "albany": "ualbany", "albanyny": "ualbany", "longisland": "liu", "longislandbrooklyn": "liu",
    "stbonaventure": "stbonaventure", "stjohnsny": "stjohns", "saintjosephct": "stjosephct",
    "newjerseyinstituteoftechnology": "njit", "virginiamilitaryinstitute": "vmi",
    "queenscharlotte": "queensnc", "ohiostate": "ohiost", "clevelandstate": "clevelandst",
    "boston": "bostonu", "army": "armywestpoint",
    "newjerseyinstitutetechnology": "njit",
}
SCHOOL_NAMES = {
    "binghamton": "Binghamton", "highpointpanthers.com": "High Point", "navysports.com": "Navy",
    "merrimackathletics.com": "Merrimack", "brownbears.com": "Brown", "gomarquette.com": "Marquette",
    "gocrimson.com": "Harvard", "goholycross.com": "Holy Cross", "umbcretrievers.com": "UMBC",
    "detroittitans.com": "Detroit Mercy", "mercerbears.com": "Mercer", "hamptonpirates.com": "Hampton",
    "guhoyas.com": "Georgetown", "uvmathletics.com": "Vermont", "hopkinssports.com": "Johns Hopkins",
    "gobobcats.com": "Quinnipiac", "gojaspers.com": "Manhattan", "ionagaels.com": "Iona",
    "liuathletics.com": "LIU", "goprincetontigers.com": "Princeton", "stonybrookathletics.com": "Stony Brook",
    "mountathletics.com": "Mount St. Mary's", "fairfieldstags.com": "Fairfield", "goriverhawks.com": "UMass Lowell",
    "lemoynedolphins.com": "Le Moyne",
}


def canonical_team(value):
    value = re.sub(r"(?:#|No\s*\.?)\s*\d+(?:/\d+)?(?:\s*Seed)?", "", str(value), flags=re.I)
    value = re.sub(r"^\s*(?:\(RV\)|RV)\s*", "", value, flags=re.I)
    value = re.sub(r"\((?:DH|Homecoming)\)", "", value, flags=re.I)
    value = re.sub(r"\([^)]*(?:exh|scrimmage)[^)]*\)", "", value, flags=re.I)
    value = re.sub(r"\b(?:university|college|the|of)\b", "", value, flags=re.I)
    value = re.sub(r"\bsaint\b", "st", value, flags=re.I)
    value = re.sub(r"[^a-z0-9]", "", value.casefold())
    return ALIASES.get(value, value)


def canonical_id(value):
    """Normalize integer-looking IDs only in audit keys; preserve source strings."""
    value = str(value).strip()
    if re.fullmatch(r"\d+\.0+", value):
        value = value.split(".")[0]
    return value


def digest(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read_table(name):
    return pd.read_csv(PACKAGE / name, dtype=str, keep_default_na=False)


def parse_schedule(path):
    """Parse actual saved schedule cards, not Grok's extracted comparisons."""
    match = re.match(r"(.+?)_(202[345])_schedule", path.name)
    if not match:
        return [], "NOT_A_SCHEDULE"
    school, year = match.group(1), int(match.group(2))
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    old = soup.select(".sidearm-schedule-game")
    cards = old or soup.select('.c-schedulepage__games .s-game-card--standard')
    if not cards:
        return [], "NO_SCHEDULE_CARDS; challenge or unsupported markup"
    result = []
    for index, card in enumerate(cards):
        def text(selector):
            node = card.select_one(selector)
            return node.get_text(" ", strip=True) if node else ""
        if old:
            opponent = text(".sidearm-schedule-game-opponent-name")
            date_text = text(".sidearm-schedule-game-opponent-date")
            score_text = text(".sidearm-schedule-game-result")
            marker = text(".sidearm-schedule-game-conference-vs")
            location = text(".sidearm-schedule-game-location")
        else:
            opponent = text('[data-test-id="s-game-card-standard__header-team-opponent-link"]')
            date_text = text('[data-test-id="s-game-card-standard__header-game-date-details"]')
            score_text = text('[data-test-id="s-game-card-standard__header-game-team-score"]')
            marker = text('[data-test-id="s-stamp__root"]')
            location = text('[data-test-id="s-game-card-facility-and-location__details-standard"]')
        day = re.search(r"([A-Za-z]{3})\s+(\d{1,2})", date_text)
        score = re.search(r"\b([WL])\s*,?\s*(\d+)\s*[-–]\s*(\d+)", score_text)
        full_text = card.get_text(" ", strip=True)
        excluded = bool(re.search(r"\bscrimmage\b|\bexhibition\b|\(exh\.?\)", full_text, flags=re.I))
        parsed_date = datetime.strptime(f"{year} {day.group(1)} {day.group(2)}", "%Y %b %d").date().isoformat() if day else ""
        row = {"season": year, "school": SCHOOL_NAMES.get(school, school), "opponent": opponent,
               "date": parsed_date, "result": score_text, "marker": marker, "location": location,
               "excluded_exhibition_scrimmage": excluded, "has_final_score": bool(score),
               # Some schools print the winner's goals first even on an L row.
               # W/L determines score orientation; retain the original display.
               "school_goals": (max if score.group(1) == "W" else min)(int(score.group(2)), int(score.group(3))) if score else None,
               "opponent_goals": (min if score.group(1) == "W" else max)(int(score.group(2)), int(score.group(3))) if score else None,
               "school_won": score.group(1) == "W" if score else None,
               "evidence_file": str(path.relative_to(ROOT)), "card_index": index,
               "source_url": f"https://{school if school != 'binghamton' else 'binghamtonbearcats.com'}/sports/mens-lacrosse/schedule/{year}"}
        row["cancelled_or_postponed"] = bool(re.search(r"\bcancel[le]*d\b|\bpostponed\b", full_text, flags=re.I))
        result.append(row)
    return result, "PARSED"


def load_games():
    frames = []
    for year in (2023, 2024, 2025):
        name = f"corrected/ncaa_lacrosse_games_{year}_corrected.csv" if year != 2025 else "corrected/ncaa_lacrosse_game_index_2025_corrected.csv"
        frame = read_table(name)
        frame["_dataset"] = name
        frame["_source_row"] = np.arange(2, len(frame) + 2)
        frames.append(frame)
    games = pd.concat(frames, ignore_index=True).fillna("")
    games["_h"] = games.home_team.map(canonical_team)
    games["_a"] = games.away_team.map(canonical_team)
    return games


def compare_schedules(games):
    rows, page_counts = [], []
    for path in sorted((PACKAGE / "evidence/games").glob("*_schedule*.html")):
        parsed, status = parse_schedule(path)
        page_counts.append({"file": str(path.relative_to(ROOT)), "status": status, "cards": len(parsed)})
        for row in parsed:
            school, opponent = canonical_team(row["school"]), canonical_team(row["opponent"])
            season = games[games.season.eq(str(row["season"]))]
            candidates = season[((season._h.eq(school) & season._a.eq(opponent)) | (season._a.eq(school) & season._h.eq(opponent)))]
            row.update(game_id="", match_status="NO_FINAL_SCORE" if not row["has_final_score"] else "NO_MATCH", date_agrees=False, score_agrees=False, orientation_agrees=False)
            if row["has_final_score"] and not row["excluded_exhibition_scrimmage"]:
                dated = candidates[candidates.game_date.eq(row["date"])]
                candidate = dated if len(dated) == 1 else candidates if len(candidates) == 1 else candidates.iloc[:0]
                if len(candidate) == 1:
                    game = candidate.iloc[0]
                    home = game._h == school
                    own, other = (game.home_score, game.away_score) if home else (game.away_score, game.home_score)
                    row.update(game_id=game.game_id, match_status="UNIQUE_TEAM_PAIR_AND_DATE" if len(dated) == 1 else "UNIQUE_PAIR_DATE_CONFLICT",
                               date_agrees=game.game_date == row["date"],
                               score_agrees=float(own) == row["school_goals"] and float(other) == row["opponent_goals"])
                    marker = row["marker"].strip().casefold()
                    neutral = game.neutral_site.casefold() == "true" or marker not in {"at", "vs", "vs."}
                    row["orientation_agrees"] = (marker == "at" and not home) or (marker.startswith("vs") and home) or neutral
                    row["orientation_status"] = "NEUTRAL_OR_NOT_ESTABLISHED" if neutral else "CONFIRMED" if row["orientation_agrees"] else "CONFLICT"
                if row["excluded_exhibition_scrimmage"]:
                    row["match_status"] = "EXCLUDED_EXHIBITION"
            rows.append(row)
    return pd.DataFrame(rows), page_counts


TEAM_COUNTS = ["goals", "goals_allowed", "final_score_scoreboard", "assists", "shots", "shots_on_goal",
               "faceoffs_won", "faceoffs_attempted", "ground_balls", "turnovers", "caused_turnovers", "saves",
               "goalie_goals_allowed", "clears_completed", "clears_attempted", "emo_goals", "emo_opportunities",
               "penalties", "penalty_seconds", "free_position_shots"]
PLAYER_COUNTS = ["goals", "assists", "points", "shots", "shots_on_goal", "ground_balls", "turnovers",
                 "caused_turnovers", "goalie_saves", "goalie_goals_allowed", "penalties", "penalty_seconds",
                 "faceoffs_won", "faceoffs_attempted"]
NON_D1_OPPONENTS = {"mitchell", "standrews", "wabash", "randolph", "stjosephct", "gordon", "salemst", "regisma"}


def assert_originals():
    manifest = json.loads((ROOT / "reports/grok_stage2_existing_checksums.json").read_text())
    return assert_research_snapshot(ROOT, manifest)


def numeric_frame(frame, fields):
    return frame[fields].apply(pd.to_numeric, errors="coerce")


def numeric_issues(frame, counts, other=()):
    numbers = numeric_frame(frame, counts + list(other))
    missing = frame[counts + list(other)].apply(lambda s: s.str.strip().str.casefold().isin(["", "null", "nan", "none", "na", "n/a"]))
    masks = {
        "NONNUMERIC_OR_NONFINITE": ((~missing & numbers.isna()) | (numbers.notna() & ~np.isfinite(numbers))).any(axis=1),
        "NEGATIVE_STAT": numbers.lt(0).any(axis=1),
        "NONINTEGER_COUNT": (numbers[counts].notna() & (numbers[counts] % 1).ne(0)).any(axis=1),
    }
    return numbers, masks


def add_issue_rows(output, frame, masks, dataset):
    for code, mask in masks.items():
        for index in frame.index[mask.fillna(False)]:
            row = frame.loc[index]
            output.append({"dataset": dataset, "source_csv_row": int(index) + 2, "game_id": row.game_id,
                           "season": row.season, "team": row.get("team", ""), "team_id_ncaa": row.get("team_id_ncaa", ""),
                           "jersey": row.get("jersey", ""), "player": (row.get("player_first", "") + " " + row.get("player_last", "")).strip(),
                           "issue": code, "factual_status": "EXCLUSION_SUPPORTED" if code == "EXCLUDED_GAME_COPY" else "REVIEW_REQUIRED", "permission_status": "NOT_CLEARED_NO_CHANGE",
                           "source_url": row.get("source_url", "")})


def audit_local_ncaa_cache(games):
    """Use the project's pre-existing official 2025 raw responses, offline."""
    entries = defaultdict(list)
    paths = sorted((ROOT / "data/raw/games/2025").glob("2025-??-??.json"))
    for path in paths:
        for wrapper in json.loads(path.read_text()).get("games", []):
            game = wrapper["game"]
            page_id = str(game.get("url", "")).rstrip("/").split("/")[-1]
            entries[page_id].append((game, path))
    checks = []
    for row in games[games.season.eq("2025")].itertuples():
        candidates = entries.get(row.game_id, [])
        score_match, date_match, team_match = False, False, False
        files = []
        for raw, path in candidates:
            scores = float(raw["home"]["score"]) == float(row.home_score) and float(raw["away"]["score"]) == float(row.away_score)
            names = canonical_team(raw["home"]["names"]["short"]) == canonical_team(row.home_team) and canonical_team(raw["away"]["names"]["short"]) == canonical_team(row.away_team)
            when = datetime.strptime(raw["startDate"], "%m-%d-%Y").date().isoformat()
            score_match |= scores
            team_match |= names
            date_match |= scores and names and when == row.game_date
            files.append(str(path.relative_to(ROOT)))
        checks.append({"game_id": row.game_id, "raw_payloads_found": len(candidates), "score_matches_raw": score_match,
                       "teams_match_raw": team_match, "date_matches_any_raw": date_match, "evidence_files": ";".join(files)})
    return pd.DataFrame(checks), len(paths)


def audit_stats(games, corroborated):
    team = read_table("corrected/ncaa_lacrosse_team_game_stats_2023_2025_corrected.csv")
    players = read_table("corrected/ncaa_lacrosse_player_stats_2023_2025_corrected.csv")
    for frame in (team, players):
        frame["_tid"] = frame.team_id_ncaa.map(canonical_id)
        frame["_excluded_game"] = frame.game_id.isin(EXCLUDE_GAMES)
        frame["_source_corroborated_result"] = frame.game_id.isin(corroborated)
        scope_ids = set(games.loc[games._h.isin(NON_D1_OPPONENTS) | games._a.isin(NON_D1_OPPONENTS), "game_id"])
        frame["_scope_out"] = frame.game_id.isin(scope_ids)
    g = games.set_index("game_id")
    assert g.index.is_unique
    team_n, team_masks = numeric_issues(team, TEAM_COUNTS, ["shooting_pct", "penalty_minutes"])
    team_masks.update({
        "SOG_EXCEEDS_SHOTS": team_n.shots_on_goal.gt(team_n.shots),
        "GOALS_EXCEED_SOG": team_n.goals.gt(team_n.shots_on_goal),
        "FACEOFF_WINS_EXCEED_ATTEMPTS": team_n.faceoffs_won.gt(team_n.faceoffs_attempted),
        "CLEARS_EXCEED_ATTEMPTS": team_n.clears_completed.gt(team_n.clears_attempted),
        "EMO_GOALS_EXCEED_OPPORTUNITIES": team_n.emo_goals.gt(team_n.emo_opportunities),
        "SHOOTING_PERCENTAGE_OUT_OF_RANGE": team_n.shooting_pct.gt(1),
        "ASSISTS_EXCEED_TEAM_GOALS": team_n.assists.gt(team_n.goals),
        "PENALTY_MINUTE_SECOND_CONFLICT": (team_n.penalty_minutes * 60 - team_n.penalty_seconds).abs().gt(1e-8),
        "MISSING_CORE_BOX_STATS": team_n[["goals", "assists", "shots", "shots_on_goal", "ground_balls", "turnovers", "saves"]].isna().any(axis=1),
        "DUPLICATE_GAME_TEAM_KEY": team.duplicated(["game_id", "_tid"], keep=False),
        "EXCLUDED_GAME_COPY": team._excluded_game,
        "GAME_REFERENCE_MISSING": ~team.game_id.isin(g.index),
        "MISSING_TEAM_IDENTIFIER": team._tid.eq(""),
    })
    expected_team_ids = []
    expected_goals, expected_allowed, expected_team, expected_opponent, expected_opponent_ids = [], [], [], [], []
    date_mismatch, season_mismatch = [], []
    for row in team.itertuples():
        game = g.loc[row.game_id]
        side = row.home_away if row.home_away in {"home", "away"} else "home"
        other = "away" if side == "home" else "home"
        expected_team_ids.append(canonical_id(game[f"{side}_team_id_ncaa"]))
        expected_opponent_ids.append(canonical_id(game[f"{other}_team_id_ncaa"]))
        expected_goals.append(float(game[f"{side}_score"]))
        expected_allowed.append(float(game[f"{other}_score"]))
        expected_team.append(canonical_team(game[f"{side}_team"]))
        expected_opponent.append(canonical_team(game[f"{other}_team"]))
        date_mismatch.append(row.game_date != game.game_date)
        season_mismatch.append(row.season != game.season)
    team_masks["TEAM_OPPONENT_IDENTIFIER_OR_ROLE_CONFLICT"] = team._tid.ne(expected_team_ids) | team.opponent_id_ncaa.map(canonical_id).ne(expected_opponent_ids) | ~team.home_away.isin(["home", "away"])
    team_masks["TEAM_OPPONENT_NAME_CONFLICT"] = team.team.map(canonical_team).ne(expected_team) | team.opponent.map(canonical_team).ne(expected_opponent)
    team_masks["DATE_CONFLICT"] = pd.Series(date_mismatch)
    team_masks["SEASON_CONFLICT"] = pd.Series(season_mismatch)
    team_masks["BOX_GOALS_VS_FINAL_RESULT"] = team_n.goals.notna() & team_n.goals.ne(expected_goals)
    team_masks["SCOREBOARD_GOALS_VS_RESULT"] = team_n.final_score_scoreboard.notna() & team_n.final_score_scoreboard.ne(expected_goals)
    team_masks["GOALS_ALLOWED_VS_RESULT"] = team_n.goals_allowed.notna() & team_n.goals_allowed.ne(expected_allowed)
    lookup = team.assign(_idx=team.index).set_index(["game_id", "_tid"])
    opposite = [lookup.loc[(r.game_id, canonical_id(r.opponent_id_ncaa)), "_idx"] for r in team.itertuples()]
    opp = team_n.loc[opposite].reset_index(drop=True)
    team_masks["SAVES_OPPONENT_SOG_GOALS_RESIDUAL"] = (team_n.saves - (opp.shots_on_goal - opp.goals)).abs().gt(0)
    team_masks["CAUSED_TURNOVERS_EXCEED_OPPONENT_TURNOVERS"] = team_n.caused_turnovers.gt(opp.turnovers)
    team_masks["FACEOFF_TEAM_TOTAL_CONFLICT"] = (team_n.faceoffs_won + opp.faceoffs_won).ne(team_n.faceoffs_attempted) & team_n.faceoffs_attempted.notna() & opp.faceoffs_won.notna() & team_n.faceoffs_won.notna()

    pn, player_masks = numeric_issues(players, PLAYER_COUNTS, ["goalie_minutes"])
    players["_jersey"] = players.jersey.map(canonical_id)
    players["_name"] = (players.player_first + players.player_last).str.casefold().str.replace(r"[^a-z0-9]", "", regex=True)
    player_masks.update({
        "SOG_EXCEEDS_SHOTS": pn.shots_on_goal.gt(pn.shots),
        "GOALS_EXCEED_SOG": pn.goals.gt(pn.shots_on_goal),
        "POINTS_IDENTITY_CONFLICT": pn.points.ne(pn.goals + pn.assists) & pn[["points", "goals", "assists"]].notna().all(axis=1),
        "FACEOFF_WINS_EXCEED_ATTEMPTS": pn.faceoffs_won.gt(pn.faceoffs_attempted),
        "GOALIE_TIME_LIKELY_SECONDS_NOT_MINUTES": pn.goalie_minutes.gt(300),
        "EXCLUDED_GAME_COPY": players._excluded_game,
        "DUPLICATE_GAME_PLAYER_KEY": players.duplicated(["game_id", "_tid", "_jersey", "_name"], keep=False),
        "MISSING_PLAYER_NAME_OR_TEAM_ID": players["_tid"].eq("") | players["_name"].eq(""),
        "MISSING_CORE_COUNT": pn[["goals", "assists", "points", "shots", "shots_on_goal"]].isna().any(axis=1),
        "INVALID_BOOLEAN_VALUE": ~players.participated.isin(["True", "False"]) | ~players.started.isin(["True", "False"]),
        "SEASON_CONFLICT": players.season.ne(players.game_id.map(g.season)),
        "DATE_CONFLICT": players.game_date.ne(players.game_id.map(g.game_date)),
    })
    keys = pd.MultiIndex.from_arrays([players.game_id, players._tid])
    player_masks["TEAM_GAME_REFERENCE_MISSING"] = pd.Series(~keys.isin(lookup.index))
    joined = lookup.reindex(keys).reset_index(drop=True)
    player_masks["TEAM_OPPONENT_OR_ROLE_CONFLICT"] = players.team.map(canonical_team).ne(joined.team.map(canonical_team)) | players.opponent.map(canonical_team).ne(joined.opponent.map(canonical_team)) | players.home_away.ne(joined.home_away)
    player_masks["NONPARTICIPANT_WITH_RECORDED_COUNT"] = players.participated.eq("False") & pn[PLAYER_COUNTS].fillna(0).ne(0).any(axis=1)

    # Aggregates compare only shared, present data. A discrepancy is a review
    # flag, not permission to overwrite a player or invent an unattributed goal.
    aggregate_columns = ["goals", "assists", "shots", "shots_on_goal", "faceoffs_won", "faceoffs_attempted", "goalie_saves", "goalie_goals_allowed"]
    aggregate = pn[aggregate_columns].groupby([players.game_id, players._tid]).sum(min_count=1)
    reconciliation = lookup[["_idx", "game_audit_status"]].join(aggregate, how="left")
    # Individual goalie saves correspond to the team's saves column. Duration
    # is intentionally not summed because its units are demonstrably mixed.
    team_reference = team_n.assign(goalie_saves=team_n.saves)
    reconciliation = reconciliation.join(team_reference.set_index(lookup.index)[aggregate_columns].add_suffix("_team"))
    reconciliation["has_player_rows"] = reconciliation.index.isin(aggregate.index)
    for column in aggregate_columns:
        reconciliation[f"{column}_difference"] = reconciliation[column] - reconciliation[f"{column}_team"]
    goal_bad_keys = reconciliation.index[reconciliation.goals_difference.ne(0) & reconciliation.goals_difference.notna()]
    team_masks["PLAYER_GOAL_SUM_RESIDUAL"] = pd.Series(pd.MultiIndex.from_frame(team[["game_id", "_tid"]]).isin(goal_bad_keys))
    player_masks["TEAM_PLAYER_GOAL_AGGREGATE_REVIEW"] = pd.Series(keys.isin(goal_bad_keys))
    # No global equality check for turnovers/ground balls: NCAA team-only
    # credits and missing attribution can legitimately prevent equality.
    issues = []
    add_issue_rows(issues, team, team_masks, "team_stats")
    add_issue_rows(issues, players, player_masks, "player_stats")

    old = players[players.game_id.eq("6270089")]
    wrong = players[players.game_id.eq("6455124")]
    identity = ["_tid", "_jersey", "_name"]
    copies = wrong.merge(old, on=identity, how="left", suffixes=("_wrong", "_2024"), indicator=True, validate="one_to_one")
    comparable = PLAYER_COUNTS
    equivalent = pd.Series(True, index=copies.index)
    for column in comparable:
        left = pd.to_numeric(copies[column + "_wrong"], errors="coerce")
        right = pd.to_numeric(copies[column + "_2024"], errors="coerce")
        equivalent &= left.eq(right) | (left.isna() & right.isna())
    counts = {
        "team_rows_checked": len(team), "player_rows_checked": len(players),
        "team_issue_counts": {name: int(mask.sum()) for name, mask in team_masks.items()},
        "player_issue_counts": {name: int(mask.sum()) for name, mask in player_masks.items()},
        "team_missing_by_column": team.drop(columns=[c for c in team if c.startswith("_")]).eq("").sum().to_dict(),
        "player_missing_by_column": players.drop(columns=[c for c in players if c.startswith("_")]).eq("").sum().to_dict(),
        "team_nonexcluded_rows": int((~team._excluded_game).sum()),
        "player_nonexcluded_rows": int((~players._excluded_game).sum()),
        "team_rows_complete_core_box": int((~team_masks["MISSING_CORE_BOX_STATS"] & ~team._excluded_game).sum()),
        "player_participated_true": int(players.participated.eq("True").sum()),
        "player_nonparticipants": int(players.participated.eq("False").sum()),
        "player_nonexcluded_participated_true": int((players.participated.eq("True") & ~players._excluded_game).sum()),
        "goalie_time_nonblank": int(pn.goalie_minutes.notna().sum()),
        "team_scope_out_rows": int(team._scope_out.sum()), "player_scope_out_rows": int(players._scope_out.sum()),
        "unnamed_player_rows": int(players["_name"].eq("").sum()),
        "unnamed_player_games": players.loc[players["_name"].eq(""), "game_id"].value_counts().to_dict(),
        "goalie_time_large_values": pn.goalie_minutes[pn.goalie_minutes.gt(300)].value_counts().head(8).to_dict(),
        "team_games_without_players": int((~reconciliation.has_player_rows).sum()),
        "reconciliations_with_players": int(reconciliation.has_player_rows.sum()),
        "aggregate_mismatch_team_games": {column: int((reconciliation[f"{column}_difference"].ne(0) & reconciliation[f"{column}_difference"].notna()).sum()) for column in aggregate_columns},
        "liuq_wrong_season_player_rows": len(wrong), "liuq_identity_matches_2024": int(copies._merge.eq("both").sum()),
        "liuq_same_non_time_stat_vectors": int(equivalent.sum()), "liuq_existing_2024_player_rows": len(old),
        "liuq_same_team_stat_vectors": bool(team_n.loc[team.game_id.eq("6270089")].reset_index(drop=True).equals(team_n.loc[team.game_id.eq("6455124")].reset_index(drop=True))),
        "source_corroborated_result_team_rows": int(team._source_corroborated_result.sum()),
        "source_corroborated_result_player_rows": int(players._source_corroborated_result.sum()),
        "fully_source_verified_stat_records": None,
        "stat_source_verification_status": "NOT_ESTABLISHED; original NCAA box/PBP evidence omitted; targeted official box verifies selected fields only",
    }
    # Bounded numerical-screen counts have a deliberately narrower meaning than
    # independently verified records. Minutes and aggregation flags are separate.
    for label, frame, masks in (("team", team, team_masks), ("player", players, player_masks)):
        blocked = frame._excluded_game.copy()
        for code, mask in masks.items():
            if not any(part in code for part in ("RESIDUAL", "AGGREGATE", "LIKELY_SECONDS")):
                blocked |= mask.fillna(False)
        counts[label + "_basic_internal_screen_pass"] = int((~blocked).sum())
        counts[label + "_d1_basic_internal_screen_pass"] = int((~blocked & ~frame._scope_out).sum())
    return counts, pd.DataFrame(issues), reconciliation.reset_index(), team, players


def compare_local_2025(games):
    local = pd.read_csv(ROOT / "data/processed/lacrosse_games_2025.csv", dtype=str, keep_default_na=False)
    local["_page_id"] = local.game_page_url.str.rsplit("/", n=1).str[-1]
    imported = games[games.season.eq("2025")].set_index("game_id")
    rows = []
    for row in local.to_dict("records"):
        page_id = row["_page_id"]
        if page_id not in imported.index:
            rows.append({"local_game_id": row["game_id"], "imported_game_id": "", "status": "NO_IMPORTED_URL_ID"})
            continue
        other = imported.loc[page_id]
        dates = row["game_date"] == other.game_date
        scores = float(row["home_score"]) == float(other.home_score) and float(row["away_score"]) == float(other.away_score)
        teams = canonical_team(row["home_team"]) == other._h and canonical_team(row["away_team"]) == other._a
        rows.append({"local_game_id": row["game_id"], "imported_game_id": page_id,
                     "local_date": row["game_date"], "imported_date": other.game_date,
                     "home_team": row["home_team"], "away_team": row["away_team"],
                     "dates_match": dates, "scores_match": scores, "teams_orientation_match": teams,
                     "result_fields_match": dates and scores and teams, "proposed_exclusion": EXCLUDE_GAMES.get(page_id, ""),
                     "status": "MATCH" if dates and scores and teams else "CONFLICT"})
    return pd.DataFrame(rows)


def write_new_csv(frame, path):
    protected = json.loads((ROOT / "reports/grok_stage2_existing_checksums.json").read_text())
    if str(path.relative_to(ROOT)) in protected:
        raise ValueError("Refusing to overwrite a protected original")
    with path.open("w" if path.exists() else "x", newline="") as handle:
        frame.to_csv(handle, index=False)


def run_audit():
    protected = assert_originals()
    games = load_games()
    schedules, pages = compare_schedules(games)
    # This corroborates result/date/teams. Neutral/nominal orientation is retained
    # as a separate field, rather than pretending a schedule proves home advantage.
    supported = schedules.date_agrees & schedules.score_agrees & ~schedules.excluded_exhibition_scrimmage
    corroborated = set(schedules.loc[supported, "game_id"]) - set(EXCLUDE_GAMES)
    stats, issues, reconciliation, teams, players = audit_stats(games, corroborated)
    local = compare_local_2025(games)
    cache, cache_count = audit_local_ncaa_cache(games)
    games["_out_of_d1_vs_d1_scope"] = games._h.isin(NON_D1_OPPONENTS) | games._a.isin(NON_D1_OPPONENTS)
    games["_excluded"] = games.game_id.isin(EXCLUDE_GAMES)
    coverage = []
    for season, frame in games.groupby("season"):
        pairs = frame.apply(lambda r: "|".join(sorted([r._h, r._a])), axis=1)
        dates = pd.to_datetime(frame.game_date, format="%Y-%m-%d", errors="coerce")
        appearances = pd.concat([frame[["game_id", "game_date", column]].rename(columns={column: "team"}) for column in ("_h", "_a")])
        score = numeric_frame(frame, ["home_score", "away_score"])
        correct_winner = frame.home_team.where(score.home_score.gt(score.away_score), frame.away_team)
        winner_present = frame.winner.ne("")
        candidate = ~frame._excluded & ~frame._out_of_d1_vs_d1_scope
        record = {
            "season": season, "physical_game_rows": len(frame), "unique_game_ids": int(frame.game_id.nunique()),
            "result_candidates_nonduplicate": int((~frame._excluded).sum()), "d1_vs_d1_candidates": int(candidate.sum()),
            "official_schedule_corroborated_results": int((frame.game_id.isin(corroborated) & candidate).sum()),
            "scope_excluded_games": int(frame._out_of_d1_vs_d1_scope.sum()), "duplicate_wrong_season_excluded_games": int(frame._excluded.sum()),
            "unverified_result_candidates": int((candidate & ~frame.game_id.isin(corroborated)).sum()),
            "first_date": frame.game_date.min(), "last_date": frame.game_date.max(), "distinct_game_dates": int(frame.game_date.nunique()),
            "duplicate_ids_extra": int(frame.game_id.duplicated().sum()),
            "duplicate_same_date_matchups_extra": int(pd.DataFrame({"date": frame.game_date.to_numpy(), "pair": pairs.to_numpy()}).duplicated().sum()),
            "same_day_repeated_team_appearances": int(appearances.duplicated(["game_date", "team"], keep=False).sum()),
            "season_date_conflicts": int((dates.dt.year.astype(str) != season).sum()),
            "not_final_rows": int(frame.status.ne("final").sum()), "missing_final_scores": int(score.isna().any(axis=1).sum()),
            "winner_disagreements_where_supplied": int((winner_present & frame.winner.ne(correct_winner)).sum()),
            "missing_home_numeric_ids": int(frame.home_team_id_ncaa.eq("").sum()), "missing_away_numeric_ids": int(frame.away_team_id_ncaa.eq("").sum()),
            "negative_scores": int(score.lt(0).any(axis=1).sum()),
            "noninteger_scores": int((score.notna() & (score % 1).ne(0)).any(axis=1).sum()),
            "tied_scores": int(score.home_score.eq(score.away_score).sum()),
            "team_stat_rows": int(teams.season.eq(season).sum()), "player_stat_rows": int(players.season.eq(season).sum()),
            "season_completeness": "NOT_VERIFIED", "permission_status": "NOT_CLEARED_NO_CHANGE",
        }
        coverage.append(record)
    games["factual_status"] = np.select([
        games._excluded, games._out_of_d1_vs_d1_scope, games.game_id.isin(corroborated),
        games.season.eq("2025") & games.game_id.isin(cache.loc[cache.score_matches_raw & cache.teams_match_raw, "game_id"])],
        ["EXCLUDE_DUPLICATE_OR_WRONG_SEASON", "OUTSIDE_D1_VS_D1_SCOPE", "SCHOOL_CORROBORATED_RESULT", "NCAA_RAW_SOURCE_ONLY"],
        default="PROVISIONAL_PRIMARY_ARTIFACT_MISSING")
    games["permission_status"] = "NOT_CLEARED_NO_CHANGE"
    games["proposed_d1_eligible"] = ~games._excluded & ~games._out_of_d1_vs_d1_scope
    repeated = games.assign(_pair=games.apply(lambda r:"|".join(sorted([r._h,r._a])), axis=1))
    repeated["_score_pair"] = games.apply(lambda r:"|".join(str(int(float(x))) for x in sorted([r.home_score,r.away_score],key=float)), axis=1)
    repeated_groups = repeated[repeated.duplicated(["season","_pair","_score_pair"],keep=False)][["game_id","season","game_date","home_team","away_team","home_score","away_score"]].to_dict("records")
    nonfinal_hits = []
    for row in schedules[~schedules.has_final_score].to_dict("records"):
        school, opponent = canonical_team(row["school"]), canonical_team(row["opponent"])
        hit = games[games.season.eq(str(row["season"])) & games.game_date.eq(row["date"]) & ((games._h.eq(school)&games._a.eq(opponent))|(games._a.eq(school)&games._h.eq(opponent)))]
        if not hit.empty:
            nonfinal_hits.append({"schedule_row":row,"imported_game_ids":hit.game_id.tolist()})
    files = {}
    for name, frame in [(name, games[games._dataset.eq(name)]) for name in games._dataset.unique()] + [
        ("corrected/ncaa_lacrosse_team_game_stats_2023_2025_corrected.csv", teams),
        ("corrected/ncaa_lacrosse_player_stats_2023_2025_corrected.csv", players)]:
        columns = [column for column in frame.columns if not column.startswith("_")]
        # Reload to preserve the actual per-file schema (2025 lacks winner etc.).
        actual = read_table(name)
        files[name] = {"rows": len(actual), "columns": actual.columns.tolist(), "missing_by_column": actual.eq("").sum().to_dict(),
                       "sha256": digest(PACKAGE / name), "source_url_examples": actual.source_url.head(2).tolist(),
                       "factual_status": "PARTIALLY_CORROBORATED_AND_INTERNAL_CHECKED", "permission_status": "NOT_CLEARED_NO_CHANGE"}
    identities = pd.concat([games[[f"{side}_team_id_ncaa", f"{side}_team_seo", f"{side}_team"]].rename(columns={f"{side}_team_id_ncaa":"id",f"{side}_team_seo":"seo",f"{side}_team":"name"}) for side in ("home","away")])
    identities["id"] = identities.id.map(canonical_id)
    identities = identities[identities.id.ne("")]
    summary = {"protected_existing_files": protected, "coverage": coverage, "schemas": files, "schedule_pages": pages,
               "identifiers": {"numeric_team_id_multiple_seo": identities.groupby("id").seo.nunique()[lambda x:x.gt(1)].to_dict(),
                               "missing_numeric_id_games": games[games.home_team_id_ncaa.eq("")|games.away_team_id_ncaa.eq("")][["game_id","season","home_team","away_team"]].to_dict("records"),
                               "player_permanent_id_column_present": False},
               "local_raw_2025_evidence": {"raw_scoreboard_files_read":cache_count,"imported_games_checked":len(cache),
                                          "score_matches":int(cache.score_matches_raw.sum()),"team_matches":int(cache.teams_match_raw.sum()),
                                          "date_matches":int(cache.date_matches_any_raw.sum()),"date_conflict_ids":cache.loc[~cache.date_matches_any_raw,"game_id"].tolist()},
               "schedule_comparison_rows": len(schedules), "schedule_result_rows": int(schedules.has_final_score.sum()),
               "repeated_pair_identical_score_games": repeated_groups,
               "nonfinal_schedule_cards": int((~schedules.has_final_score).sum()), "nonfinal_cards_overlapping_imported_finals": nonfinal_hits,
               "unmatched_scored_schedule_rows": schedules[schedules.has_final_score & schedules.game_id.eq("") & ~schedules.excluded_exhibition_scrimmage].to_dict("records"),
               "schedule_orientation_conflicts": schedules[schedules.get("orientation_status", pd.Series(index=schedules.index, dtype=str)).eq("CONFLICT")].to_dict("records"),
               "statistics": stats, "local_2025_comparison": {
                   "rows_compared": len(local), "result_fields_match": int(local.result_fields_match.sum()), "date_conflicts": int((~local.dates_match).sum()),
                   "score_conflicts": int((~local.scores_match).sum()), "team_orientation_conflicts": int((~local.teams_orientation_match).sum()),
                   "local_ids_not_in_imported_page_id_namespace": int(local.imported_game_id.eq("").sum()),
                   "imported_ids_absent_from_local_page_ids": len(set(games[games.season.eq('2025')].game_id) - set(local.imported_game_id)),
                   "records_proposed_for_exclusion": int(local.proposed_exclusion.ne("").sum())},
               "source_data_and_models_modified": False, "odds_imported": False, "permissions_cleared": False}
    for frame, name in [(pd.DataFrame(coverage), "grok_stage2_coverage.csv"), (schedules, "grok_stage2_schedule_comparison.csv"),
                        (games[["game_id","season","game_date","home_team","away_team","home_score","away_score","_dataset","_source_row","factual_status","permission_status","proposed_d1_eligible"]], "grok_stage2_game_assessments.csv"),
                        (local, "grok_stage2_local_2025_comparison.csv"), (issues, "grok_stage2_statistical_issues.csv"),
                        (cache, "grok_stage2_local_raw_evidence.csv"),
                        (reconciliation, "grok_stage2_player_team_reconciliation.csv")]:
        write_new_csv(frame, ROOT / "reports" / name)
    summary_path = ROOT / "reports/grok_stage2_checks.json"
    assert str(summary_path.relative_to(ROOT)) not in json.loads((ROOT / "reports/grok_stage2_existing_checksums.json").read_text())
    with summary_path.open("w" if summary_path.exists() else "x") as handle:
        json.dump(summary, handle, indent=2, default=lambda value: int(value) if isinstance(value, np.integer) else float(value) if isinstance(value, np.floating) else bool(value) if isinstance(value, np.bool_) else str(value))
        handle.write("\n")
    assert_originals()
    print(json.dumps({"coverage": coverage, "statistics": {k:v for k,v in stats.items() if not k.endswith('missing_by_column')}, "local":summary['local_2025_comparison'], "unmatched_schedules":summary['unmatched_scored_schedule_rows']}, indent=2))
    return summary


if __name__ == "__main__":
    run_audit()
