# CLAUDE.md

Frisbii MCP Skills Pack: skills for Frisbii Billing and Frisbii Pay merchants, built on the Frisbii Billing & Pay MCP server. The `frisbii-skills` plugin is read-only; the opt-in `frisbii-actions` plugin makes changes, always after the merchant confirms them. Owner: Martyn Arbon. See `README.md` for the layout and the skill list.

This repository is public. Keep internal material (planning sheets, marketing plans, email drafts, validation notes, internal page IDs or links) out of it.

## Working on skills

- Read-only skills live in `plugins/frisbii-skills/skills/<skill-name>/SKILL.md`; skills that change data live in `plugins/frisbii-actions/skills/<skill-name>/SKILL.md`. The frontmatter `name` must equal the folder name.
- Base every tool call on the **live** Frisbii Billing & Pay MCP tool schemas (load them with ToolSearch, `mcp__Frisbii_Billing_Pay_MCP__*`), not on older docs. If a tool description disagrees with a skill, fix the skill.
- Every read-only skill starts with "Apply **frisbii-core** first" plus the minimum-rules block, states its **Product** and **Call budget** lines, and never calls a write tool.
- Every action skill starts with "Apply **frisbii-actions-core** first" plus its minimum-rules block, states **Product**, **Call budget** and **Writes** (the only write tools it may call), and follows the confirm-before-write protocol in `frisbii-actions-core`. Never add refunds, charges or payment-method changes.
- Skills that surface failed or overdue payments end with the recovery next steps in `frisbii-core/references/recovery-next-steps.md`.
- After changing skills, run `scripts/package.sh` and `claude plugin validate .`.

## Documentation pages (Frisbii maintainers)

Each skill also has an internal documentation page. Whenever you change a skill, update its page in the same task, following the internal guide "Maintaining the skill pages" in the Skills Central Confluence space. The page tooling and page copy live there, not in this repo. If you can't reach it, say which skills changed so the owner can update their pages.
