#!/usr/bin/env python3
"""Generate a public commit calendar and code-change dashboard for RCZ88.

The commit calendar covers commits attributed to RCZ88 in public repositories
owned by RCZ88, excluding this profile repository. The code-change totals inspect
up to the 25 newest matching commits from the last 30 days.
"""
from __future__ import annotations
import argparse, json, time, urllib.error, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from typing import Any

OWNER = "RCZ88"
PROFILE_REPO = "RCZ88/RCZ88"
API = "https://api.github.com"
SEARCH_LIMIT = 1000
DIFF_SAMPLE_LIMIT = 25
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "RCZ88-engineering-activity-dashboard/1.0",
}

def get_json(url: str, attempts: int = 4) -> Any:
    """GET public GitHub API JSON with bounded retries on transient throttling."""
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            retry_after = error.headers.get("Retry-After")
            rate_limited = error.headers.get("X-RateLimit-Remaining") == "0"
            transient = error.code in (429, 500, 502, 503, 504) or (error.code == 403 and (retry_after or rate_limited))
            if transient and attempt < attempts - 1:
                delay = int(retry_after) if retry_after and retry_after.isdigit() else min(2 ** (attempt + 1), 20)
                time.sleep(delay)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if attempt == attempts - 1:
                raise
            time.sleep(min(2 ** attempt, 8))
    raise RuntimeError("GitHub API request retry loop ended unexpectedly")

def parsed_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None

def in_scope(item: dict[str, Any]) -> bool:
    repo = item.get("repository") or {}
    owner = repo.get("owner") or {}
    return (
        owner.get("login", "").casefold() == OWNER.casefold()
        and repo.get("full_name", "").casefold() != PROFILE_REPO.casefold()
        and not repo.get("private", False)
    )

