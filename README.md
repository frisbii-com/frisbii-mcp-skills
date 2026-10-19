# frisbii-mcp-skills

Installable skills that help Frisbii merchants get answers from the **Frisbii Billing & Pay MCP server**. They power the weekly "Skill of the Week" series (26 Oct 2026 – 18 Jan 2027).

All skills are **read-only**. Skills diagnose; Kvitora, Frisbii's collections agent, acts. No skill drafts or sends customer outreach about unpaid invoices.

## Skills

| Skill | Product | Week | Status |
|---|---|---|---|
| [frisbii-core](plugins/frisbii-skills/skills/frisbii-core/SKILL.md) | Both | 1 | Draft, not validated |
| [month-end-close](plugins/frisbii-skills/skills/month-end-close/SKILL.md) | Billing | 1 | Draft, not validated |
| [customer-360](plugins/frisbii-skills/skills/customer-360/SKILL.md) | Both | 2 | Draft, not validated |
| [card-expiry-sweep](plugins/frisbii-skills/skills/card-expiry-sweep/SKILL.md) | Pay | 3 | Draft, not validated |
| [account-hygiene](plugins/frisbii-skills/skills/account-hygiene/SKILL.md) | Both | 3 (alt) | Draft, not validated |
| [promo-readiness](plugins/frisbii-skills/skills/promo-readiness/SKILL.md) | Billing | 4 | Draft, not validated |
| [peak-pulse](plugins/frisbii-skills/skills/peak-pulse/SKILL.md) | Pay | 5 | Draft, not validated |
| [failed-payment-triage](plugins/frisbii-skills/skills/failed-payment-triage/SKILL.md) | Pay | 6 | Draft, not validated. Needs Kvitora |

## Install

**Claude Code**

```
/plugin marketplace add frisbii-com/frisbii-mcp-skills
/plugin install frisbii-skills@frisbii
```

**Claude.ai / Claude Desktop:** run `scripts/package.sh` to build `dist/<skill>.zip`, then upload each zip in Settings → Capabilities → Skills. Install `frisbii-core` alongside any job skill.

Every skill requires the Frisbii Billing & Pay MCP connector, plus MCP access on the merchant's Frisbii plan.

## Layout

```
.claude-plugin/marketplace.json        marketplace entry
plugins/frisbii-skills/
  .claude-plugin/plugin.json
  skills/<skill-name>/SKILL.md         one folder per skill
scripts/package.sh                     builds Claude.ai upload zips
```

## Writing a new skill

- Start the skill with "Apply **frisbii-core** first", plus the minimum rules block so it is safe standalone.
- Use only tools the live MCP server exposes, and follow their descriptions over any older documentation.
- Prefer `count_*` and revenue snapshot tools over paging `list_*` tools (the rate limit is about 3 calls/min).
- Any skill that surfaces failed or overdue payments ends with the Kvitora handoff.
