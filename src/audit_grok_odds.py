"""Offline Stage 3 audit. Reads package files; writes only new Stage 3 reports.

Supplier scripts are never imported or executed. Supplier evidence flags are
claims, not independent verification. No network access or processed-data writes.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
from decimal import Decimal
from urllib.parse import urlparse

import pandas as pd
from bs4 import BeautifulSoup

from src.audit_grok_games_stats import canonical_id, canonical_team

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "data/incoming/grok/stage1_28f5677d90c3/audit_package"
REPORTS = ROOT / "reports"
MISSING = {"", "null", "none", "nan", "n/a"}
BOOKS = {"DraftKings", "BetMGM", "FanDuel", "Caesars", "bet365"}
DOMAIN_KEYS = {"www.actionnetwork.com": "actionnetwork", "betonlacrosse.com": "betonlacrosse",
               "sports.betmgm.com": "betmgm", "sportsbook.draftkings.com": "draftkings",
               "sportsbook-nash.draftkings.com": "draftkings", "laxallstars.com": "laxallstars",
               "www.legalsportsbetting.com": "legalsportsbetting"}


def missing(value):
    return str(value).strip().casefold() in MISSING


def number(value):
    if missing(value):
        return None
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None


def american_valid(value):
    n = number(value)
    return n is not None and n.is_integer() and abs(n) >= 100


def decimal_from_american(value):
    if not american_valid(value):
        return None
    n = float(value)
    return 1 + (n / 100 if n > 0 else 100 / -n)


def decimal_agrees(american, decimal):
    """Respect the precision actually printed (e.g. 1.8696 for -115)."""
    expected = decimal_from_american(american)
    actual = number(decimal)
    if expected is None or actual is None or actual <= 1:
        return False
    precision = max(0, -Decimal(str(decimal)).as_tuple().exponent)
    # Original feed decimals sometimes have ~1e-8 serialization noise.
    return abs(actual - expected) <= max(0.5 * 10 ** (-precision), 1e-7) + 1e-12


def aware_time(value):
    if missing(value):
        return None
    try:
        t = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return t if t.utcoffset() is not None else None
    except ValueError:
        return None


def valid_day(value):
    try:
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value))) and datetime.strptime(value, "%Y-%m-%d").date().isoformat() == value
    except ValueError:
        return False


def team(value):
    # Explicit, unambiguous spelling aliases, reviewed against the existing
    # crosswalk / NCAA names. No fuzzy matching; Rutgers is never Denver.
    normalized = canonical_team(value)
    return {"stjoes": "stjosephs", "stjohnsnewyork": "stjohns"}.get(normalized, normalized)


def table(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def digest(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def match_event(event, games):
    """Require original date and both teams; an identifier cannot repair a conflict."""
    if event["season"] not in set(games.season):
        return {"match_status": "OUT_OF_REFERENCE_SEASONS", "matched_game_id": "", "candidate_game_ids": ""}
    if not valid_day(event["date"]):
        return {"match_status": "NO_DATE", "matched_game_id": "", "candidate_game_ids": ""}
    h, a = team(event["home"]), team(event["away"])
    season = games[games.season.eq(event["season"])]
    pairs = season[season.apply(lambda g: {team(g.home_team), team(g.away_team)} == {h, a}, axis=1)]
    exact = pairs[pairs.game_date.eq(event["date"])]
    base = {"matched_game_id": "", "candidate_game_ids": "|".join(pairs.game_id)}
    if len(exact) > 1:
        return {**base, "match_status": "AMBIGUOUS"}
    if len(exact) == 0:
        return {**base, "match_status": "DATE_CONFLICT" if len(pairs) else "UNMATCHED_TEAMS_DATE"}
    g = exact.iloc[0]
    if g.proposed_d1_eligible != "True":
        return {**base, "match_status": "EXCLUDED_STAGE2_GAME"}
    claimed = canonical_id(event.get("claimed_id", ""))
    if not missing(claimed) and claimed != g.game_id:
        return {**base, "match_status": "ID_CONFLICT"}
    return {**base, "match_status": "MATCHED_STAGE2_CANDIDATE", "matched_game_id": g.game_id,
            "stage2_factual_status": g.factual_status,
            "raw_listed_home_agrees": h == team(g.home_team),
            "reference_home": g.home_team, "reference_away": g.away_team}


def evidence_candidates(reference, files):
    """Resolve only inside the package; never follow supplier /workspace paths."""
    reference = str(reference).strip()
    if missing(reference):
        return []
    exact = [f for f in files if f.as_posix().endswith("/" + reference)]
    if exact:
        return exact
    # Basename search is a discovery aid, never content verification.
    return [f for f in files if f.name == Path(reference).name]


def snapshot(row):
    """Identity of a *claimed* observation; never an authenticated odds timestamp."""
    for column, kind in [("quote_capture_timestamp", "claimed_quote_capture"),
                         ("archive_capture_timestamp", "claimed_archive_capture")]:
        if aware_time(row[column]):
            return kind, aware_time(row[column]).isoformat()
    if aware_time(row["article_published_at"]):
        return "editorial_version_no_odds_timestamp", row["article_published_at"] + "|" + row["article_modified_at"]
    return "undated_evidence_reference", row["evidence_file"]


def pair_complete(rows, market, home, away):
    """All rows must already share book/event/source/snapshot/line type."""
    priced = [r for r in rows if american_valid(r["american_odds"])]
    if market == "moneyline":
        selections = {team(r["selection"]) for r in priced}
        return home != away and {home, away}.issubset(selections)
    if market == "spread":
        return any(team(x["selection"]) == home and team(y["selection"]) == away
                   and number(x["line"]) is not None and number(y["line"]) is not None
                   and abs(float(x["line"]) + float(y["line"])) < 1e-9 for x in priced for y in priced)
    if market == "total":
        return any(x["selection"].casefold() == "over" and y["selection"].casefold() == "under"
                   and number(x["line"]) is not None and number(y["line"]) is not None
                   and float(x["line"]) == float(y["line"]) > 0 for x in priced for y in priced)
    return False


def choose_sample(frame, n=40):
    """Deterministic greedy marginal strata coverage, then SHA-256 fill (seed 519)."""
    dimensions = ["sportsbook", "season", "market", "grade_audited", "source_domain", "source_dataset", "technical_status"]
    strata = {r.record_id: {(d, str(getattr(r, d))) for d in dimensions} for r in frame.itertuples()}
    rank = lambda rid: hashlib.sha256(f"519|{rid}".encode()).hexdigest()
    remaining = sorted(strata, key=rank)
    selected, covered = [], set()
    while remaining and len(selected) < n:
        best = min(remaining, key=lambda rid: (-len(strata[rid] - covered), rank(rid)))
        selected.append(best)
        covered |= strata[best]
        remaining.remove(best)
    return frame.set_index("record_id").loc[selected].reset_index()


def inspect_rows(odds, crosswalk, original, games, files):
    cw = {r["odds_game_id"]: r for r in crosswalk.to_dict("records")}
    raw = {r["record_id"]: r for r in original.to_dict("records")}
    matches = {}
    output = []
    for r in odds.to_dict("records"):
        c = cw.get(r["game_id"], {})
        old = raw.get(r["orig_record_id"], {}) if r["source_dataset"] == "original" else {}
        event = {"season": r["season"], "date": old.get("game_date", c.get("odds_game_date", "")),
                 "home": old.get("home_team", c.get("odds_home_team", "")),
                 "away": old.get("away_team", c.get("odds_away_team", "")),
                 "claimed_id": r["ncaa_game_id"]}
        cachekey = tuple(event.values())
        if cachekey not in matches:
            matches[cachekey] = match_event(event, games)
        m = matches[cachekey]
        h, a = team(event["home"]), team(event["away"])
        issues = []
        if r["market"] not in {"moneyline", "spread", "total"}:
            issues.append("UNKNOWN_MARKET")
        if missing(r["sportsbook"]):
            issues.append("MISSING_BOOKMAKER")
        elif r["sportsbook"] not in BOOKS:
            issues.append("UNRECOGNIZED_BOOKMAKER")
        if missing(r["american_odds"]):
            issues.append("MISSING_PRICE")
        elif not american_valid(r["american_odds"]):
            issues.append("INVALID_AMERICAN_PRICE")
        if r["market"] in {"spread", "total"} and number(r["line"]) is None:
            issues.append("MISSING_OR_INVALID_LINE")
        if r["market"] == "total":
            if number(r["line"]) is not None and float(r["line"]) <= 0:
                issues.append("NONPOSITIVE_TOTAL")
            if r["selection"].casefold() not in {"over", "under"}:
                issues.append("TOTAL_SIDE_UNSPECIFIED")
        elif not missing(event["home"]) and not missing(event["away"]) and team(r["selection"]) not in {h, a}:
            issues.append("SELECTION_TEAM_CONFLICT")
        if r["verified_in_raw"] == "implied_not_printed":
            issues.append("LINE_NOT_EXPLICITLY_QUOTED")
        # Accommodate the supplier's literal spelling without altering it.
        if r["verified_in_raw"].startswith("implied") and "LINE_NOT_EXPLICITLY_QUOTED" not in issues:
            issues.append("LINE_NOT_EXPLICITLY_QUOTED")
        if not valid_day(event["date"]):
            issues.append("MISSING_OR_INVALID_ORIGINAL_DATE")
        elif event["date"][:4] != r["season"]:
            issues.append("SEASON_DATE_CONFLICT")
        u = urlparse(r["source_url"])
        if u.scheme not in {"https", "http"} or not u.netloc:
            issues.append("INVALID_SOURCE_URL")
        if not missing(r["archive_url"]):
            au = urlparse(r["archive_url"])
            if au.scheme not in {"http", "https"} or not au.netloc:
                issues.append("INVALID_ARCHIVE_URL")
        for col in ["quote_capture_timestamp", "article_published_at", "article_modified_at", "archive_capture_timestamp", "start_time_utc_used"]:
            if not missing(r[col]) and aware_time(r[col]) is None:
                issues.append("INVALID_OR_NAIVE_" + col.upper())
        decimal = old.get("price_decimal", "")
        if not missing(decimal):
            n = number(decimal)
            if n is None or n <= 1:
                issues.append("INVALID_ORIGINAL_DECIMAL_PRICE")
            elif american_valid(r["american_odds"]) and not decimal_agrees(r["american_odds"], decimal):
                issues.append("AMERICAN_DECIMAL_DISAGREEMENT")
        available = evidence_candidates(r["evidence_file"], files)
        kind, identity = snapshot(r)
        start = aware_time(r["start_time_utc_used"])
        qtime, atime, ptime, mtime = [aware_time(r[col]) for col in ["quote_capture_timestamp", "archive_capture_timestamp", "article_published_at", "article_modified_at"]]
        effective = qtime or atime or ptime
        before = bool(start and effective and effective < start)
        if effective and start and effective >= start:
            issues.append("CLAIMED_OBSERVATION_NOT_BEFORE_START")
        if mtime and start and mtime >= start:
            issues.append("ARTICLE_MODIFIED_AT_OR_AFTER_START")
        # Do not turn a supplier assertion into historical authentication.
        row = {**r, **m, "source_domain": u.netloc, "original_game_date": event["date"],
               "original_home_team": event["home"], "original_away_team": event["away"],
               "original_odds_game_id": old.get("game_id", "NOT_SUPPLIED_ADDITIONAL_ORIGINAL_MISSING"),
               "original_decimal_price": decimal,
               "audit_date_changed_from_original": valid_day(event["date"]) and not missing(r["ncaa_game_date"]) and event["date"] != r["ncaa_game_date"],
               "quote_evidence_files_found": "|".join(str(f.relative_to(ROOT)) for f in available),
               "quote_evidence_available": bool(available), "independent_quote_verified": False,
               "evidence_status": "NOT_INDEPENDENTLY_VERIFIED",
               "permission_status_independent": "UNRESOLVED_REVIEW_REQUIRED_NO_CLEARANCE",
               "snapshot_kind": kind, "snapshot_identity": identity,
               "claimed_observation_before_start": before,
               "article_publication_before_start": bool(start and ptime and ptime < start),
               "article_modification_at_or_after_start": bool(start and mtime and mtime >= start),
               "validation_issues": "|".join(issues), "price_valid": american_valid(r["american_odds"]),
               "candidate_home_key": team(m.get("reference_home", event["home"])),
               "candidate_away_key": team(m.get("reference_away", event["away"]))}
        role = "n/a (total)" if r["market"] == "total" else "home" if m.get("reference_home") and team(r["selection"]) == team(m["reference_home"]) else "away" if m.get("reference_away") and team(r["selection"]) == team(m["reference_away"]) else "UNRESOLVED"
        row["selection_role_independent"] = role
        row["selection_role_agrees"] = role == r["selection_role"] if role != "UNRESOLVED" else "UNRESOLVED"
        if row["quote_evidence_available"]:
            # Fail closed: a filename alone would not implement a source parser.
            raise RuntimeError("Original odds evidence was found. Inspect it manually before classifying historical support.")
        row["candidate_event_key"] = m["matched_game_id"] or "UNMATCHED:" + r["game_id"]
        chronology_flags = {"ARTICLE_MODIFIED_AT_OR_AFTER_START", "CLAIMED_OBSERVATION_NOT_BEFORE_START"}
        structural_issues = set(issues) - chronology_flags
        row["priced_structural_candidate"] = not structural_issues and r["technical_status"] != "rejected"
        pre_capture_claim = bool(start and ((qtime and qtime < start) or (atime and atime < start)))
        row["claimed_pregame_candidate"] = (row["priced_structural_candidate"] and r["grade_audited"] in {"A", "B"}
                                            and before and (not row["article_modification_at_or_after_start"] or pre_capture_claim))
        # A claimed pre-game capture is a conditional lead, not authentication.
        output.append(row)
    return pd.DataFrame(output).fillna("")


def market_groups(rows):
    selected = rows[rows.priced_structural_candidate]
    keys = ["season", "candidate_event_key", "sportsbook", "market", "snapshot_kind", "snapshot_identity", "source_url", "evidence_file", "line_type"]
    groups = []
    for key, group in selected.groupby(keys, sort=True, dropna=False):
        first = group.iloc[0]
        complete = pair_complete(group.to_dict("records"), first.market, first.candidate_home_key, first.candidate_away_key)
        pregame_pair = pair_complete(group[group.claimed_pregame_candidate].to_dict("records"), first.market, first.candidate_home_key, first.candidate_away_key)
        groups.append({**dict(zip(keys, key)), "record_ids": "|".join(group.record_id),
                       "records": len(group), "complete_pair": complete, "claimed_pregame_complete_pair": pregame_pair,
                       "matched_game_id": first.matched_game_id,
                       "capture_timestamp_claim_present": first.snapshot_kind in {"claimed_quote_capture", "claimed_archive_capture"},
                       "authenticated_snapshot": False})
    return pd.DataFrame(groups)


def coverage(rows, groups, games):
    output = []
    for season in ["2023", "2024", "2025", "2026"]:
        r = rows[rows.season.eq(season)]
        matched = r[r.match_status.eq("MATCHED_STAGE2_CANDIDATE")]
        nonreject = matched[matched.technical_status.ne("rejected")]
        g = groups[groups.season.eq(season)]
        mg = g[g.matched_game_id.ne("")]
        ml = mg[mg.market.eq("moneyline") & mg.complete_pair]
        allml = g[g.market.eq("moneyline") & g.complete_pair]
        denom = len(games[games.season.eq(season) & games.proposed_d1_eligible.eq("True")])
        output.append({"season": season, "records": len(r), "source_event_ids": r.game_id.nunique(),
                       "supplier_nonrejected_records": int(r.technical_status.ne("rejected").sum()),
                       "supplier_rejected_records": int(r.technical_status.eq("rejected").sum()),
                       "matched_records_including_supplier_rejects": len(matched),
                       "matched_nonrejected_records": len(nonreject),
                       "unique_matched_games": nonreject.matched_game_id.nunique(),
                       "ambiguous_records": int(r.match_status.eq("AMBIGUOUS").sum()),
                       "ambiguous_event_ids": r[r.match_status.eq("AMBIGUOUS")].game_id.nunique(),
                       "unmatched_records": int(r.match_status.ne("MATCHED_STAGE2_CANDIDATE").sum()),
                       "unmatched_event_ids": r[r.match_status.ne("MATCHED_STAGE2_CANDIDATE")].game_id.nunique(),
                       "date_conflict_records": int(r.match_status.eq("DATE_CONFLICT").sum()),
                       "records_blocked_for_date_team_id_or_excluded_game": int(r.match_status.isin(["DATE_CONFLICT", "UNMATCHED_TEAMS_DATE", "ID_CONFLICT", "EXCLUDED_STAGE2_GAME"]).sum()),
                       "excluded_stage2_records": int(r.match_status.eq("EXCLUDED_STAGE2_GAME").sum()),
                       "priced_structural_candidate_records": int(r.priced_structural_candidate.sum()),
                       "matched_priced_structural_candidate_records": int(nonreject.priced_structural_candidate.sum()),
                       "candidate_complete_moneyline_games_all_events": allml.candidate_event_key.nunique(),
                       "candidate_complete_moneyline_games_matched": ml.matched_game_id.nunique(),
                       "candidate_multiple_complete_moneyline_books_games_matched": int(ml.groupby("matched_game_id").sportsbook.nunique().ge(2).sum()),
                       "claimed_pregame_complete_moneyline_games_matched": ml[ml.claimed_pregame_complete_pair].matched_game_id.nunique(),
                       "candidate_complete_spread_games_matched": mg[mg.market.eq("spread") & mg.complete_pair].matched_game_id.nunique(),
                       "candidate_complete_total_games_matched": mg[mg.market.eq("total") & mg.complete_pair].matched_game_id.nunique(),
                       "candidate_any_priced_spread_games_matched": mg[mg.market.eq("spread")].matched_game_id.nunique(),
                       "candidate_any_priced_total_games_matched": mg[mg.market.eq("total")].matched_game_id.nunique(),
                       "candidate_moneyline_games_with_claimed_capture_matched": ml[ml.capture_timestamp_claim_present].matched_game_id.nunique(),
                       "claimed_opening_records": int(r.is_opening.eq("True").sum()),
                       "claimed_closing_records": int(r.is_closing.eq("True").sum()),
                       "independently_supported_odds_records": 0, "authenticated_pregame_games": 0,
                       "usable_opening_games": 0, "usable_closing_games": 0,
                       "records_requiring_permission_review": int(r.technical_status.ne("rejected").sum()),
                       "records_suitable_for_provisional_academic_analysis": 0, "formally_cleared_records": 0,
                       "reference_candidate_games": denom,
                       "matched_coverage_percent_of_candidates": round(nonreject.matched_game_id.nunique() / denom * 100, 4) if denom else "",
                       "candidate_complete_ml_percent_of_candidates": round(ml.matched_game_id.nunique() / denom * 100, 4) if denom else ""})
    return pd.DataFrame(output)


def permissions(rows):
    original = table(PACKAGE / "source_permissions_audit.csv")
    terms = PACKAGE / "evidence/odds/raw_terms"
    policies = []
    for f in sorted(terms.glob("tos_*.html")):
        soup = BeautifulSoup(f.read_text(), "html.parser")
        for node in soup(["script", "style"]):
            node.decompose()
        text = soup.get_text(" ", strip=True)
        policies.append({"file": str(f.relative_to(ROOT)), "sha256": digest(f), "title": soup.title.get_text() if soup.title else "",
                         "text_characters": len(text),
                         "page_not_found": "not found" in text[:150].casefold(),
                         "automation_restriction_text_present": bool(re.search(r"automated means|page-scrape|reverse-engineer, scrape", text, re.I)),
                         "personal_use_text_present": bool(re.search(r"personal.{0,25}use", text, re.I))})
    comments = {
        "draftkings": ("EXPLICIT_RESTRICTION_IN_SUPPLIED_TERMS_SCOPE_REVIEW", "Supplied DraftKings terms discuss fantasy contests; applicability to sportsbook and nash endpoints needs review. Automated collection and broad content reuse restrictions appear in the text."),
        "actionnetwork": ("EXPLICIT_RESTRICTION_IN_SUPPLIED_TERMS", "Supplied terms restrict automatic and equivalent manual extraction; limited personal home copying is not an explicit academic dataset license."),
        "betmgm": ("UNRESOLVED_GOVERNING_TERMS_UNAVAILABLE", "US pages are short location shells. Blog/other-entity terms cannot establish governing US sportsbook permission."),
        "betonlacrosse": ("UNRESOLVED_TERMS_NOT_LOCATED", "Saved homepage invites historical research; attempted terms pages are 404. Copyright footer is not by itself a prohibition on every internal use of facts."),
        "legalsportsbetting": ("UNRESOLVED_TERMS_NOT_LOCATED", "Saved terms attempts are 404; about page is not a data-use license. Six odds records name no bookmaker."),
        "laxallstars": ("UNRESOLVED_TERMS_NOT_LOCATED", "Saved terms pages contain only a 404 title. No permission can be established from these pages."),
        "internet_archive": ("RESEARCH_ACCESS_IN_HISTORICAL_TERMS_SCOPE_REVIEW", "Saved historical terms dated 2014, captured 2020, discuss research and noninfringing/fair use. They confer no general license to underlying third-party content."),
    }
    result = []
    keys = rows.source_domain.map(DOMAIN_KEYS)
    for r in original.to_dict("records"):
        key = r["source_key"]
        count = int(keys.eq(key).sum())
        access, note = comments.get(key, ("NOT_REVIEWED_FOR_NEW_ACCESS_NO_DIRECT_ODDS_ROWS", "Reference/unused source retained for transparency; no new retrieval or permission clearance in Stage 3."))
        result.append({**r, "direct_odds_records": count,
                       "role": "archive_access_layer" if key == "internet_archive" else "direct_odds_source" if count else "reference_or_unused_source",
                       "access_or_retrieval": access,
                       "internal_academic_analysis": "UNRESOLVED_UNIVERSITY_OR_PROVIDER_REVIEW" if count or key == "internet_archive" else "NOT_ASSESSED_NO_DIRECT_ODDS_ROWS",
                       "redistribution": "NO_AFFIRMATIVE_LICENSE_ESTABLISHED" if count or key == "internet_archive" else "NOT_ASSESSED_NO_DIRECT_ODDS_ROWS",
                       "automated_collection": "RESTRICTED_IN_SUPPLIED_TEXT_SCOPE_REVIEW" if key in {"draftkings", "actionnetwork", "espn", "espn_games_validation", "cradl", "usalacrosse"} else "UNRESOLVED_NOT_AUTHORIZED_BY_ROBOTS",
                       "stage3_review": note, "policy_basis": "SUPPLIED_CACHED_TEXT_ONLY_NOT_CURRENT_LIVE_LEGAL_CLEARANCE",
                       "cleared_in_stage3": False})
    for book in ["FanDuel", "Caesars", "bet365"]:
        result.append({"source": book, "source_key": book.casefold(), "role": "bookmaker_attributed_by_editorial_source",
                       "direct_odds_records": 0, "editorially_attributed_records": int(rows.sportsbook.eq(book).sum()),
                       "access_or_retrieval": "NO_DIRECT_COLLECTION_IN_PACKAGE", "internal_academic_analysis": "UNRESOLVED_UNIVERSITY_REVIEW",
                       "redistribution": "NO_AFFIRMATIVE_LICENSE_ESTABLISHED", "automated_collection": "NOT_ASSESSED_NO_DIRECT_COLLECTION",
                       "stage3_review": "No governing bookmaker policy supplied. Review actual publisher terms and applicable rights; bookmaker attribution alone neither grants nor disproves internal academic-use permission.",
                       "policy_basis": "NO_SUPPLIED_GOVERNING_BOOKMAKER_TERMS", "cleared_in_stage3": False})
    return pd.DataFrame(result).astype(object).fillna(""), policies


def evidence_sample(rows):
    sample = choose_sample(rows)
    sample["sample_method"] = "seed519_sha256_greedy_marginal_strata_then_hash_fill_n40"
    sample["game_genuine_evidence"] = sample.apply(lambda r: r.stage2_factual_status if r.match_status == "MATCHED_STAGE2_CANDIDATE" else "NOT_CONFIRMED_FOR_THIS_ORIGINAL_DATE_AND_PAIR", axis=1)
    sample["quoted_price_present_in_original_evidence"] = "NOT_INDEPENDENTLY_VERIFIED_ORIGINAL_MISSING"
    sample["named_book_supported_by_original_evidence"] = "NOT_INDEPENDENTLY_VERIFIED_ORIGINAL_MISSING"
    sample["pregame_documentation_authenticated"] = "NOT_INDEPENDENTLY_VERIFIED_ORIGINAL_MISSING"
    sample["home_away_review"] = sample.apply(lambda r: "MATCHES_STAGE2_REFERENCE" if r.match_status == "MATCHED_STAGE2_CANDIDATE" and r.raw_listed_home_agrees is True else "RAW_LISTING_REVERSED_VS_STAGE2_REFERENCE_SELECTION_IDENTITY_RETAINED" if r.match_status == "MATCHED_STAGE2_CANDIDATE" else "UNRESOLVED", axis=1)
    sample["independent_review_note"] = "Referenced historical file absent, including basename search of supplied package. Evidence detail is supplier prose; hash list and today's URL status are not quote content. No restricted fetch attempted."
    return sample


def markdown(frame):
    def cell(v):
        return str(v).replace("|", " / ").replace("\n", " ")
    return "| " + " | ".join(frame.columns) + " |\n| " + " | ".join("---" for _ in frame.columns) + " |\n" + "\n".join("| " + " | ".join(cell(v) for v in row) + " |" for row in frame.itertuples(index=False, name=None))


def run():
    odds = table(PACKAGE / "odds_provenance_audit.csv")
    original = table(PACKAGE / "originals/ncaa_lacrosse_historical_odds_2025.csv")
    crosswalk = table(PACKAGE / "corrected/odds_game_to_ncaa_game_crosswalk_corrected.csv")
    games = table(REPORTS / "grok_stage2_game_assessments.csv")
    files = [f for f in PACKAGE.rglob("*") if f.is_file()]
    rows = inspect_rows(odds, crosswalk, original, games, files)
    groups = market_groups(rows)
    cov = coverage(rows, groups, games)
    sample = evidence_sample(rows)
    rights, policy_checks = permissions(rows)
    semantic_keys = ["season", "candidate_event_key", "sportsbook", "market", "selection", "line", "american_odds", "snapshot_kind", "snapshot_identity", "source_url", "evidence_file", "line_type"]
    rows["same_observation_duplicate"] = rows.duplicated(semantic_keys, keep=False)
    checks = {"python_version": __import__("sys").version, "environment": __import__("sys").executable,
              "records": len(rows), "raw_event_ids": rows.game_id.nunique(), "full_row_duplicates": int(odds.duplicated().sum()),
              "duplicate_record_ids": int(odds.record_id.duplicated().sum()),
              "same_observation_duplicate_rows": int(rows.same_observation_duplicate.sum()),
              "supplier_repeat_observations": int((~rows.repeat_observation_of.map(missing)).sum()),
              "source_domains": rows.source_domain.value_counts().to_dict(), "sportsbooks": rows.sportsbook.value_counts().to_dict(),
              "markets": rows.market.value_counts().to_dict(), "grades": rows.grade_audited.value_counts().to_dict(),
              "supplier_technical_status": rows.technical_status.value_counts().to_dict(),
              "missing_values": {c: int(odds[c].map(missing).sum()) for c in odds},
              "issues": dict(Counter(issue for value in rows.validation_issues for issue in value.split("|") if issue)),
              "matching": rows.match_status.value_counts().to_dict(),
              "quote_evidence_references": rows.evidence_file.nunique(),
              "quote_evidence_available_records": int(rows.quote_evidence_available.sum()),
              "historically_supported_quotes": 0, "evidence_unresolved_records": len(rows),
              "sample_size": len(sample), "sample_strata": {c: sorted(sample[c].unique().tolist()) for c in ["sportsbook", "season", "market", "grade_audited", "source_domain", "source_dataset", "technical_status"]},
              "provisional_academic_analysis_records": 0, "formally_cleared_records": 0,
              "current_policy_network_checks": 0, "policy_capture_checks": policy_checks,
              "original_odds_sha256": digest(PACKAGE / "originals/ncaa_lacrosse_historical_odds_2025.csv"),
              "additional_525_original_rows_supplied": False,
              "opening_claim_records": int(rows.is_opening.eq("True").sum()), "closing_claim_records": int(rows.is_closing.eq("True").sum())}
    original_index = original.set_index("record_id")
    checks["original_1470_field_conflicts"] = {}
    for audited, source in [("american_odds", "price_american"), ("line", "line"), ("market", "market"), ("selection", "side"), ("sportsbook", "sportsbook"), ("source_url", "source_url")]:
        differences = [r["record_id"] for r in odds[odds.source_dataset.eq("original")].to_dict("records")
                       if r[audited] != original_index.loc[r["orig_record_id"], source]
                       and not (missing(r[audited]) and missing(original_index.loc[r["orig_record_id"], source]))]
        checks["original_1470_field_conflicts"][audited] = differences
    checks["supplier_original_event_id_normalizations"] = rows[rows.source_dataset.eq("original") & rows.game_id.ne(rows.original_odds_game_id)].record_id.tolist()
    checks["supplier_partition_checks"] = {}
    for filename, status in [("odds_quarantine_permission_required.csv", "requires_permission"), ("odds_rejected.csv", "rejected"), ("odds_cleared_for_analysis.csv", "cleared_for_analysis")]:
        partition = table(PACKAGE / "odds" / filename)
        expected_ids = set(odds[odds.status.eq(status)].record_id)
        checks["supplier_partition_checks"][filename] = {"rows": len(partition), "columns": len(partition.columns),
                                                       "ids_exactly_equal_audit_partition": set(partition.record_id) == expected_ids}
    rows.to_csv(REPORTS / "grok_stage3_record_checks.csv", index=False)
    groups.to_csv(REPORTS / "grok_stage3_market_groups.csv", index=False)
    cov.to_csv(REPORTS / "grok_stage3_odds_coverage.csv", index=False)
    rights.to_csv(REPORTS / "grok_stage3_source_permissions.csv", index=False)
    rows[rows.match_status.ne("MATCHED_STAGE2_CANDIDATE")].to_csv(REPORTS / "grok_stage3_unmatched_odds.csv", index=False)
    sample.to_csv(REPORTS / "grok_stage3_evidence_sample.csv", index=False)
    (REPORTS / "grok_stage3_checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    write_report(rows, cov, sample, checks)
    print(json.dumps({"records": len(rows), "coverage": cov.to_dict("records"), "issues": checks["issues"], "sample_size": len(sample)}, indent=2))


def write_report(rows, cov, sample, checks):
    selected = cov[["season", "records", "source_event_ids", "unique_matched_games", "matched_nonrejected_records", "unmatched_records", "candidate_complete_moneyline_games_matched", "candidate_multiple_complete_moneyline_books_games_matched", "candidate_complete_spread_games_matched", "candidate_complete_total_games_matched"]].copy()
    selected.columns = ["Season", "Rows", "Source event IDs", "Matched games", "Matched nonrejected rows", "Unmatched rows", "Candidate paired ML games", "Candidate multi-book ML games", "Candidate paired spreads", "Candidate paired totals"]
    conflicts = rows[rows.match_status.ne("MATCHED_STAGE2_CANDIDATE")].groupby(["season", "game_id", "original_game_date", "match_status"], dropna=False).agg(records=("record_id", "size"), candidate_ids=("candidate_game_ids", "first")).reset_index()
    issue_frame = pd.DataFrame(checks["issues"].items(), columns=["Independent check", "Records"])
    missing_frame = pd.DataFrame(checks["missing_values"].items(), columns=["Column", "Missing records"])
    rejected = rows[rows.technical_status.eq("rejected")][["record_id", "market", "american_odds", "reason"]]
    c25 = cov[cov.season.eq("2025")].iloc[0]
    sample_summary = pd.DataFrame({"Dimension": list(checks["sample_strata"]), "Values covered": [", ".join(v) for v in checks["sample_strata"].values()]})
    report = f"""# Stage 3: independent odds audit