def search_user_commits(start: datetime, end: datetime) -> tuple[list[dict[str, Any]], int, bool]:
    # Search is global because the API's repository commits endpoint requires
    # one request per repository. Filter the returned public results to owned repos.
    q = f"author:{OWNER} committer-date:>={start.date().isoformat()} committer-date:<={(end.date() + timedelta(days=1)).isoformat()}"
    results: list[dict[str, Any]] = []
    page, total = 1, 0
    while True:
        params = urllib.parse.urlencode({"q": q, "sort": "committer-date", "order": "desc", "per_page": 100, "page": page})
        payload = get_json(f"{API}/search/commits?{params}")
        total = int(payload.get("total_count", 0))
        batch = payload.get("items", [])
        results.extend(item for item in batch if in_scope(item))
        if len(batch) < 100 or page * 100 >= min(total, SEARCH_LIMIT):
            break
        page += 1
        time.sleep(6.2)  # Unauthenticated GitHub Search API: stay below its per-minute limit.
    unique = {item["sha"]: item for item in results if item.get("sha")}
    commits = list(unique.values())
    commits.sort(
        key=lambda item: parsed_datetime(((item.get("commit") or {}).get("committer") or {}).get("date"))
        or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return commits, total, total > SEARCH_LIMIT

def recent_diff_stats(commits: list[dict[str, Any]], now: datetime) -> dict[str, int]:
    cutoff = now - timedelta(days=29)
    recent = []
    for item in commits:
        raw_date = ((item.get("commit") or {}).get("committer") or {}).get("date")
        timestamp = parsed_datetime(raw_date)
        if timestamp and cutoff <= timestamp <= now:
            recent.append(item)
    sample = recent[:DIFF_SAMPLE_LIMIT]
    added = deleted = touched = analyzed = 0
    for item in sample:
        repo = (item.get("repository") or {}).get("full_name")
        sha = item.get("sha")
        if not repo or not sha:
            continue
        url = f"{API}/repos/{repo}/commits/{urllib.parse.quote(sha, safe='')}"
        try:
            details = get_json(url)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as error:
            # Continue through individual missing/temporarily inaccessible diffs.
            print(f"Warning: could not inspect {repo}@{sha[:7]} (HTTP {error.code})")
            continue
        stats = details.get("stats") or {}
        added += int(stats.get("additions", 0))
        deleted += int(stats.get("deletions", 0))
        touched += len(details.get("files") or [])
        analyzed += 1
        time.sleep(0.15)
    return {"recent_found": len(recent), "analyzed": analyzed, "added": added, "deleted": deleted, "touched": touched}

def public_push_count(now: datetime) -> tuple[int, bool]:
    cutoff = now - timedelta(days=29)
    events = []
    for page in range(1, 4):  # Public event feed returns at most 300 items here.
        params = urllib.parse.urlencode({"per_page": 100, "page": page})
        batch = get_json(f"{API}/users/{OWNER}/events/public?{params}")
        events.extend(batch)
        if len(batch) < 100:
            break
    pushes = sum(
        1 for event in events
        if event.get("type") == "PushEvent"
        and (dt := parsed_datetime(event.get("created_at"))) is not None
        and cutoff <= dt <= now
    )
    oldest = parsed_datetime(events[-1].get("created_at")) if events else None
    may_be_truncated = len(events) >= 300 and oldest is not None and oldest >= cutoff
    return pushes, may_be_truncated

def render_svg(daily: Counter[str], total: int, search_truncated: bool, diffs: dict[str, int],
               pushes: int | None, push_truncated: bool, now: datetime) -> str:
    end_date = now.date()
    start_date = end_date - timedelta(days=364)
    first_day = start_date - timedelta(days=start_date.weekday())
    last_day = end_date + timedelta(days=6-end_date.weekday())
    weeks = (last_day - first_day).days // 7 + 1
    cell, gap, step, x0, y0 = 10, 3, 13, 44, 112
    grid_width = weeks * step - gap
    grid_right = x0 + grid_width
    colors = ["#172536", "#164e49", "#147d70", "#22a38c", "#72e1bf"]
    def color_for(n: int) -> str:
        return colors[0] if n <= 0 else colors[1] if n == 1 else colors[2] if n <= 3 else colors[3] if n <= 6 else colors[4]
    def fmt(value: int, lower: bool = False) -> str:
        return ("≥" if lower else "") + f"{value:,}"
    commit_total = fmt(total, search_truncated)
    push_total = "N/A" if pushes is None else fmt(pushes, push_truncated)
    days_active = sum(1 for n in daily.values() if n > 0)
    sample_capped = diffs["recent_found"] > DIFF_SAMPLE_LIMIT
    p = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="460" viewBox="0 0 1200 460" role="img" aria-labelledby="chart-title chart-desc">',
        f'<title id="chart-title">RCZ88 commit activity and recent code changes</title><desc id="chart-desc">{escape(commit_total)} attributed commits in the last year, {days_active} active days, and diff details from {diffs["analyzed"]} recent commits.</desc>',
        '<defs><linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0b1220"/><stop offset="1" stop-color="#142438"/></linearGradient></defs>',
        '<rect width="1200" height="460" rx="18" fill="url(#panel)"/><path d="M26 79H1174" stroke="#2a3d52"/>',
        '<g font-family="ui-monospace,SFMono-Regular,Menlo,monospace">',
        '<text x="32" y="29" font-size="10" letter-spacing="2" fill="#7dd3fc">ENGINEERING ACTIVITY / RCZ88</text>',
        '<text x="32" y="58" font-size="22" fill="#f1f5f9">Commit history &amp; code changes</text>',
        f'<text x="1168" y="43" text-anchor="end" font-size="27" fill="#f8fafc">{escape(commit_total)}</text>',
        '<text x="1168" y="61" text-anchor="end" font-size="10" fill="#8da3b8">COMMITS / 365 DAYS</text></g>',
    ]
    for offset in range((last_day-first_day).days+1):
        current = first_day + timedelta(days=offset)
        if current.day == 1 and start_date <= current <= end_date:
            p.append(f'<text x="{x0+(offset//7)*step}" y="100" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#91a4b8">{current.strftime("%b")}</text>')
    for name, row in (("Mon", 0), ("Wed", 2), ("Fri", 4)):
        p.append(f'<text x="34" y="{y0+row*step+8}" text-anchor="end" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="#71869b">{name}</text>')
    for offset in range((last_day-first_day).days+1):
        current = first_day + timedelta(days=offset)
        if start_date <= current <= end_date:
            count = daily.get(current.isoformat(), 0)
            title = escape(f"{current.isoformat()}: {count} commit(s)")
            p.append(f'<rect x="{x0+(offset//7)*step}" y="{y0+current.weekday()*step}" width="{cell}" height="{cell}" rx="2" fill="{color_for(count)}" stroke="#304154" stroke-width=".35"><title>{title}</title></rect>')
    card_x = max(780, grid_right + 32)
    card_w = 1170 - card_x
    p += [
        f'<rect x="{card_x}" y="{y0-2}" width="{card_w}" height="66" rx="10" fill="#102033" stroke="#2c4156"/>',
        f'<text x="{card_x+15}" y="{y0+18}" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="#7dd3fc">ACTIVE DAYS / YEAR</text>',
        f'<text x="{card_x+15}" y="{y0+48}" font-family="sans-serif" font-size="25" fill="#f8fafc">{days_active:,}</text>',
        f'<rect x="{card_x}" y="{y0+76}" width="{card_w}" height="66" rx="10" fill="#102033" stroke="#2c4156"/>',
        f'<text x="{card_x+15}" y="{y0+96}" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="#7dd3fc">PUBLIC PUSHES / 30 DAYS</text>',
        f'<text x="{card_x+15}" y="{y0+126}" font-family="sans-serif" font-size="25" fill="#f8fafc">{escape(push_total)}</text>',
    ]
    if push_truncated:
        p.append(f'<text x="{card_x+15}" y="{y0+155}" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="#fbbf24">Event feed may be capped</text>')
    base_y, gap_x, total_w = 268, 14, 1136
    card_w2 = (total_w-3*gap_x)/4
    metrics = [
        ("LINES ADDED", f'+{diffs["added"]:,}', "30 days · sampled commit diffs", "#5eead4"),
        ("LINES DELETED", f'−{diffs["deleted"]:,}', "30 days · sampled commit diffs", "#fda4af"),
        ("FILES TOUCHED", f'{diffs["touched"]:,}', "Across inspected commits", "#93c5fd"),
        ("DIFFS INSPECTED", f'{diffs["analyzed"]:,}/{diffs["recent_found"]:,}', "Latest commits in 30 days", "#c4b5fd"),
    ]
    for index, (heading, value, subheading, foreground) in enumerate(metrics):
        x = 32 + index*(card_w2+gap_x)
        p += [
            f'<rect x="{x:.1f}" y="{base_y}" width="{card_w2:.1f}" height="78" rx="10" fill="#101f31" stroke="#2b4055"/>',
            f'<text x="{x+14:.1f}" y="{base_y+20}" font-family="ui-monospace,Menlo,monospace" font-size="9" letter-spacing=".8" fill="#91a4b8">{heading}</text>',
            f'<text x="{x+14:.1f}" y="{base_y+48}" font-family="sans-serif" font-size="23" fill="{foreground}">{value}</text>',
            f'<text x="{x+14:.1f}" y="{base_y+65}" font-family="ui-monospace,Menlo,monospace" font-size="8.5" fill="#71869b">{subheading}</text>',
        ]
    p.append('<text x="32" y="379" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#8296aa">COMMIT DENSITY</text>')
    for index, colour in enumerate(colors):
        p.append(f'<rect x="{151+index*16}" y="369" width="10" height="10" rx="2" fill="{colour}"/>')
    p.append('<text x="243" y="379" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#8296aa">LESS TO MORE COMMITS</text>')
    p += [
        f'<text x="32" y="411" font-family="sans-serif" font-size="10" fill="#8296aa">{"Search reached GitHub’s 1,000-result cap; commit total is a lower bound." if search_truncated else "Attributed commits in public repositories owned by RCZ88; profile repository excluded."}</text>',
        f'<text x="32" y="429" font-family="sans-serif" font-size="10" fill="#8296aa">Code-change totals inspect {diffs["analyzed"]} of up to {DIFF_SAMPLE_LIMIT} latest eligible commit diffs in 30 days{" (sample is capped)" if sample_capped else ""}.</text>',
        '<text x="32" y="447" font-family="sans-serif" font-size="10" fill="#8296aa">Lines changed measure code churn, not net code growth or code quality. Public push events may be incomplete.</text>',
        '</svg>',
    ]
    return "\n".join(p) + "\n"

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("assets/commit-activity.svg"))
    args = parser.parse_args()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    start = now - timedelta(days=364)
    commits, _, search_truncated = search_user_commits(start, now)
    daily: Counter[str] = Counter()
    seen: set[str] = set()
    for item in commits:
        sha = item.get("sha")
        commit_data = item.get("commit") or {}
        timestamp = parsed_datetime(((commit_data.get("committer") or {}).get("date")))
        if sha and sha not in seen and timestamp and start <= timestamp <= now:
            seen.add(sha)
            daily[timestamp.date().isoformat()] += 1
    diffs = recent_diff_stats(commits, now)
    try:
        pushes, push_truncated = public_push_count(now)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as error:
        print(f"Warning: public push event feed unavailable: {error}")
        pushes, push_truncated = None, False
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_svg(daily, len(seen), search_truncated, diffs, pushes, push_truncated, now), encoding="utf-8")
    print(f"Wrote {args.output}: {len(seen)} commits, {diffs['analyzed']} inspected diffs, {diffs['added']} lines added, {diffs['deleted']} deleted, {pushes if pushes is not None else 'N/A'} public push events")

if __name__ == "__main__":
    main()
