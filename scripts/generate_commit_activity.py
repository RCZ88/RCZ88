#!/usr/bin/env python3
"""Generate a public commit calendar and recent public push count for RCZ88."""
import argparse, json, time
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

OWNER = "RCZ88"
PROFILE_REPO = "RCZ88/RCZ88"
API = "https://api.github.com"
HEADERS = {"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"RCZ88-profile-activity/1.0"}

def get(url):
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=25) as r:
                return json.load(r)
        except HTTPError as e:
            if e.code in (403,429) and attempt < 3:
                time.sleep(min(2 ** (attempt + 1), 30)); continue
            raise
        except (URLError, TimeoutError):
            if attempt == 3: raise
            time.sleep(2 ** attempt)

def iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def collect(now):
    start = now - timedelta(days=364)
    repos, page = [], 1
    while True:
        batch = get(f"{API}/users/{OWNER}/repos?"+urlencode({"type":"owner","per_page":100,"page":page}))
        repos.extend(x for x in batch if not x.get("private") and x.get("full_name","").lower()!=PROFILE_REPO.lower())
        if len(batch)<100: break
        page += 1
    counts, seen = Counter(), set()
    for repo in repos:
        page=1
        while True:
            params=urlencode({"author":OWNER,"since":iso(start),"until":iso(now),"per_page":100,"page":page})
            batch=get(f"{API}/repos/{repo['full_name']}/commits?{params}")
            for item in batch:
                sha=item.get("sha")
                raw=(item.get("commit") or {}).get("committer") or {}
                if not sha or sha in seen or not raw.get("date"): continue
                dt=datetime.fromisoformat(raw["date"].replace("Z","+00:00")).astimezone(timezone.utc)
                if start <= dt <= now:
                    seen.add(sha); counts[dt.date().isoformat()] += 1
            if len(batch)<100: break
            page += 1
    events=[]
    for page in range(1,4):
        batch=get(f"{API}/users/{OWNER}/events/public?per_page=100&page={page}")
        events.extend(batch)
        if len(batch)<100: break
    cutoff=now-timedelta(days=30)
    pushes=sum(1 for e in events if e.get("type")=="PushEvent" and cutoff <= datetime.fromisoformat(e["created_at"].replace("Z","+00:00")).astimezone(timezone.utc) <= now)
    truncated=len(events)>=300 and bool(events) and datetime.fromisoformat(events[-1]["created_at"].replace("Z","+00:00")).astimezone(timezone.utc)>=cutoff
    return counts, pushes, truncated

def render(counts,pushes,truncated,now):
    start=(now-timedelta(days=364)).date(); end=now.date()
    first=start-timedelta(days=start.weekday()); last=end+timedelta(days=6-end.weekday())
    weeks=(last-first).days//7+1; x0,y0,cell,gap=42,88,10,4; step=cell+gap
    gridw=weeks*step-gap; total=sum(counts.values())
    palette=["#1e293b","#174c4a","#167a6f","#21a58e","#70e1bd"]
    def level(n): return 0 if n==0 else 1 if n==1 else 2 if n<=3 else 3 if n<=7 else 4
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="250" viewBox="0 0 1040 250" role="img" aria-labelledby="t d">',f'<title id="t">RCZ88 public commit activity</title><desc id="d">{total} commits over 365 days; {pushes} observed public push events over 30 days.</desc>','<rect width="1040" height="250" rx="18" fill="#0b1220"/>','<path d="M20 72H1020" stroke="#263547"/>','<g font-family="ui-monospace,Menlo,monospace"><text x="30" y="32" font-size="10" letter-spacing="1.8" fill="#7dd3fc">ACTIVITY / PUBLIC REPOSITORIES</text><text x="30" y="57" font-size="21" fill="#f8fafc">Commits, last 365 days</text>',f'<text x="1010" y="46" text-anchor="end" font-size="28" fill="#f8fafc">{total:,}</text>','<text x="1010" y="61" text-anchor="end" font-size="10" fill="#8294a8">COMMITS</text></g>']
    for off in range((end-first).days+1):
        d=first+timedelta(days=off)
        if d.day==1 and d>=start:
            p.append(f'<text x="{x0+(off//7)*step}" y="82" font-family="monospace" font-size="10" fill="#91a4b8">{d.strftime("%b")}</text>')
    for label,row in (("Mon",0),("Wed",2),("Fri",4)):
        p.append(f'<text x="30" y="{y0+row*step+cell-1}" text-anchor="end" font-family="monospace" font-size="9" fill="#71869b">{label}</text>')
    for off in range((last-first).days+1):
        d=first+timedelta(days=off)
        if not start<=d<=end: continue
        n=counts.get(d.isoformat(),0); title=escape(f"{d.isoformat()}: {n} commits")
        p.append(f'<rect x="{x0+(off//7)*step}" y="{y0+d.weekday()*step}" width="{cell}" height="{cell}" rx="2" fill="{palette[level(n)]}" stroke="#2a394c" stroke-width=".35"><title>{title}</title></rect>')
    ly=y0+7*step+9; lx=x0+36
    p.append(f'<text x="{x0}" y="{ly}" font-family="monospace" font-size="10" fill="#8294a8">LESS</text>')
    for i,c in enumerate(palette): p.append(f'<rect x="{lx+i*16}" y="{ly-9}" width="10" height="10" rx="2" fill="{c}"/>')
    p.append(f'<text x="{lx+82}" y="{ly}" font-family="monospace" font-size="10" fill="#8294a8">MORE</text>')
    cardx=x0+gridw+26; cardw=1040-cardx-28; label=(">=" if truncated else "")+str(pushes)
    p += [f'<rect x="{cardx}" y="{y0+4}" width="{cardw}" height="86" rx="10" fill="#111f30" stroke="#2a394c"/>',f'<text x="{cardx+14}" y="{y0+24}" font-family="monospace" font-size="9" fill="#7dd3fc">PUBLIC PUSH EVENTS</text>',f'<text x="{cardx+14}" y="{y0+60}" font-family="sans-serif" font-size="29" fill="#f8fafc">{label}</text>',f'<text x="{cardx+14}" y="{y0+77}" font-family="monospace" font-size="10" fill="#8294a8">observed / last 30 days</text>','<text x="30" y="230" font-family="sans-serif" font-size="10" fill="#71869b">By committer date · owned public repositories · profile repo excluded</text>','</svg>']
    return '\n'.join(p)+'\n'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,default=Path("dist/commit-activity.svg")); args=ap.parse_args()
    now=datetime.now(timezone.utc).replace(microsecond=0); counts,pushes,truncated=collect(now)
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(render(counts,pushes,truncated,now),encoding="utf-8")
    print(f"Wrote {args.output}: {sum(counts.values())} public commits; {pushes} observed public pushes"+(" (event feed may be truncated)" if truncated else ""))

if __name__=="__main__": main()
