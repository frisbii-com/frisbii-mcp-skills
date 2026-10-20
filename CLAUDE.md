# CLAUDE.md

Frisbii MCP Skills Pack: read-only skills for Frisbii Billing and Frisbii Pay merchants, built on the Frisbii Billing & Pay MCP server. Owner: Martyn Arbon. See `README.md` for the layout and the skill list.

## Working on skills

- Skills live in `plugins/frisbii-skills/skills/<skill-name>/SKILL.md`. The frontmatter `name` must equal the folder name.
- Base every tool call on the **live** Frisbii Billing & Pay MCP tool schemas (load them with ToolSearch, `mcp__Frisbii_Billing_Pay_MCP__*`), not on older docs. If a tool description disagrees with a skill, fix the skill.
- Every job skill starts with "Apply **frisbii-core** first" plus the minimum-rules block, states its **Product**, **Featured** week and **Call budget** lines, and stays read-only.
- Kvitora is out of scope (decision of 19 Oct 2026): skills end with the recovery next steps in `frisbii-core/references/recovery-next-steps.md`, never a Kvitora handoff.
- After changing skills, run `scripts/package.sh` and `claude plugin validate .`.

## Keep Confluence in sync (required)

Every skill has a page in the Confluence space **SKILL** (Skills Central, site `billwerk.atlassian.net`, space id `11604230148`). The pages follow the space's "Skill page template" (page `11604262921`), sit under the overview page "Frisbii MCP Skills Pack" (`11604590602`), and are generated from the repo:

- `docs/confluence/pages.json`: page IDs, page copy per skill (summary, audience, week, what it does, triggers, examples, related skills, notes), the overview page and the calendar page.
- `scripts/confluence_page.py <skill>` renders a skill page; `--overview` renders the overview; `--calendar` prints the calendar page; `--list` shows every page ID.
- `docs/marketing-calendar.md` is the source of the "Skill of the Week: marketing calendar" page (`11604131885`).

**Whenever you change a skill, update its Confluence page in the same task.** That applies to any change under `plugins/frisbii-skills/skills/<skill>/` (SKILL.md, references, scripts), and to a change in its `docs/confluence/pages.json` entry.

1. If the change affects what the page says (behaviour, triggers, examples, limitations, product, week, status), update that skill's entry in `docs/confluence/pages.json` first. Name, product, call budget, files and section headings are read from `SKILL.md` automatically.
2. Before publishing, read the live page (`getConfluencePage`, markdown). If someone edited it in Confluence since the last publish (the version message lacks "Owner: Martyn Arbon", or the content differs from the render), carry those edits into `pages.json`, `docs/marketing-calendar.md` or the renderer first, so publishing doesn't undo them.
3. Run `python3 scripts/confluence_page.py <skill>` and publish the output with `updateConfluencePage`:
   - `cloudId`: `billwerk.atlassian.net`; `pageId`: the skill's `page_id`; `title`: the skill name;
   - `contentFormat`: `markdown`; `body`: the script output, unchanged;
   - `versionMessage`: `Owner: Martyn Arbon. <one-line summary of the change>`.
4. If the change affects the overview (a new or removed skill, a summary, product or week change), also publish `--overview` to page `11604590602` in the same way.
5. **New skill:** add an entry to `pages.json` (with `"page_id": null`), create the page with `createConfluencePage` (space `11604230148`, parent `11604590602`, title = skill name, `contentFormat: markdown`), record the ID with `python3 scripts/set_page_id.py <skill> <page-id>`, then republish the overview.
6. **Removed or renamed skill:** update `pages.json` and the overview, and ask the owner before deleting or renaming the Confluence page.
7. **Calendar changes** (`docs/marketing-calendar.md`, or a skill moving week): update the markdown, the skill's `week` in `pages.json`, then publish `--calendar` to page `11604131885` and the affected skill pages.
8. Commit the `pages.json` changes together with the skill change, and report the updated page links.

If Confluence can't be reached, finish the repo change, say which pages still need publishing, and don't claim they are in sync.

## Spreadsheet

`docs/Frisbii_MCP_Skills_Pack_and_13_Week_Plan.xlsx` is the planning sheet. Its feasibility columns (M–O on the Skills tab) come from `docs/mcp-tool-map.md`. When the tool map or validation results change, update the sheet too. Keep its existing columns, drop-downs and Summary formulas intact.