Audit date: 2026-11-10. Offline, read-only review in `dsf-lacrosse`, Python 3.11. No new dataset, source retrieval, supplier-script execution, model run, main-data merge, or permission clearance.

## Decision

**All 1,995 records were mechanically inspected. Independently authenticated historical odds quotations: 0.** This is an evidence-availability finding, not a finding that all quotes are false. All {checks['quote_evidence_references']} distinct historical quote-file references are absent from the supplied package, including a basename search. The 40-observation stratified review therefore returns **NOT INDEPENDENTLY VERIFIED** for every quote, bookmaker attribution, and pre-game-content claim. A URL, a hash of an omitted file, supplier prose, or a current HTTP 200 cannot demonstrate what a historical page contained.

The package supports conditional structure/matching estimates below, but does **not yet support a defensible bookmaker-versus-model experiment**. Provisional academic-analysis records approved by this audit: **0**; formally cleared: **0**. Internal academic use of factual observations and redistribution of source content are separate questions. Lack of a redistribution license alone is not treated as proof that all internal academic analysis is prohibited. Evidence and applicable permissions must be resolved before changing quarantine status.

## Inputs and actual inventory

Package root: `data/incoming/grok/stage1_28f5677d90c3/audit_package/`.

* `odds_provenance_audit.csv`: **1,995 × 46**, the combined supplier audit, not an independent raw source.
* `originals/ncaa_lacrosse_historical_odds_2025.csv`: **1,470 × 23**, despite its filename covers **2023–2026**; SHA-256 `{checks['original_odds_sha256']}`.
* The external original `ncaa_lacrosse_additional_odds_2023_2026.csv` (**525 rows claimed**) was omitted; these observations exist only in the combined supplier-derived audit. Their original decimal fields/event metadata cannot be checked against that omitted CSV.
* `odds/odds_quarantine_permission_required.csv`: **1,983 × 46**; `odds/odds_rejected.csv`: **12 × 46**; `odds/odds_cleared_for_analysis.csv`: **0 × 46**. These are partitions, not additional unique quotes.
* `odds/odds_game_usability.csv` (**306 × 30**), corrected crosswalk (**308 × 17**), corrections (**11 × 7**), and source-permissions audit (**19 × 10**) are supplier claims; this audit recomputes game matches and market groups instead of accepting their totals.
* Evidence consists of policy/robots captures, source URL and live-status lists, and `evidence/odds/raw_odds_evidence_sha256.txt`; **no referenced historical quote HTML/JSON contents** are present. Policy pages, Bet On Lacrosse's homepage, and LegalSportsBetting's about page are not the referenced historical odds articles.

