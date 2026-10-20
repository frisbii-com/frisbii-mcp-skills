#!/usr/bin/env python3
"""Render the Confluence page body (markdown) for a skill, or for the pack overview.

Usage:
  python3 scripts/confluence_page.py <skill-name>     # one skill page
  python3 scripts/confluence_page.py --overview       # pack overview page
  python3 scripts/confluence_page.py --calendar       # marketing calendar page
  python3 scripts/confluence_page.py --list           # skill, page_id, title

Page copy lives in docs/confluence/pages.json. Facts that change with the skill
(name, product, call budget, files, section headings) are read from SKILL.md so
the page always matches the repo. Pages follow the SKILL space template
(Skill page template, page 11604262921).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META = json.loads((ROOT / "docs/confluence/pages.json").read_text())
SKILLS_DIR = ROOT / "plugins" / META["plugin"] / "skills"
WIKI = META["site"] + "/wiki"


def page_url(page_id):
    return f"{WIKI}/spaces/{META['space_key']}/pages/{page_id}"


def skill_link(name):
    pid = META["skills"].get(name, {}).get("page_id")
    return f"[{name}]({page_url(pid)})" if pid else name


def read_skill(name):
    text = (SKILLS_DIR / name / "SKILL.md").read_text()
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    front = dict(re.findall(r"^(\w+):\s*(.*)$", fm.group(1), re.M)) if fm else {}
    field = lambda label: (re.search(rf"^\*\*{label}:\*\*\s*(.+)$", text, re.M) or [None, ""])[1].strip()
    prose = re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)
    headings = re.findall(r"^## (.+)$", prose, re.M)
    return front, field, headings


def files_table(name, extra):
    rows = []
    for f in sorted((SKILLS_DIR / name).rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(SKILLS_DIR / name).as_posix()
        if rel == "SKILL.md":
            _, _, headings = read_skill(name)
            sections = ", ".join(re.sub(r"^\d+\.\s*", "", h) for h in headings)
            purpose = f"Main instructions: {sections}"
        else:
            purpose = extra.get(rel, "Reference material the agent reads on demand")
        rows.append(f"| `{rel}` | {purpose} |")
    return "\n".join(rows)


def install_block(name):
    repo, plugin, market = META["repository"], META["plugin"], META["marketplace"]
    core = "" if name == "frisbii-core" else " Install `frisbii-core` alongside it; every skill in the pack relies on it."
    return f"""**Claude Code** (installs all skills in the pack)

```
/plugin marketplace add {repo}
/plugin install {plugin}@{market}
```

**Claude.ai and Claude Desktop**

Run `scripts/package.sh` in the repository to build `dist/{name}.zip`, then upload it in Settings → Capabilities → Skills.

**Cursor, Codex and other agents** (via the `skills` CLI, not yet tested with this pack)

```
npx skills add {repo} --skill {name}
```

Prerequisites: the Frisbii Billing & Pay MCP connector, and MCP access on the merchant's Frisbii plan.{core}"""


def render_skill(name):
    m = META["skills"][name]
    front, field, _ = read_skill(name)
    assert front.get("name") == name, f"frontmatter name {front.get('name')!r} != {name!r}"
    product = field("Product") or m.get("product", "")
    budget = field("Call budget")
    week = m.get("week", "")

    out = ["## Summary", "", "|  |  |", "| --- | --- |"]
    out += [
        f"| **Skill name** | `{name}` |",
        f"| **One-line summary** | {m['summary']} |",
        f"| **Toolkit / plugin** | Frisbii MCP Skills Pack → `{META['plugin']}` plugin |",
        f"| **Audience** | {m['audience']} |",
        "| **Supported agents** | Claude.ai, Claude Desktop and Claude Code; other agents that support skills and MCP |",
        f"| **Owner** | {META['owner']} |",
        f"| **Status** | {META['status']} |",
    ]
    if product:
        out.append(f"| **Product** | {product} |")
    if week:
        out.append(f"| **Skill of the Week** | {week} |")
    if budget:
        out.append(f"| **Call budget** | {budget} |")

    out += ["", "## What it does", ""]
    for para in m["what"]:
        out += [para, ""]
    out.append("Read-only: the skill never changes anything in Frisbii and never sends anything to customers.")

    out += ["", "## When the agent uses it", ""]
    out += [f"* {t}" for t in m["triggers"]]
    out.append(f"* Asked for by name: \"use the {name} skill\".")

    out += ["", "## Example use cases", "", "| Ask the agent… | What you get |", "| --- | --- |"]
    out += [f"| {p} | {o} |" for p, o in m["examples"]]

    out += ["", "## What's included", "", "| File | Purpose |", "| --- | --- |", files_table(name, m.get("files", {}))]

    repo = META["repository"]
    out += ["", "## Where it is located", "",
            f"* **Repository:** [{repo}](https://github.com/{repo})",
            f"* **Path:** `plugins/{META['plugin']}/skills/{name}/`",
            f"* **Marketplace:** `{META['marketplace']}`"]

    out += ["", "## How to install", "", install_block(name)]

    out += ["", "## Related skills", ""]
    out += [f"* {r}" for r in m["related"]]

    out += ["", "## Notes and limitations", ""]
    out += [f"* {n}" for n in m["notes"]]
    return "\n".join(out) + "\n"


