#!/usr/bin/env python3
"""Mine a GitHub repository's review history: who reviews (weighted toward recency), who merges, what outside authors get, and every word the top reviewers wrote.

Usage:
    mine_reviews.py OWNER/REPO [--prs 300] [--comment-pages 5] [--half-life 180] [--top 6] [--since YYYY-MM-DD] [--out DIR] [--no-profiles]

Needs `gh` logged in (read-only calls only) and Python 3.9+. Nothing is posted, edited, cloned or forked.

Writes under --out (default ./lens-mining/OWNER-REPO):
    summary.md                recency-weighted reviewer ranking, arc by year, who merges, outside-author outcomes, bots, suggested lens shape
    raw/prs.jsonl             one PR per line: metadata, review submissions, issue comments
    raw/reviews.tsv           pr, login, state, date, body (one line)
    raw/inline-comments.jsonl the newest inline review comments on the repo (path, line, body, pr, author)
    raw/<login>.md            everything each top reviewer wrote, grouped by PR, newest first (the qualitative corpus)
    raw/declined.md           closed-unmerged PRs by outside authors with their last comments (what gets a no)
    raw/backtest.md           answer key for the held-out PRs: the reviewers' real comments, kept out of raw/<login>.md; open it only after running the lens on each held-out diff
"""
import argparse
import collections
import datetime as dt
import json
import os
import re
import statistics
import subprocess
import sys

BOT_LOGINS = {
    "copilot-pull-request-reviewer", "coderabbitai", "chatgpt-codex-connector", "github-actions",
    "dependabot", "renovate", "codecov", "codecov-commenter", "sonarcloud", "netlify", "vercel",
    "cursor", "greptile-apps", "ellipsis-dev", "claude", "mergify", "stale", "allcontributors",
}
INSIDE = {"MEMBER", "OWNER", "COLLABORATOR"}
PR_PAGE = 50
REVIEWS_FIRST = 40
COMMENTS_FIRST = 30

PR_FIELDS = """
  number title state isDraft createdAt mergedAt closedAt additions deletions changedFiles authorAssociation
  author { login __typename } mergedBy { login }
"""

LIST_QUERY = """
query($owner:String!, $name:String!, $first:Int!, $after:String) {
  repository(owner:$owner, name:$name) {
    pullRequests(first:$first, after:$after, states:[MERGED, CLOSED, OPEN], orderBy:{field:CREATED_AT, direction:DESC}) {
      totalCount pageInfo { hasNextPage endCursor }
      nodes {
        %s
        reviews(first:%d) { totalCount nodes { author { login __typename } state submittedAt body } }
        comments(first:%d) { totalCount nodes { author { login __typename } createdAt body } }
      }
    }
  }
}
""" % (PR_FIELDS, REVIEWS_FIRST, COMMENTS_FIRST)


def die(msg, code=2):
    print(f"mine_reviews: {msg}", file=sys.stderr)
    sys.exit(code)


def gh(args, allow_fail=False):
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        if allow_fail:
            return None
        die(f"gh {' '.join(args[:3])}... failed:\n{proc.stderr.strip()}")
    return proc.stdout


def gh_json(args, allow_fail=False):
    out = gh(args, allow_fail=allow_fail)
    if out is None:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        die(f"gh returned non-JSON for {' '.join(args[:4])}: {out[:200]}")


def graphql(query, **variables):
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is None:
            continue
        flag = "-F" if isinstance(value, int) else "-f"
        args += [flag, f"{key}={value}"]
    data = gh_json(args)
    if "errors" in data and not data.get("data"):
        die("GraphQL errors: " + json.dumps(data["errors"])[:500])
    return data["data"]


def parse_date(value):
    if not value:
        return None
    return dt.datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)


def login_of(actor):
    if not actor:
        return None
    return actor.get("login")


def is_bot(actor_or_login, typename=None):
    if isinstance(actor_or_login, dict):
        typename = actor_or_login.get("__typename") or typename
        login = actor_or_login.get("login") or ""
    else:
        login = actor_or_login or ""
    if typename == "Bot":
        return True
    base = login.lower().removesuffix("[bot]")
    return login.lower().endswith("[bot]") or base in BOT_LOGINS


def one_line(text, limit=None):
    text = re.sub(r"\s+", " ", (text or "")).strip()
    return text[:limit] if limit else text