Counts match Grok's partition: **1,887 supplier-verified / 96 supplier-provisional / 12 supplier-rejected; 1,983 permission-required / 0 cleared**. Supplier evidence grades: **A 702, B 1,207, C 86**. Those grades have not been independently authenticated. There are **308 source event-ID strings**, not 308 independently established distinct genuine games. Grok merges two differently dated pairs of 2023 IDs; without the missing original evidence this audit does not accept those postponement attachments automatically.

Sportsbook attributions: DraftKings 889, BetMGM 564, FanDuel 236, Caesars 164, bet365 112, **missing 30**. Five named books; names are normalized string labels, not independently authenticated operator attribution. Markets: spread 711, total 701, moneyline 583. Source-domain counts:

{markdown(pd.DataFrame(checks['source_domains'].items(), columns=['Source domain', 'Records']))}

All IDs are unique; full-row duplicates: {checks['full_row_duplicates']}; exact same-observation duplicates under this audit's source/snapshot-aware key: {checks['same_observation_duplicate_rows']}. Grok separately marks seven cross-publication repeats as rejected and 50 later observations as repeats. Equal prices at different dates/books/articles do not alone establish duplicate historical observations; missing evidence prevents authenticating those seven cross-publication rejection reasons. No deduplication was applied to originals.

