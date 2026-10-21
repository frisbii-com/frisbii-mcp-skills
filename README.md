# frisbii-mcp-skills

Skills that let Frisbii merchants ask their AI assistant about their billing and payments data, using the **Frisbii Billing & Pay MCP server**. They work in Claude and in other AI assistants that support skills and MCP.

The repo holds two plugins:

- **frisbii-skills**: read-only skills. They never change anything in Frisbii or send anything. They can suggest next steps, and draft customer messages for the merchant to send.
- **frisbii-actions** (optional): skills that make changes, such as retrying payments or creating coupons. Every change is previewed and made only after the merchant confirms it.

## Read-only skills (frisbii-skills)

| Skill | Works with | Try asking |
|---|---|---|
| [frisbii-core](plugins/frisbii-skills/skills/frisbii-core/SKILL.md) | Frisbii Billing, Frisbii Pay | (shared rules, used by every skill) |
| [month-end-close](plugins/frisbii-skills/skills/month-end-close/SKILL.md) | Frisbii Billing, Frisbii Pay (subscriptions) | "Close September for me." |
| [payout-reconciliation](plugins/frisbii-skills/skills/payout-reconciliation/SKILL.md) | Frisbii Billing, Frisbii Pay | "Reconcile my September payouts." |
| [customer-360](plugins/frisbii-skills/skills/customer-360/SKILL.md) | Frisbii Billing, Frisbii Pay | "Brief me on this customer before my call." |
| [card-expiry-sweep](plugins/frisbii-skills/skills/card-expiry-sweep/SKILL.md) | Frisbii Billing, Frisbii Pay | "Check the cards for my top 20 customers." |
| [account-hygiene](plugins/frisbii-skills/skills/account-hygiene/SKILL.md) | Frisbii Billing, Frisbii Pay | "Give my account a health check." |
| [promo-readiness](plugins/frisbii-skills/skills/promo-readiness/SKILL.md) | Frisbii Billing, Frisbii Pay (subscriptions) | "Is my next promo set up right?" |
| [peak-pulse](plugins/frisbii-skills/skills/peak-pulse/SKILL.md) | Frisbii Billing (sign-ups), Frisbii Pay | "How are payments doing today?" |
| [failed-payment-triage](plugins/frisbii-skills/skills/failed-payment-triage/SKILL.md) | Frisbii Billing, Frisbii Pay | "Why are payments failing?" |
| [promo-cohort-quality](plugins/frisbii-skills/skills/promo-cohort-quality/SKILL.md) | Frisbii Billing, Frisbii Pay (subscriptions) | "Did my Black Friday customers stick?" |
| [dispute-monitor](plugins/frisbii-skills/skills/dispute-monitor/SKILL.md) | Frisbii Billing, Frisbii Pay | "Which disputes need a response?" |
| [renewal-radar](plugins/frisbii-skills/skills/renewal-radar/SKILL.md) | Frisbii Billing | "Which annual renewals are coming up?" |
| [year-in-review](plugins/frisbii-skills/skills/year-in-review/SKILL.md) | Frisbii Billing, Frisbii Pay | "My 2026 in review." |
| [board-pack](plugins/frisbii-skills/skills/board-pack/SKILL.md) | Frisbii Billing, Frisbii Pay (subscriptions) | "Board pack for Q3." |
| [churn-and-retention](plugins/frisbii-skills/skills/churn-and-retention/SKILL.md) | Frisbii Billing, Frisbii Pay (subscriptions) | "Who's at risk of cancelling?" |
| [migration-from-transform](plugins/frisbii-skills/skills/migration-from-transform/SKILL.md) | Frisbii Billing (moving from Frisbii Transform) | "We're moving from Transform. Where do we start?" |
| [dunning-review](plugins/frisbii-skills/skills/dunning-review/SKILL.md) | Frisbii Billing, Frisbii Pay | "How well do my retries work?" |
| [payment-method-mix](plugins/frisbii-skills/skills/payment-method-mix/SKILL.md) | Frisbii Billing, Frisbii Pay | "How do my customers pay?" |
| [plan-performance](plugins/frisbii-skills/skills/plan-performance/SKILL.md) | Frisbii Billing, Frisbii Pay (subscriptions) | "Which plans are performing best?" |

"Frisbii Pay (subscriptions)" means the skill works for Frisbii Pay merchants who run subscriptions on Pay.

## Action skills (frisbii-actions)

| Skill | Works with | Changes |
|---|---|---|
| [frisbii-actions-core](plugins/frisbii-actions/skills/frisbii-actions-core/SKILL.md) | Frisbii Billing, Frisbii Pay | Safety rules for every action skill: preview, confirm, one write at a time |
| [failed-payment-recovery](plugins/frisbii-actions/skills/failed-payment-recovery/SKILL.md) | Frisbii Billing, Frisbii Pay | Retries failed payments likely to succeed |
| [promo-setup](plugins/frisbii-actions/skills/promo-setup/SKILL.md) | Frisbii Billing | Creates discounts and coupons, extends coupons |
| [retention-offer](plugins/frisbii-actions/skills/retention-offer/SKILL.md) | Frisbii Billing | Applies a coupon to a subscription, pauses or resumes it |
| [account-cleanup](plugins/frisbii-actions/skills/account-cleanup/SKILL.md) | Frisbii Billing, Frisbii Pay | Voids stale unpaid invoices, cancels stuck pending subscriptions |
| [dunning-tuning](plugins/frisbii-actions/skills/dunning-tuning/SKILL.md) | Frisbii Billing, Frisbii Pay | Changes a dunning plan's retries, grace period or final action |
| [catalogue-build](plugins/frisbii-actions/skills/catalogue-build/SKILL.md) | Frisbii Billing | Creates plans and add-ons, e.g. when moving from Frisbii Transform |

Action skills need MCP access that allows changes. Each one lists the only write tools it may call, never refunds, charges or touches payment methods, and makes at most 10 changes per confirmation.

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

## License

MIT. See [LICENSE](LICENSE).