def size_bucket(pr):
    lines = (pr.get("additions") or 0) + (pr.get("deletions") or 0)
    if lines <= 20:
        return "≤20 lines"
    if lines <= 100:
        return "21–100 lines"
    return ">100 lines"


def fetch_prs(owner, name, limit, since, include_bot_prs):
    prs, cursor, skipped_bots = [], None, 0
    while len(prs) < limit:
        page = graphql(LIST_QUERY, owner=owner, name=name, first=PR_PAGE, after=cursor)
        conn = page["repository"]["pullRequests"]
        for node in conn["nodes"]:
            created = parse_date(node["createdAt"])
            if since and created < since:
                return prs, conn["totalCount"], skipped_bots
            if not include_bot_prs and is_bot(node.get("author")):
                skipped_bots += 1
                continue
            if len(prs) < limit:
                prs.append(node)
        if not conn["pageInfo"]["hasNextPage"]:
            return prs, conn["totalCount"], skipped_bots
        cursor = conn["pageInfo"]["endCursor"]
        if prs:
            print(f"  fetched {len(prs)} PRs (newest {prs[0]['createdAt'][:10]}, oldest {prs[-1]['createdAt'][:10]}; {skipped_bots} bot PRs skipped)", file=sys.stderr)
    return prs, conn["totalCount"], skipped_bots


def complete_truncated(owner, name, prs):
    """GraphQL pages cap nested reviews/comments; refetch the few PRs that overflowed through REST."""
    for pr in prs:
        if pr["reviews"]["totalCount"] > REVIEWS_FIRST:
            rows = gh_json(["api", f"repos/{owner}/{name}/pulls/{pr['number']}/reviews", "--paginate"], allow_fail=True) or []
            pr["reviews"]["nodes"] = [
                {"author": {"login": (r.get("user") or {}).get("login"), "__typename": (r.get("user") or {}).get("type")},
                 "state": r.get("state"), "submittedAt": r.get("submitted_at"), "body": r.get("body") or ""}
                for r in rows
            ]
        if pr["comments"]["totalCount"] > COMMENTS_FIRST:
            rows = gh_json(["api", f"repos/{owner}/{name}/issues/{pr['number']}/comments", "--paginate"], allow_fail=True) or []
            pr["comments"]["nodes"] = [
                {"author": {"login": (c.get("user") or {}).get("login"), "__typename": (c.get("user") or {}).get("type")},
                 "createdAt": c.get("created_at"), "body": c.get("body") or ""}
                for c in rows
            ]


def fetch_inline_comments(owner, name, pages):
    comments = []
    for page in range(1, pages + 1):
        rows = gh_json(["api", f"repos/{owner}/{name}/pulls/comments?sort=created&direction=desc&per_page=100&page={page}"])
        if not rows:
            break
        for c in rows:
            user = c.get("user") or {}
            comments.append({
                "id": c["id"],
                "reply_to": c.get("in_reply_to_id"),
                "login": user.get("login"),
                "bot": is_bot(user.get("login"), user.get("type")),
                "pr": int(c["pull_request_url"].rsplit("/", 1)[-1]),
                "path": c.get("path"),
                "line": c.get("line") or c.get("original_line"),
                "created_at": c.get("created_at"),
                "url": c.get("html_url"),
                "body": c.get("body") or "",
            })
        print(f"  fetched {len(comments)} inline comments (oldest {comments[-1]['created_at'][:10]})", file=sys.stderr)
        if len(rows) < 100:
            break
    return comments


def fetch_pr_meta(owner, name, numbers):
    """Metadata for PRs referenced by inline comments but outside the PR window, 50 per GraphQL call."""
    meta = {}
    numbers = sorted(numbers)
    for start in range(0, len(numbers), 50):
        chunk = numbers[start:start + 50]
        body = " ".join(f"p{n}: pullRequest(number:{n}) {{ {PR_FIELDS} }}" for n in chunk)
        query = "query($owner:String!, $name:String!) { repository(owner:$owner, name:$name) { %s } }" % body
        data = graphql(query, owner=owner, name=name)
        for key, node in data["repository"].items():
            if node:
                node["reviews"] = {"totalCount": 0, "nodes": []}
                node["comments"] = {"totalCount": 0, "nodes": []}
                node["outside_window"] = True
                meta[node["number"]] = node
    return meta