The three status-partition files' actual ID sets agree with the combined audit. For all 1,470 available original rows, American price, line, market, selection, bookmaker and source URL agree with the supplier audit (normalizing only empty/null tokens for comparison). The supplier renamed six original event IDs for Colgate–UAlbany, February 17, 2024, from `2024-02-17_colgate_vs_ualbany` to `2024-02-17_albany_vs_colgate`; `original_odds_game_id` and original row ID are retained in the new ledger. That alias/order normalization is distinct from silently correcting event dates or prices.

## Price, structure, orientation, and timestamps

American prices must be finite signed integer values with absolute value ≥100; decimal prices must exceed 1 and agree with American conversion to half a unit of their printed decimal precision, with a minimum 0.0000001 serialization tolerance, when both exist in the original 1,470 rows. For example, 1.8696 is consistent with −115; ordinary rounding and ~0.00000001 feed-serialization noise are not data errors. Conversion is a validation calculation, never a fabricated source field. Missing prices are not automatically invalid lines: a published unpriced spread/total is useful descriptive information but cannot be used as a priced bet. **No -110 defaults, opposite-side prices, or negated inferred spreads were added.** Actual check counts (overlapping flags):

{markdown(issue_frame)}

The two ±8 moneylines are independently invalid American prices. Three claimed sign errors and seven claimed cross-source duplicates remain held as supplier rejects; their exact historical source-based reasons cannot be independently confirmed. Supplier's rejected record IDs and explanations:

{markdown(rejected)}

For spread pairing both explicit team selections, valid prices, and opposite signed lines are required. For totals both explicit Over and Under at the same positive total are required; six undirected total entries are not an Over or Under quote. Line-only rows cannot become priced pairs. The 39 supplier-marked inferred spread lines are excluded from priced structural candidates, even if the implied opposite handicap would be mathematically conventional.

Two-sided markets group **same event, book, market, source URL, evidence file, claimed snapshot/version and line type**. Books and distinct snapshot times are never pooled. Publication/modification timestamps identify a claimed editorial version only; they are **not sportsbook quote timestamps**. A complete pair in this table is therefore a **conditional supplied-data pair**, not authenticated historical betting coverage. Multiple books requires ≥2 separately complete moneyline pairs, not simply two bookmaker labels somewhere in a game's rows. Spread lines are attached to the selected team; reversing a publisher's home/away order does not negate the line.

All nonmissing timestamp fields are checked for parseable timezone-aware ISO timestamps. Quotes/archives/publication are separately compared with the supplier's claimed start; starts themselves are not independently authenticated in Stage 3. A pre-game publication does not establish that today's mutable article retained its pre-game odds. A modification at or after start blocks the separate claimed-pre-game subset unless a pre-game capture is also claimed; neither claim authenticates the original. Structural pairs do not imply pre-game availability. Exact sportsbook transaction/quote times cannot be established from the missing snapshots; capture time, even if recovered, is an observation time rather than necessarily the operator's own update time.

