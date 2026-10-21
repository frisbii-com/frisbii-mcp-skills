# frisbii-mcp-skills

Skills that let Frisbii merchants ask their AI assistant about their billing and payments data, using the **Frisbii Billing & Pay MCP server**. They work in Claude and in other AI assistants that support skills and MCP.

The repo holds two plugins:

- **frisbii-skills**: read-only skills. They never change anything in Frisbii or send anything. They can suggest next steps, and draft customer messages for the merchant to send.
- **frisbii-actions** (optional): skills that make changes, such as retrying payments or creating coupons. Every change is previewed and made only after the merchant confirms it.

## Read-only skills (frisbii-skills)

| Skill | Product | Try asking | Status |
|---|---|---|---|
| [frisbii-core](plugins/frisbii-skills/skills/frisbii-core/SKILL.md) | Both | (shared rules, used by every skill) | Tested |
| [month-end-close](plugins/frisbii-skills/skills/month-end-close/SKILL.md) | Billing | "Close September for me." | Tested |
| [payout-reconciliation](plugins/frisbii-skills/skills/payout-reconciliation/SKILL.md) | Pay | "Reconcile my September payouts." | Not yet tested |
| [customer-360](plugins/frisbii-skills/skills/customer-360/SKILL.md) | Both | "Brief me on this customer before my call." | Tested |
| [card-expiry-sweep](plugins/frisbii-skills/skills/card-expiry-sweep/SKILL.md) | Pay | "Check the cards for my top 20 customers." | Tested |
| [account-hygiene](plugins/frisbii-skills/skills/account-hygiene/SKILL.md) | Both | "Give my account a health check." | Tested |
| [promo-readiness](plugins/frisbii-skills/skills/promo-readiness/SKILL.md) | Billing | "Is my next promo set up right?" | Tested |
| [peak-pulse](plugins/frisbii-skills/skills/peak-pulse/SKILL.md) | Pay | "How are payments doing today?" | Tested |
| [failed-payment-triage](plugins/frisbii-skills/skills/failed-payment-triage/SKILL.md) | Pay | "Why are payments failing?" | Tested |
| [promo-cohort-quality](plugins/frisbii-skills/skills/promo-cohort-quality/SKILL.md) | Billing | "Did my Black Friday customers stick?" | Tested |
| [dispute-monitor](plugins/frisbii-skills/skills/dispute-monitor/SKILL.md) | Pay | "Which disputes need a response?" | Tested on an account with no disputes |
| [renewal-radar](plugins/frisbii-skills/skills/renewal-radar/SKILL.md) | Billing | "Which annual renewals are coming up?" | Tested on an account with no annual plans |
| [year-in-review](plugins/frisbii-skills/skills/year-in-review/SKILL.md) | Both | "My 2026 in review." | Tested |
| [board-pack](plugins/frisbii-skills/skills/board-pack/SKILL.md) | Billing | "Board pack for Q3." | Tested |
| [churn-and-retention](plugins/frisbii-skills/skills/churn-and-retention/SKILL.md) | Billing | "Who's at risk of cancelling?" | Tested |
| [migration-from-transform](plugins/frisbii-skills/skills/migration-from-transform/SKILL.md) | Billing (Transform customers) | "We're moving from Transform. Where do we start?" | Tested. Content still needs migration-team review |
| [dunning-review](plugins/frisbii-skills/skills/dunning-review/SKILL.md) | Pay | "How well do my retries work?" | Tested |
| [payment-method-mix](plugins/frisbii-skills/skills/payment-method-mix/SKILL.md) | Pay | "How do my customers pay?" | Tested |
| [plan-performance](plugins/frisbii-skills/skills/plan-performance/SKILL.md) | Billing | "Which plans are performing best?" | Tested |

"Tested" means the skill was run against a live Frisbii Billing account through the MCP server in October 2026, and fixed where the live tools behaved differently. Pay-only behaviour (payouts, disputes, card-heavy accounts) and annual plans still need testing on accounts that have that data.

## Action skills (frisbii-actions)

