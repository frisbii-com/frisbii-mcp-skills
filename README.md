# frisbii-mcp-skills

Installable skills that help Frisbii merchants get answers from the **Frisbii Billing & Pay MCP server**.

The repo holds two plugins:

- **frisbii-skills**: read-only skills. They never change anything in Frisbii or send anything. They can suggest next steps, and draft customer messages for the merchant to send.
- **frisbii-actions** (opt-in): skills that make changes, such as retrying payments or creating coupons. Every change is previewed and made only after the merchant confirms it.

## Read-only skills (frisbii-skills)

| Skill | Product | Status |
|---|---|---|
| [frisbii-core](plugins/frisbii-skills/skills/frisbii-core/SKILL.md) | Both | Draft, not validated |
| [month-end-close](plugins/frisbii-skills/skills/month-end-close/SKILL.md) | Billing | Draft, not validated |
| [payout-reconciliation](plugins/frisbii-skills/skills/payout-reconciliation/SKILL.md) | Pay | Draft, not validated |
| [customer-360](plugins/frisbii-skills/skills/customer-360/SKILL.md) | Both | Draft, not validated |
| [card-expiry-sweep](plugins/frisbii-skills/skills/card-expiry-sweep/SKILL.md) | Pay | Draft, not validated |
| [account-hygiene](plugins/frisbii-skills/skills/account-hygiene/SKILL.md) | Both | Draft, not validated |
| [promo-readiness](plugins/frisbii-skills/skills/promo-readiness/SKILL.md) | Billing | Draft, not validated |
| [peak-pulse](plugins/frisbii-skills/skills/peak-pulse/SKILL.md) | Pay | Draft, not validated |
| [failed-payment-triage](plugins/frisbii-skills/skills/failed-payment-triage/SKILL.md) | Pay | Draft, not validated |
| [promo-cohort-quality](plugins/frisbii-skills/skills/promo-cohort-quality/SKILL.md) | Billing | Draft, not validated |
| [dispute-monitor](plugins/frisbii-skills/skills/dispute-monitor/SKILL.md) | Pay | Draft, not validated |
| [renewal-radar](plugins/frisbii-skills/skills/renewal-radar/SKILL.md) | Billing | Draft, not validated |
| [year-in-review](plugins/frisbii-skills/skills/year-in-review/SKILL.md) | Both | Draft, not validated |
| [board-pack](plugins/frisbii-skills/skills/board-pack/SKILL.md) | Billing | Draft, not validated |
| [churn-and-retention](plugins/frisbii-skills/skills/churn-and-retention/SKILL.md) | Billing | Draft, not validated |
| [migration-from-transform](plugins/frisbii-skills/skills/migration-from-transform/SKILL.md) | Billing (Transform customers) | Draft, not validated. Content needs migration-team review |
| [dunning-review](plugins/frisbii-skills/skills/dunning-review/SKILL.md) | Pay | Draft, not validated |
| [payment-method-mix](plugins/frisbii-skills/skills/payment-method-mix/SKILL.md) | Pay | Draft, not validated |
| [plan-performance](plugins/frisbii-skills/skills/plan-performance/SKILL.md) | Billing | Draft, not validated |

All 19 skills are drafted and still need testing against live merchant data.

## Action skills (frisbii-actions)

| Skill | Product | Changes | Status |
|---|---|---|---|
| [frisbii-actions-core](plugins/frisbii-actions/skills/frisbii-actions-core/SKILL.md) | Both | Safety rules for every action skill: preview, confirm, one write at a time | Draft, not validated |
| [failed-payment-recovery](plugins/frisbii-actions/skills/failed-payment-recovery/SKILL.md) | Pay and Billing | Retries failed payments likely to succeed | Draft, not validated |
| [promo-setup](plugins/frisbii-actions/skills/promo-setup/SKILL.md) | Billing | Creates discounts and coupons, extends coupons | Draft, not validated |
| [retention-offer](plugins/frisbii-actions/skills/retention-offer/SKILL.md) | Billing | Applies a coupon to a subscription, pauses or resumes it | Draft, not validated |
| [account-cleanup](plugins/frisbii-actions/skills/account-cleanup/SKILL.md) | Both | Voids stale unpaid invoices, cancels stuck pending subscriptions | Draft, not validated |
| [dunning-tuning](plugins/frisbii-actions/skills/dunning-tuning/SKILL.md) | Pay and Billing | Changes a dunning plan's retries, grace period or final action | Draft, not validated |
| [catalogue-build](plugins/frisbii-actions/skills/catalogue-build/SKILL.md) | Billing | Creates plans and add-ons, e.g. when moving from Frisbii Transform | Draft, not validated |

Action skills need MCP access that allows changes. Each one lists the only write tools it may call, never refunds or touches payment methods, and makes at most 10 changes per confirmation.

## Install

**Claude Code**

```
/plugin marketplace add frisbii-com/frisbii-mcp-skills
/plugin install frisbii-skills@frisbii
/plugin install frisbii-actions@frisbii      # optional: skills that make changes
```

**Claude.ai / Claude Desktop:** run `scripts/package.sh` to build `dist/<skill>.zip`, then upload each zip in Settings → Capabilities → Skills. Install `frisbii-core` alongside any read-only skill, and `frisbii-actions-core` alongside any action skill.

Every skill requires the Frisbii Billing & Pay MCP connector, plus MCP access on the merchant's Frisbii plan.

## Layout

```
.claude-plugin/marketplace.json        marketplace entry
plugins/frisbii-skills/                read-only skills
  .claude-plugin/plugin.json
  skills/<skill-name>/SKILL.md         one folder per skill
plugins/frisbii-actions/               opt-in action skills (write tools)
  .claude-plugin/plugin.json
  skills/<skill-name>/SKILL.md
scripts/package.sh                     builds Claude.ai upload zips
```

## Writing a new skill

- Start a read-only skill with "Apply **frisbii-core** first", and an action skill with "Apply **frisbii-actions-core** first", plus the minimum rules block so it is safe standalone.
- Read-only skills go in `frisbii-skills` and never call write tools. Skills that change data go in `frisbii-actions`, list their allowed write tools under **Writes**, and follow the confirm-before-write protocol.
- Use only tools the live MCP server exposes, and follow their descriptions over any older documentation.
- Prefer `count_*` and revenue snapshot tools over paging `list_*` tools (the rate limit is about 3 calls/min).
- Any skill that surfaces failed or overdue payments ends with the recovery next steps (`frisbii-core/references/recovery-next-steps.md`).
