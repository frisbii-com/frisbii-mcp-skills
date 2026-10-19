---
name: renewal-radar
description: Lists annual and high-value Frisbii subscription renewals coming up in the next 30–60 days, flags renewals with a cancellation already scheduled, and shows the recurring revenue up for renewal. Use when a merchant asks about upcoming renewals, "which annual contracts renew in January", renewals at risk, or wants to prepare account managers before the new year. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# renewal-radar

**Product:** Billing.
**Featured:** week 8 (14 Dec 2026, pre-January renewals).
**Call budget:** 2 pre-flight calls + 3–12 calls, about 2–5 minutes depending on how many annual subscriptions exist.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies. Always quote `as_of` for snapshot figures.

## 1. Scope

- **Horizon:** default 60 days from today. Use the merchant's horizon if given ("January renewals" means 1–31 Jan).
- **What counts:** subscriptions on plans with a billing interval of 6 months or more (annual by default), plus any subscription above a value threshold if the merchant gives one ("over EUR 1,000/year").

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `get_subscription_revenue` | `state=active`, `group_by=plan`, `group_limit=25` | Plans ranked by MRR, so you know where the value sits |
| 2 | `list_plans` | `plan_state=active`, `limit=100` | Plan intervals (`interval_length` + `schedule_type`) to find annual plans |
| 2b | `get_plan` | `handle`, for the top plans from call 1 (max 5), **only if call 2 is empty** | Fallback for the known list_plans issue |
| 3…n | `list_subscriptions` | `plan_handle`, `state=active_non_cancelled`, `limit=100`, per annual plan (max 5 plans, max 2 pages each) | Next renewal date, quantity, customer per subscription |
| last | `get_committed_recurring_revenue` | `group_by=plan` | Revenue on those plans already asked to stop |

Filter call 3's rows to a next renewal date inside the horizon. If the 5-plan or 2-page caps cut anything off, say which plans weren't fully covered.

For scheduled cancellations among the renewing subscriptions: `list_subscriptions` with `state=cancelled` (active, cancellation scheduled) and the same `plan_handle`, or rely on call "last" for the totals only.

## 3. Output

```
## Renewal radar: next {horizon} ({from}–{to})
**{n} renewals** on annual plans · {CUR} {annual value} up for renewal · {m} with a cancellation already scheduled

### Renewing (soonest first)
| Renews | Customer | Plan | Qty | Annual value | Note |
| 2 Jan  | acme-a/s | Pro Annual | 5 | DKK 59,940 | ⚠ cancellation scheduled |

### By plan
| Plan | Renewing | Annual value | Already asked to stop |
```

- Value: plan amount × quantity (from `get_plan` or the subscription row, minor units). Label it "list value" if discounts may apply.
- Add one-line suggestions where useful: talk to scheduled-cancellation accounts before their end date; check payment methods on the largest renewals (customer-360 or card-expiry-sweep).
- For a single account, suggest running customer-360 on it.