| Skill | Product | Changes | Status |
|---|---|---|---|
| [frisbii-actions-core](plugins/frisbii-actions/skills/frisbii-actions-core/SKILL.md) | Both | Safety rules for every action skill: preview, confirm, one write at a time | Not yet tested |
| [failed-payment-recovery](plugins/frisbii-actions/skills/failed-payment-recovery/SKILL.md) | Pay and Billing | Retries failed payments likely to succeed | Not yet tested |
| [promo-setup](plugins/frisbii-actions/skills/promo-setup/SKILL.md) | Billing | Creates discounts and coupons, extends coupons | Not yet tested |
| [retention-offer](plugins/frisbii-actions/skills/retention-offer/SKILL.md) | Billing | Applies a coupon to a subscription, pauses or resumes it | Not yet tested |
| [account-cleanup](plugins/frisbii-actions/skills/account-cleanup/SKILL.md) | Both | Voids stale unpaid invoices, cancels stuck pending subscriptions | Not yet tested |
| [dunning-tuning](plugins/frisbii-actions/skills/dunning-tuning/SKILL.md) | Pay and Billing | Changes a dunning plan's retries, grace period or final action | Not yet tested |
| [catalogue-build](plugins/frisbii-actions/skills/catalogue-build/SKILL.md) | Billing | Creates plans and add-ons, e.g. when moving from Frisbii Transform | Not yet tested |

Action skills need MCP access that allows changes. Each one lists the only write tools it may call, never refunds, charges or touches payment methods, and makes at most 10 changes per confirmation. They will be tested on a test account with write access, never on live merchant data.

## Requirements

- The **Frisbii Billing & Pay MCP connector** set up in your AI assistant.
- **MCP access on your Frisbii plan.** Each skill checks this first and stops with a clear message if access is missing or blocked.

## Install

**Claude Code**

```
/plugin marketplace add frisbii-com/frisbii-mcp-skills
/plugin install frisbii-skills@frisbii
/plugin install frisbii-actions@frisbii      # optional: skills that make changes
```

**Claude.ai / Claude Desktop:** run `scripts/package.sh` to build `dist/<skill>.zip`, then upload each zip in Settings → Capabilities → Skills. Install `frisbii-core` alongside any read-only skill, and `frisbii-actions-core` alongside any action skill.

**Other AI assistants:** each skill is a standard `SKILL.md` folder. Use your assistant's own way of adding skills, with the same `-core` pairing as above.

## Good to know

What the MCP server allows shapes what the skills can do:

- **Data is a snapshot.** Figures run about two hours behind for payments, invoices and subscriptions, and longer for revenue. Every answer says what time its data covers.
- **Rate limit of about 3 calls a minute.** Skills prefer `count_*` and revenue snapshot tools over paging `list_*` tools, and state a call budget up front.
- **Some lists cover the last 30 days only** when no customer is given (payment methods, failed payments, dunning invoices, charges, settlements), and return about 10 rows per page.
- **No account-wide card list.** card-expiry-sweep checks the customers you name (up to 20 at a time) plus recent expired-card failures across the account.

## Layout

```
.claude-plugin/marketplace.json        marketplace entry
plugins/frisbii-skills/                read-only skills
  .claude-plugin/plugin.json
  skills/<skill-name>/SKILL.md         one folder per skill
plugins/frisbii-actions/               optional action skills (write tools)
  .claude-plugin/plugin.json
  skills/<skill-name>/SKILL.md
scripts/package.sh                     builds Claude.ai upload zips
```

## Writing a new skill

- Start a read-only skill with "Apply **frisbii-core** first", and an action skill with "Apply **frisbii-actions-core** first", plus the minimum rules block so it is safe standalone.
- Read-only skills go in `frisbii-skills` and never call write tools. Skills that change data go in `frisbii-actions`, list their allowed write tools under **Writes**, and follow the confirm-before-write protocol.
- Use only tools the live MCP server exposes, and follow their descriptions over any older documentation. Check `group_by` values against the server: an invalid one is refused and the error lists the allowed columns.
- Any skill that surfaces failed or overdue payments ends with the recovery next steps (`frisbii-core/references/recovery-next-steps.md`).
- After changing skills, run `scripts/package.sh` and `claude plugin validate .`.