## Independent game matching and coverage

Reference: `reports/grok_stage2_game_assessments.csv`. Stage 2 proposed D-I-versus-D-I candidates are **559 / 570 / 578** in 2023 / 2024 / 2025; their full-season completeness and permissions remain unresolved. Match results are candidate joins, not new certification of every game. No reference file for 2026 is supplied, and no 2026 odds are forced onto 2025 games.

Require original date, season, both canonical team identities and a compatible event ID where present. For original rows use the unchanged original odds CSV; for additional rows use the crosswalk's original event fields, whose raw originals are missing. Use Stage 2's closed aliases plus the explicit unambiguous spellings `St. Joe's` → `Saint Joseph's` and `St. John's - New York` → `St. John's (NY)` seen in the crosswalk/reference. No fuzzy matching. Supplier-adjusted NCAA date/teams alone cannot repair an original-date/team conflict. Original home/away order is checked separately; odds selection identity is preserved. The per-row ledger retains IDs, dates, roles, source flags, and all independent findings.

{markdown(selected)}

Across supplied reference seasons: **{int(cov.unique_matched_games.sum())} distinct matched candidate games**, **{int(cov.matched_nonrejected_records.sum())} nonrejected matched rows**; **{int(cov.unmatched_records.sum())} rows** remain unattached. Candidate complete matched moneylines: **{int(cov.candidate_complete_moneyline_games_matched.sum())} games**; candidate multi-book complete moneylines: **{int(cov.candidate_multiple_complete_moneyline_books_games_matched.sum())}**; candidate complete priced spreads / totals: **{int(cov.candidate_complete_spread_games_matched.sum())} / {int(cov.candidate_complete_total_games_matched.sum())}**. These are structural counts, never verified pre-game coverage. **{int(cov.records_blocked_for_date_team_id_or_excluded_game.sum())} rows** are blocked specifically by original-date/team conflicts; none references an excluded Stage 2 game. Ambiguous candidate joins: **0**. Out-of-reference-season and missing-date observations are unresolved, not automatically false games.

