# frisbii-mcp-skills

Installable skills that help Frisbii merchants get answers from the **Frisbii Billing & Pay MCP server**. They power the weekly "Skill of the Week" series (26 Oct 2026 – 18 Jan 2027).

All skills are **read-only**: they never change anything in Frisbii or send anything. They can suggest next steps, and draft customer messages for the merchant to send.

## Skills

| Skill | Product | Week | Status |
|---|---|---|---|
| [frisbii-core](plugins/frisbii-skills/skills/frisbii-core/SKILL.md) | Both | 1 | Draft, not validated |
| [month-end-close](plugins/frisbii-skills/skills/month-end-close/SKILL.md) | Billing | 1 | Draft, not validated |
| [payout-reconciliation](plugins/frisbii-skills/skills/payout-reconciliation/SKILL.md) | Pay | 1 & 11 (alt) | Draft, not validated |
| [customer-360](plugins/frisbii-skills/skills/customer-360/SKILL.md) | Both | 2 | Draft, not validated |
| [card-expiry-sweep](plugins/frisbii-skills/skills/card-expiry-sweep/SKILL.md) | Pay | 3 | Draft, not validated |
| [account-hygiene](plugins/frisbii-skills/skills/account-hygiene/SKILL.md) | Both | 3 (alt) | Draft, not validated |
| [promo-readiness](plugins/frisbii-skills/skills/promo-readiness/SKILL.md) | Billing | 4 | Draft, not validated |
| [peak-pulse](plugins/frisbii-skills/skills/peak-pulse/SKILL.md) | Pay | 5 | Draft, not validated |
| [failed-payment-triage](plugins/frisbii-skills/skills/failed-payment-triage/SKILL.md) | Pay | 6 | Draft, not validated |
| [promo-cohort-quality](plugins/frisbii-skills/skills/promo-cohort-quality/SKILL.md) | Billing | 7 | Draft, not validated |
| [dispute-monitor](plugins/frisbii-skills/skills/dispute-monitor/SKILL.md) | Pay | 7 (alt) | Draft, not validated |
| [renewal-radar](plugins/frisbii-skills/skills/renewal-radar/SKILL.md) | Billing | 8 | Draft, not validated |
| [year-in-review](plugins/frisbii-skills/skills/year-in-review/SKILL.md) | Both | 9 | Draft, not validated |
| [board-pack](plugins/frisbii-skills/skills/board-pack/SKILL.md) | Billing | 11 | Draft, not validated |
| [churn-and-retention](plugins/frisbii-skills/skills/churn-and-retention/SKILL.md) | Billing | 12 | Draft, not validated |
| [migration-from-transform](plugins/frisbii-skills/skills/migration-from-transform/SKILL.md) | Billing (Transform customers) | 13 | Draft, not validated. Content needs migration-team review |
| [dunning-review](plugins/frisbii-skills/skills/dunning-review/SKILL.md) | Pay | 13 (alt) | Draft, not validated |
| [payment-method-mix](plugins/frisbii-skills/skills/payment-method-mix/SKILL.md) | Pay | 4 (alt) | Draft, not validated |
| [plan-performance](plugins/frisbii-skills/skills/plan-performance/SKILL.md) | Billing | Unscheduled | Draft, not validated |

All 19 skills from the roadmap are drafted. The full roadmap and the skill-to-MCP-tool mapping are in [docs/mcp-tool-map.md](docs/mcp-tool-map.md). The test plan is in [docs/validation-plan.md](docs/validation-plan.md).

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
docs/mcp-tool-map.md                   skill → MCP tool mapping and gaps
docs/validation-plan.md                test prompts and pass criteria
scripts/package.sh                     builds Claude.ai upload zips
```

## Writing a new skill

- Start the skill with "Apply **frisbii-core** first", plus the minimum rules block so it is safe standalone.
- Use only tools the live MCP server exposes, and follow their descriptions over any older documentation.
- Prefer `count_*` and revenue snapshot tools over paging `list_*` tools (the rate limit is about 3 calls/min).
- Any skill that surfaces failed or overdue payments ends with the recovery next steps (`frisbii-core/references/recovery-next-steps.md`).
