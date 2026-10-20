# CLAUDE.md

Frisbii MCP Skills Pack: read-only skills for Frisbii Billing and Frisbii Pay merchants, built on the Frisbii Billing & Pay MCP server. Owner: Martyn Arbon. See `README.md` for the layout and the skill list.

## Working on skills

- Skills live in `plugins/frisbii-skills/skills/<skill-name>/SKILL.md`. The frontmatter `name` must equal the folder name.
- Base every tool call on the **live** Frisbii Billing & Pay MCP tool schemas (load them with ToolSearch, `mcp__Frisbii_Billing_Pay_MCP__*`), not on older docs. If a tool description disagrees with a skill, fix the skill.
- Every job skill starts with "Apply **frisbii-core** first" plus the minimum-rules block, states its **Product**, **Featured** week and **Call budget** lines, and stays read-only.
- Kvitora is out of scope (decision of 19 Oct 2026): skills end with the recovery next steps in `frisbii-core/references/recovery-next-steps.md`, never a Kvitora handoff.
- After changing skills, run `scripts/package.sh` and `claude plugin validate .`.