def render_overview():
    repo, plugin, market = META["repository"], META["plugin"], META["marketplace"]
    out = [
        "The Frisbii MCP Skills Pack gives merchants ready-made skills for answering business questions from their own Frisbii Billing and Frisbii Pay data through the **Frisbii Billing & Pay MCP server**: month-end close, customer briefings, failed payments, payouts, churn and more. It powers the weekly \"Skill of the Week\" series (26 Oct 2026 – 18 Jan 2027).",
        "",
        "All skills are **read-only**: they never change anything in Frisbii or send anything. They can suggest next steps, and draft customer messages for the merchant to send.",
        "",
        "|  |  |", "| --- | --- |",
        f"| **Repository** | [{repo}](https://github.com/{repo}) |",
        f"| **Marketplace** | `{market}` |",
        f"| **Plugin** | `{plugin}` (all {len(META['skills'])} skills) |",
        f"| **Owner** | {META['owner']} |",
        f"| **Status** | {META['status']}. Not yet validated against live data |",
        "",
        "## Skills", "",
        "| Skill | Product | Skill of the Week | Use it for |", "| --- | --- | --- | --- |",
    ]
    for name, m in META["skills"].items():
        _, field, _ = read_skill(name)
        product = (field("Product") or m.get("product", "")).split(".")[0]
        week_text = m.get("week", "Every skill")
        week = week_text.split(",")[0].split(" (")[0] + (" (alt)" if "alternative" in week_text else "")
        out.append(f"| {skill_link(name)} | {product} | {week} | {m['summary']} |")
    out += ["", "Each skill has its own page below.", "",
            "## Install", "",
            "**Claude Code** (installs all skills)", "",
            "```", f"/plugin marketplace add {repo}", f"/plugin install {plugin}@{market}", "```", "",
            "**Claude.ai and Claude Desktop:** run `scripts/package.sh` in the repository and upload each `dist/<skill>.zip` in Settings → Capabilities → Skills. Always install `frisbii-core` alongside the others.", "",
            "Every skill needs the Frisbii Billing & Pay MCP connector and MCP access on the merchant's Frisbii plan.", "",
            "## How the skills work", "",
            "* `frisbii-core` runs first: it checks the connection and MCP access, detects Pay vs Billing, and enforces rate-limit pacing (about 3 calls per minute) and read-only use.",
            "* Skills prefer the server's snapshot `count_*` and revenue tools, which return exact totals in one call, over paging lists.",
            "* Snapshot figures always show their as-of time; money is never added across currencies.", "",
            "## Related", "",
            f"* [{META['calendar']['title']}]({page_url(META['calendar']['page_id'])}): which skill is featured each week and what it drives adoption of.",
            f"* [Frisbii Agent Toolkit]({page_url('11604099086')}): skills for developers building Frisbii integrations.",
            ]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--overview":
        sys.stdout.write(render_overview())
    elif arg == "--calendar":
        sys.stdout.write((ROOT / META["calendar"]["source"]).read_text())
    elif arg == "--list":
        print(f"overview\t{META['overview']['page_id']}\t{META['overview']['title']}")
        print(f"calendar\t{META['calendar']['page_id']}\t{META['calendar']['title']}")
        for n, m in META["skills"].items():
            print(f"{n}\t{m['page_id']}\t{n}")
    elif arg in META["skills"]:
        sys.stdout.write(render_skill(arg))
    else:
        sys.exit(f"usage: {sys.argv[0]} <skill-name> | --overview | --list")