All table market counts are **unverified structural candidates**, with named book, valid supplied price/line/selection/date, no supplier rejection or inferred-line flag, and a same-source/version pair. They do not require successful pre-game authentication. A separately reported **claimed-pre-game** subset additionally requires supplier grade A/B and a claimed observation before the claimed start; post-start modification requires a claimed pre-game capture to retain this lead. Neither subset is cleared for analysis. Differences from Grok's 269 paired-moneyline / 17 multi-book / 105 priced-spread / 105 priced-total game claims reflect game-date matching, filters and snapshot grouping. `grok_stage3_odds_coverage.csv` also gives raw-event candidate counts, one-sided priced spread/total counts, capture-claim counts, denominators, and record-level counts.

**2025:** {c25.unique_matched_games} matched nonrejected candidate games / **578 eligible Stage 2 candidates** = **{c25.matched_coverage_percent_of_candidates:.2f}%**, or {c25.unique_matched_games/580*100:.2f}% of the frozen original 580 records. Candidate paired moneylines: **{c25.candidate_complete_moneyline_games_matched}** ({c25.candidate_complete_ml_percent_of_candidates:.2f}% of 578); candidate multi-book paired moneylines: **{c25.candidate_multiple_complete_moneyline_books_games_matched}**. None is yet independently authenticated or approved for use. Even after evidence recovery, an article-selected subset may be biased toward prominent games and cannot establish full-season betting coverage.

Original-event rows not safely attached to an eligible result:

{markdown(conflicts)}

The three proposed 2023 one-day postponement corrections (Hofstra–Merrimack, Holy Cross–Providence, Towson–UMBC) are not silently applied. UNC–Rutgers versus Denver–UNC is a team-label conflict: do not substitute Denver just because supplier prose says the table had a typo. Mercyhurst–UMass Lowell has a February 16 versus February 14, 2025 date conflict (reference **6439959**, school-corroborated in Stage 2). **Grok's assertion that no Binghamton–St. Bonaventure game appears in the index is incorrect:** reference **6386465** is a school-corroborated March 25, 2025 game, Binghamton 6–5 St. Bonaventure. The odds event is February 15; without original source evidence, do not assert postponement or match these automatically. Undated picks remain unmatched; publication date is not substituted for game date. No odds reference targets either Stage 2 excluded 2025 game. All unresolved/ambiguous rows, including 2026 events outside the reference, are listed in `grok_stage3_unmatched_odds.csv`. No excluded or incorrect-date event enters the matched market counts.