def fetch_profiles(logins):
    profiles = {}
    for login in logins:
        data = gh_json(["api", f"users/{login}"], allow_fail=True)
        if data:
            profiles[login] = {"name": data.get("name"), "company": data.get("company"), "bio": one_line(data.get("bio"), 100)}
    return profiles


def md_table(headers, rows):
    out = ["| " + " | ".join(str(h) for h in headers) + " |", "|" + "|".join(" --- " for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def median_duration(hours):
    """Median of a list of hours, printed as hours under three days and days above."""
    if not hours:
        return "–"
    med = statistics.median(hours)
    return f"{med:.1f} h" if med < 72 else f"{med / 24:.1f} d"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("repo", help="OWNER/REPO")
    ap.add_argument("--prs", type=int, default=1000, help="cap on PRs read, newest first (merged, closed and open)")
    ap.add_argument("--years", type=float, default=3, help="read PRs created within this many years (ignored when --since is given)")
    ap.add_argument("--me", help="your GitHub login: left out of the reviewer ranking, and your own PRs get their own section")
    ap.add_argument("--comment-pages", type=int, default=5, help="pages of 100 newest inline review comments")
    ap.add_argument("--half-life", type=float, default=180, help="days until an event counts half; recency bias")
    ap.add_argument("--top", type=int, default=6, help="how many reviewers get a corpus file and a profile lookup")
    ap.add_argument("--since", help="stop reading PRs created before this date (YYYY-MM-DD)")
    ap.add_argument("--out", help="output directory (default ./lens-mining/OWNER-REPO)")
    ap.add_argument("--holdout", type=int, default=4, help="merged outside-author PRs to keep out of the corpus as a back-test set (0 to disable)")
    ap.add_argument("--no-profiles", action="store_true", help="skip gh api users/<login> lookups")
    ap.add_argument("--include-bot-prs", action="store_true", help="count dependabot/renovate PRs toward --prs (off by default: human review habits are the point)")
    args = ap.parse_args()

    if "/" not in args.repo:
        die("repo must be OWNER/REPO")
    owner, name = args.repo.split("/", 1)
    now = dt.datetime.now(dt.timezone.utc)
    if args.since:
        since = dt.datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
    else:
        since = now - dt.timedelta(days=365.25 * args.years)
    out_dir = args.out or os.path.join("lens-mining", f"{owner}-{name}")
    raw_dir = os.path.join(out_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)

    def weight(when):
        age_days = max((now - when).total_seconds() / 86400, 0)
        return 0.5 ** (age_days / args.half_life)

    print(f"Reading {args.repo}: PRs created since {since.date()} (cap {args.prs}), {args.comment_pages} pages of inline comments", file=sys.stderr)
    prs, total_prs, skipped_bots = fetch_prs(owner, name, args.prs, since, args.include_bot_prs)
    if not prs:
        die("no pull requests found")
    complete_truncated(owner, name, prs)
    inline = fetch_inline_comments(owner, name, args.comment_pages)

    by_number = {pr["number"]: pr for pr in prs}
    missing = {c["pr"] for c in inline} - set(by_number)
    if missing:
        print(f"  fetching metadata for {len(missing)} PRs referenced only by inline comments", file=sys.stderr)
        by_number.update(fetch_pr_meta(owner, name, missing))

    # Orgs that keep membership private report staff as CONTRIBUTOR; anyone who has pressed merge here is inside.
    insiders = {login_of(pr.get("mergedBy")) for pr in prs if pr.get("mergedBy")} - {None}
    insiders |= {login_of(pr.get("author")) for pr in prs if pr.get("authorAssociation") in INSIDE} - {None}

    def is_inside(pr):
        return login_of(pr.get("author")) in insiders

    # ---- reviewer events (reviews + inline comments on PRs the reviewer did not author) ----
    score = collections.Counter()
    review_counts = collections.defaultdict(collections.Counter)
    inline_counts = collections.Counter()
    year_counts = collections.defaultdict(collections.Counter)
    first_seen, last_seen = {}, {}
    paths = collections.defaultdict(collections.Counter)
    bot_activity = collections.Counter()
    prs_reviewed = collections.defaultdict(set)

    me = args.me

    def note(login, when):
        first_seen[login] = min(first_seen.get(login, when), when)
        last_seen[login] = max(last_seen.get(login, when), when)
        year_counts[login][when.year] += 1

    for pr in prs:
        author = login_of(pr.get("author"))
        for review in pr["reviews"]["nodes"]:
            login = login_of(review.get("author"))
            if not login or login == author or login == me or review.get("state") == "PENDING":
                continue
            if is_bot(review.get("author")):
                bot_activity[login] += 1
                continue
            when = parse_date(review.get("submittedAt"))
            if not when:
                continue
            score[login] += weight(when)
            review_counts[login][review["state"]] += 1
            prs_reviewed[login].add(pr["number"])
            note(login, when)

    for c in inline:
        pr = by_number.get(c["pr"])
        author = login_of(pr.get("author")) if pr else None
        login = c["login"]
        if not login or login == author or login == me:
            continue
        if c["bot"]:
            bot_activity[login] += 1
            continue
        when = parse_date(c["created_at"])
        score[login] += weight(when)
        inline_counts[login] += 1
        prs_reviewed[login].add(c["pr"])
        note(login, when)
        if c["path"]:
            parts = c["path"].split("/")
            paths[login]["/".join(parts[:2]) if len(parts) > 2 else parts[0]] += 1

    ranked = [login for login, _ in score.most_common()]
    top = ranked[: args.top]
    total_score = sum(score.values()) or 1.0
    profiles = {} if args.no_profiles else fetch_profiles(top)

    # ---- hold out a back-test set: merged PRs by outsiders that drew real review from the top reviewers ----
    inline_by_pr = collections.defaultdict(list)
    for c in inline:
        if c["login"] in top and not c["bot"]:
            inline_by_pr[c["pr"]].append(c)
    holdout = []
    if args.holdout:
        candidates = []
        for pr in prs:
            if pr["state"] != "MERGED" or is_bot(pr.get("author")) or login_of(pr.get("author")) in top or login_of(pr.get("author")) == me:
                continue
            weight_outside = 0 if is_inside(pr) else 1
            n_comments = len(inline_by_pr.get(pr["number"], [])) + sum(
                1 for r in pr["reviews"]["nodes"] if login_of(r.get("author")) in top and (r.get("body") or "").strip())
            if n_comments >= 2:
                candidates.append((weight_outside, pr["mergedAt"], pr["number"]))
        candidates.sort(reverse=True)
        holdout = [n for _, _, n in candidates[: args.holdout]]
    held = set(holdout)

    # ---- mergers, authors, outcomes ----
    merged_by_year = collections.defaultdict(collections.Counter)
    authors_by_year = collections.defaultdict(collections.Counter)
    self_merges = collections.Counter()
    for pr in prs:
        author = login_of(pr.get("author"))
        if is_bot(pr.get("author")):
            continue
        year = pr["createdAt"][:4]
        authors_by_year[year][author or "?"] += 1
        if pr["state"] == "MERGED":
            merger = login_of(pr.get("mergedBy")) or "?"
            merged_by_year[pr["mergedAt"][:4]][merger] += 1
            if merger == author:
                self_merges[pr["mergedAt"][:4]] += 1

    outcome = collections.defaultdict(lambda: {"merged": [], "closed": [], "first_review_h": []})
    for pr in prs:
        if pr["state"] == "OPEN" or is_bot(pr.get("author")):
            continue
        group = "inside" if is_inside(pr) else "outside"
        bucket = size_bucket(pr)
        created = parse_date(pr["createdAt"])
        author = login_of(pr.get("author"))
        reviews = [parse_date(r.get("submittedAt")) for r in pr["reviews"]["nodes"]
                   if login_of(r.get("author")) not in (None, author) and not is_bot(r.get("author")) and r.get("submittedAt")]
        if reviews:
            outcome[(group, bucket)]["first_review_h"].append((min(reviews) - created).total_seconds() / 3600)
        if pr["state"] == "MERGED":
            outcome[(group, bucket)]["merged"].append((parse_date(pr["mergedAt"]) - created).total_seconds() / 3600)
        else:
            outcome[(group, bucket)]["closed"].append(pr["number"])

    # ---- raw dumps ----
    with open(os.path.join(raw_dir, "prs.jsonl"), "w") as f:
        for pr in prs:
            f.write(json.dumps(pr, ensure_ascii=False) + "\n")
    with open(os.path.join(raw_dir, "reviews.tsv"), "w") as f:
        for pr in prs:
            for r in pr["reviews"]["nodes"]:
                f.write("\t".join([str(pr["number"]), login_of(r.get("author")) or "?", r.get("state") or "?",
                                   (r.get("submittedAt") or "")[:10], one_line(r.get("body"))]) + "\n")
    with open(os.path.join(raw_dir, "inline-comments.jsonl"), "w") as f:
        for c in inline:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    def pr_header(pr):
        state = pr["state"].lower()
        when = (pr.get("mergedAt") or pr.get("closedAt") or pr.get("createdAt") or "")[:10]
        return f"### PR #{pr['number']} — {pr.get('title','')} [{state} {when}, by {login_of(pr.get('author')) or '?'}, {pr.get('authorAssociation','?').lower()}, +{pr.get('additions',0)}/−{pr.get('deletions',0)}]"

    for login in top:
        sections = collections.defaultdict(list)
        for pr in prs:
            if login_of(pr.get("author")) == login or pr["number"] in held:
                continue
            for r in pr["reviews"]["nodes"]:
                if login_of(r.get("author")) == login and (r.get("body") or "").strip():
                    sections[pr["number"]].append((parse_date(r["submittedAt"]), f"- review **{r['state']}** ({r['submittedAt'][:10]}): {r['body'].strip()}"))
            for c in pr["comments"]["nodes"]:
                if login_of(c.get("author")) == login and (c.get("body") or "").strip():
                    sections[pr["number"]].append((parse_date(c["createdAt"]), f"- comment ({c['createdAt'][:10]}): {c['body'].strip()}"))
        for c in inline:
            pr = by_number.get(c["pr"])
            if c["login"] != login or (pr and login_of(pr.get("author")) == login) or c["pr"] in held:
                continue
            tag = " (reply)" if c["reply_to"] else ""
            sections[c["pr"]].append((parse_date(c["created_at"]), f"- `{c['path']}:{c['line']}`{tag} ({c['created_at'][:10]}): {c['body'].strip()}"))
        ordered = sorted(sections.items(), key=lambda kv: max(t for t, _ in kv[1]), reverse=True)
        with open(os.path.join(raw_dir, f"{login}.md"), "w") as f:
            f.write(f"# {login} — every review body, inline comment and PR comment on PRs they did not author\n\n")
            f.write(f"Gathered {now.date()} from {args.repo}: {len(prs)} newest PRs plus {len(inline)} newest inline comments. Quotes are verbatim; cite PR number and date when you turn one into a rule."
                    + (f" Held out for the back-test (not in this file): {', '.join('#' + str(n) for n in holdout)}." if holdout else "") + "\n\n")
            for number, items in ordered:
                pr = by_number.get(number) or {"number": number, "title": "?", "state": "?", "author": None}
                f.write(pr_header(pr) + "\n\n")
                for _, line in sorted(items, key=lambda t: t[0]):
                    f.write(line + "\n")
                f.write("\n")

    with open(os.path.join(raw_dir, "declined.md"), "w") as f:
        f.write(f"# Closed without merge — outside authors ({args.repo}, {len(prs)} newest PRs)\n\nRead the last comments on each: the reason it closed is the rule for what gets a no.\n\n")
        for pr in prs:
            if pr["state"] != "CLOSED" or is_inside(pr) or is_bot(pr.get("author")):
                continue
            f.write(pr_header(pr) + "\n\n")
            tail = [c for c in pr["comments"]["nodes"] if (c.get("body") or "").strip()][-3:]
            for c in tail:
                f.write(f"- {login_of(c.get('author')) or '?'} ({(c.get('createdAt') or '')[:10]}): {one_line(c['body'], 600)}\n")
            for r in pr["reviews"]["nodes"]:
                if r.get("state") == "CHANGES_REQUESTED" and (r.get("body") or "").strip():
                    f.write(f"- {login_of(r.get('author')) or '?'} CHANGES_REQUESTED ({r['submittedAt'][:10]}): {one_line(r['body'], 600)}\n")
            f.write("\n")

    if holdout:
        with open(os.path.join(raw_dir, "backtest.md"), "w") as f:
            f.write(f"# Back-test answer key — {args.repo}\n\n")
            f.write("These merged PRs were kept out of the reviewer corpus. For each one, run the lens on the diff first (`gh pr diff <N> -R " + args.repo + "`), write down its rulings, and only then read the reviewer's real comments below. Every comment the lens missed becomes a rule; every ruling the reviewer never made is your taste, not theirs, and gets cut.\n\n")
            for number in holdout:
                pr = by_number[number]
                f.write(pr_header(pr) + "\n\n")
                f.write(f"Diff: `gh pr diff {number} -R {args.repo}`\n\n")
                items = []
                for r in pr["reviews"]["nodes"]:
                    if login_of(r.get("author")) in top and (r.get("body") or "").strip():
                        items.append((parse_date(r["submittedAt"]), f"- {login_of(r.get('author'))} review **{r['state']}** ({r['submittedAt'][:10]}): {r['body'].strip()}"))
                for c in inline_by_pr.get(number, []):
                    tag = " (reply)" if c["reply_to"] else ""
                    items.append((parse_date(c["created_at"]), f"- {c['login']} `{c['path']}:{c['line']}`{tag} ({c['created_at'][:10]}): {c['body'].strip()}"))
                for _, line in sorted(items, key=lambda t: t[0]):
                    f.write(line + "\n")
                f.write("\n")

    # ---- summary ----
    lines = [f"# Review history of {args.repo}", ""]
    lines.append(f"Mined {now.date()} with `mine_reviews.py`. Window: the {len(prs)} newest human-authored PRs of {total_prs} ({skipped_bots} bot PRs skipped; created {prs[-1]['createdAt'][:10]} → {prs[0]['createdAt'][:10]}; "
                 f"{sum(1 for p in prs if p['state']=='MERGED')} merged, {sum(1 for p in prs if p['state']=='CLOSED')} closed unmerged, {sum(1 for p in prs if p['state']=='OPEN')} open) "
                 f"plus the {len(inline)} newest inline review comments ({inline[-1]['created_at'][:10] if inline else '–'} → {inline[0]['created_at'][:10] if inline else '–'}). "
                 f"Weights halve every {args.half_life:g} days, so the ranking is what the repo does now, not what it did once.")
    lines.append("")
    lines.append("## Who reviews (recency-weighted)")
    lines.append("")
    rows = []
    for login in ranked[: max(args.top, 10)]:
        rc = review_counts[login]
        prof = profiles.get(login, {})
        who = " / ".join(x for x in [prof.get("name"), prof.get("company")] if x)
        rows.append([login, f"{score[login]:.1f}", f"{100*score[login]/total_score:.0f}%",
                     f"{rc['APPROVED']}/{rc['COMMENTED']}/{rc['CHANGES_REQUESTED']}", inline_counts[login], len(prs_reviewed[login]),
                     first_seen[login].date(), last_seen[login].date(), who or "–"])
    lines.append(md_table(["reviewer", "weighted score", "share", "reviews approve/comment/changes", "inline comments", "PRs touched", "first", "last", "who"], rows))
    lines.append("")
    lines.append("## Arc by year (review submissions + inline comments)")
    lines.append("")
    years = sorted({y for login in ranked[:args.top] for y in year_counts[login]})
    lines.append(md_table(["reviewer", *years], [[login, *[year_counts[login][y] for y in years]] for login in ranked[:args.top]]))
    lines.append("")
    lines.append("## Who presses merge")
    lines.append("")
    rows = []
    for year in sorted(merged_by_year, reverse=True):
        counter = merged_by_year[year]
        rows.append([year, sum(counter.values()), ", ".join(f"{m} {n}" for m, n in counter.most_common(5)), self_merges[year]])
    lines.append(md_table(["year", "merged PRs", "top mergers", "self-merges"], rows))
    lines.append("")
    lines.append("## Who authors")
    lines.append("")
    rows = [[year, sum(c.values()), ", ".join(f"{a} {n}" for a, n in c.most_common(5))] for year, c in sorted(authors_by_year.items(), reverse=True)]
    lines.append(md_table(["year", "PRs opened", "top authors"], rows))
    lines.append("")
    lines.append("## What outside authors get")
    lines.append("")
    rows = []
    for group in ("outside", "inside"):
        for bucket in ("≤20 lines", "21–100 lines", ">100 lines"):
            o = outcome.get((group, bucket))
            if not o:
                continue
            rows.append([group, bucket, len(o["merged"]), len(o["closed"]), median_duration(o["merged"]), median_duration(o["first_review_h"])])
    lines.append(md_table(["author", "size", "merged", "closed unmerged", "median time to merge", "median time to first review"], rows))
    lines.append("")
    lines.append(f"Inside means the author is a MEMBER, OWNER or COLLABORATOR, or has pressed merge on a PR in this window ({len(insiders)} logins; orgs with private membership report staff as plain contributors). Everyone else is outside. Closed-unmerged outside PRs are listed in `raw/declined.md`.")
    lines.append("")
    if me:
        mine = [pr for pr in prs if login_of(pr.get("author")) == me]
        if mine:
            merged = [pr for pr in mine if pr["state"] == "MERGED"]
            closed = [pr for pr in mine if pr["state"] == "CLOSED"]
            first_review = []
            per_reviewer = collections.Counter()
            changes_requested = 0
            for pr in mine:
                created = parse_date(pr["createdAt"])
                times = []
                for r in pr["reviews"]["nodes"]:
                    login = login_of(r.get("author"))
                    if login in (None, me) or is_bot(r.get("author")) or not r.get("submittedAt"):
                        continue
                    times.append(parse_date(r["submittedAt"]))
                    per_reviewer[login] += 1
                    changes_requested += r.get("state") == "CHANGES_REQUESTED"
                if times:
                    first_review.append((min(times) - created).total_seconds() / 3600)
            mine_inline = collections.Counter(c["login"] for c in inline if c["pr"] in {pr["number"] for pr in mine} and c["login"] != me and not c["bot"])
            lines.append(f"## Your PRs here ({me})")
            lines.append("")
            lines.append(f"{len(mine)} opened in the window: {len(merged)} merged, {len(closed)} closed unmerged, {len(mine) - len(merged) - len(closed)} open. "
                         f"Median time to merge {median_duration([(parse_date(p['mergedAt']) - parse_date(p['createdAt'])).total_seconds() / 3600 for p in merged])}, "
                         f"median time to first review {median_duration(first_review)}. {changes_requested} CHANGES_REQUESTED reviews.")
            lines.append("")
            lines.append("Reviews on your PRs: " + (", ".join(f"{l} {n}" for l, n in per_reviewer.most_common(6)) or "none") +
                         ". Inline comments on your PRs (newest window): " + (", ".join(f"{l} {n}" for l, n in mine_inline.most_common(6)) or "none") + ".")
            lines.append("")
    if bot_activity:
        lines.append("## Bots on PRs")
        lines.append("")
        lines.append(", ".join(f"{b} ({n})" for b, n in bot_activity.most_common()))
        lines.append("")
    lines.append("## Where each top reviewer comments (path prefixes)")
    lines.append("")
    for login in top:
        if paths[login]:
            lines.append(f"- **{login}**: " + ", ".join(f"{p} {n}" for p, n in paths[login].most_common(8)))
    lines.append("")
    lines.append("## Suggested lens shape")
    lines.append("")
    if ranked:
        top_share = score[ranked[0]] / total_score
        two_share = (score[ranked[0]] + (score[ranked[1]] if len(ranked) > 1 else 0)) / total_score
        if top_share >= 0.5:
            shape = f"One gatekeeper: **{ranked[0]}** carries {100*top_share:.0f}% of recent review weight. Name the lens for the person and write it as their review."
        elif two_share >= 0.7:
            shape = f"Two reviewers: **{ranked[0]}** and **{ranked[1]}** carry {100*two_share:.0f}% between them. Build one lens per person, decide which one owns the PR body, and state the order they run in."
        else:
            shape = f"A team: the top reviewer holds only {100*top_share:.0f}%. Name the lens for the repo, give each of the top {min(len(ranked), args.top)} reviewers a block, and add a \"who will review\" routing section by path."
        lines.append(shape)
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append(f"- `raw/<login>.md` for: {', '.join(top)}")
    lines.append("- `raw/declined.md`, `raw/reviews.tsv`, `raw/inline-comments.jsonl`, `raw/prs.jsonl`")
    if holdout:
        lines.append(f"- `raw/backtest.md`: answer key for the held-out PRs {', '.join('#' + str(n) for n in holdout)}. Run the lens on each diff before opening it.")
    with open(os.path.join(out_dir, "summary.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nWrote {out_dir}/summary.md and {raw_dir}/", file=sys.stderr)


if __name__ == "__main__":
    main()
