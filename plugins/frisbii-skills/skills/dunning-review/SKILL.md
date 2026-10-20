---
name: dunning-review
description: Reviews how well a Frisbii account's dunning (failed-payment retry) process recovers money. Covers dunning plans and retry schedules, what is in dunning now and at which step, how much was recovered vs lost, typical time to recover, and where recovery stalls. Use when a merchant asks how their dunning performs, about recovery rate, "are my retries working", how long failed payments take to recover, or whether to change their dunning settings. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# dunning-review

**Product:** Pay. Also works for Billing.
**Call budget:** 2 pre-flight calls + 6–9 calls, about 3–4 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Never change dunning plans or retry invoices. Suggest changes for the merchant to make in the Frisbii dashboard. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies.

## 1. Window

Default: invoices **due in the last 90 days**. Recovery takes weeks, so shorter windows understate it.

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `list_dunning_plans` | – | Every dunning plan: retry schedule (days), grace period, final action, default flag |
| 2 | `count_invoices` | `dunning_invoices=true` | Everything in dunning now: count and amount |
| 3 | `investigate_dunning_invoices` | `limit=100` (max 2 pages) | Current step, next retry date and days overdue per invoice |
| 4 | `count_invoices` | `due_from`, `due_to`, `group_by=state` | Outcomes for the window: settled, dunning, failed, cancelled |
| 5–7 | `list_invoices` | `state=settled`, `due_from`, `due_to`, `limit=100` (max 3 pages) | Settled invoices. Those carrying a dunning start timestamp were **recovered** through dunning. Use both timestamps for time to recover |
| 8 (optional) | `list_invoices` | `state=failed`, `due_from`, `due_to`, `limit=100` | Invoices that left dunning unpaid (**lost**) |

If the page caps cut anything off, label recovered and lost figures as "based on a sample of {n} invoices".

## 3. Metrics

- **Recovered** = settled invoices with a dunning timestamp: count and amount.
- **Lost** = failed (and cancelled after dunning) invoices in the window.
- **Recovery rate** = recovered ÷ (recovered + lost), by amount and by count. Exclude invoices still in dunning from the rate and show them as "still in progress".
- **Time to recover** = settled timestamp − dunning start. Report median and 90th percentile, in days.
- **Step profile:** from call 3, how many invoices sit at each dunning step, and where recoveries happen (if step data exists on the settled rows).
- **Plan coverage:** failed invoices not in dunning mean no retries happen. Flag them, using call 4's `failed` rows against call 2.

## 4. Output

```
## Dunning review: invoices due {window}
**Recovered {CUR} {x}** ({n} invoices) · **lost {CUR} {y}** · recovery rate **{z}%** · median {d} days to recover
In dunning now: {n} invoices, {CUR} {amount}

### Dunning plans
| Plan | Retries (days) | Grace | Final action | Default |

### Where invoices are now
| Step | Invoices | Amount | Avg days overdue |

### Recovery timing
| Recovered within | Share |
| 3 days | | 7 days | | 14 days | | 30 days | |
```

## 5. Suggestions

Base 2–4 suggestions on the numbers, for example:
- Most recoveries in the first days and almost none after day {n} → late retries add little; consider a shorter schedule or an earlier final action.
- A large share lost to hard declines → retries can't fix expired or closed cards. Card-update requests (card-expiry-sweep) work better.
- Failed invoices not in any dunning flow → assign a dunning plan in the dashboard.
- Final action cancels subscriptions → check that suits high-value customers.

These are suggestions for the merchant to apply in the Frisbii dashboard. Never apply them.