## Reproducible independent evidence sample

**40 unique observations**; deterministic SHA-256 rank of `519|record_id`, greedy maximum marginal coverage of book/year/market/grade/source-domain/dataset/supplier-status strata, then rank-based fill. This is a diagnostic stratified sample, not a probability sample for estimating a population error rate. It is not the Cartesian product of every stratum.

{markdown(sample_summary)}

All referenced originals are absent. Each sample row separately records genuine-game corroboration status inherited from Stage 2, original orientation comparison, missing source evidence, price/book authentication status and pre-game verification status. **0/40 price quotes independently confirmed; 40/40 NOT INDEPENDENTLY VERIFIED.** A Stage 2 school-corroborated result can establish that a game was genuine without establishing that any bookmaker offered the stated price. The other 1,955 rows received mechanical checks and evidence-availability checks, not a successful original-content spot-check. No implication of fabrication or source verification is made from supplier flags alone.

## Permission review: separate questions

`grok_stage3_source_permissions.csv` retains all 19 supplier source rows and adds three bookmaker-attribution rows (FanDuel, Caesars, bet365). It separately records access/retrieval, internal academic use, redistribution, automation, evidence scope and clearance. All direct source classes remain unresolved or restricted pending applicability review; no flag was cleared. All **1,983 nonrejected records** still require appropriate review; the 12 rejects are also retained, not released. Permission review alone would not remedy missing factual evidence.

* **DraftKings:** saved `tos_draftkings2.html` contains automation and personal/content-use restrictions; its fantasy-contest wording makes governing sportsbook/nash scope a question requiring review. The other saved terms attempt is a 404. No new DraftKings access attempted.
* **Action Network:** saved terms restrict automatic and equivalent manual extraction and grant limited personal home copying. No scraping/manual circumvention or new article retrieval attempted. Applicability to the proposed internal research workflow requires provider or university review.
* **BetMGM:** supplied US terms pages are short geolocation shells. Blog or another legal entity's terms cannot prove governing US sportsbook rights. Status unresolved; no bypass attempted.
* **Bet On Lacrosse:** saved homepage invites historical research but does not itself supply a dataset license; attempted terms pages are 404. Copyright notice alone does not settle permissible internal use of factual prices. Review the intended workflow and rights separately.
* **LegalSportsBetting / Lacrosse All Stars:** unavailable/404 terms do not grant permission or prove every internal factual use forbidden. Missing bookmaker attribution and undated content are additional factual problems for some rows.
* **Internet Archive:** supplied terms are historical, not a current clearance. Research/noninfringing-use language is not a general license to every captured third party's material. No archived quote body was supplied; no restricted archival retrieval attempted.
* **Other named books:** no direct FanDuel/Caesars/bet365 source collections or governing policies supplied. Editorial bookmaker attribution does not by itself determine applicable rights. Review publisher permissions and relevant underlying rights rather than assuming every editorial fact requires every operator's written license.
* NCAA/SIDEARM/ESPN rows are reference-source permissions carried forward, not new game audits. Supplier's The Odds API “cleared” label applies to **zero observations** and does not clear this package or verify NCAA coverage. No purchase, credential use, new provider investigation, or odds collection occurred.

This is a forensic review of supplied policy captures, not a current legal opinion. Cached policy presence and robots permission do not establish contractual applicability, historic policy versions, copyright ownership, lawful acquisition, fair use or a redistribution license. Resolve those questions through the appropriate university/provider review. Private factual analysis, source-page copying, publication of derived research and redistribution of raw files should be evaluated separately. Existing quarantine stays intact; no new permission restrictions on already authorized internal auditing are inferred.

## Usability, opening/closing, and next evidence needed

Supplier claims **{checks['opening_claim_records']} opening rows**, zero closing rows. Only explicit source-text claims count even provisionally; earliest/latest observed price is not automatically opening/closing. No original opening sentence or pre-game snapshot can be authenticated here, so **usable authenticated opening games 0 / closing games 0**. Same-price later captures are observations rather than line movement; authenticated movement cannot be established without evidence. All **1,995** rows have unresolved quote evidence, including the 12 held rejects. Historically supported priced records, authenticated pre-game games, and cleared comparable paired markets are all **0**.

To compare model home-win probabilities with bookmaker probabilities, first obtain the already-collected historical quote HTML/JSON (and original 525-row CSV) with source URL/capture metadata and lawful provenance; authenticate both teams' moneylines at one book and one pre-game observation; resolve original-date/team-label conflicts; obtain appropriate internal-use review. Only then calculate raw implied probabilities and remove overround within that same two-sided market (with method disclosed), mapping selection identity to NCAA home/away. Do not pool different books or times, use closing lines that were not published, invent -110 spread prices, or compute betting returns from unpriced lines. This task does not fetch those missing materials, train models, or merge any odds.

## Missing values (literal null/empty tokens normalized only in this audit view)

{markdown(missing_frame)}

Raw files are unchanged. Audit derivations do not fill source fields. A null NCAA reference in 2026 is distinct from a missing original event date; 858 null prices are distinct from malformed ±8 prices. Publication, archive, quote-capture and modification timestamps retain their distinct meanings.

## Reproduction and preservation

Run from the repository root:

```sh
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python src/audit_grok_odds.py
/Users/kiri/miniconda3/bin/conda run --no-capture-output -n dsf-lacrosse python -m pytest -q tests/test_grok_stage3_odds.py tests/test_grok_stage2_games_stats.py tests/test_validate_incoming.py
```

The script writes only Stage 3 report artifacts. It has no network path and imports only our existing Stage 2 identity helpers, never scripts from the ZIP. It fails closed if original odds evidence unexpectedly becomes available, because that requires an actual content inspection rather than a filename-based approval. Tests include clearly labeled synthetic examples and read-only actual-package invariants. Final test totals, existence checks and SHA-256 comparison against all **457** pre-existing files are in `reports/grok_stage3_verification.json`; no original dataset, feature/prediction file or earlier report is intentionally changed. Full-season coverage remains unverified, and no research proposal is written.
"""
    (REPORTS / "grok_stage3_odds_audit.md").write_text(report)


if __name__ == "__main__":
    run()
