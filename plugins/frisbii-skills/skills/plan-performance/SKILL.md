---
name: plan-performance
description: Compares a Frisbii merchant's subscription plans. Shows which plans hold the most recurring revenue, which are growing (new sign-ups), which lose the most subscribers (churn), how much revenue on each plan is already scheduled to cancel, and how discounts are used. Use when a merchant asks which plans perform best, plan growth or churn, "which plan should we push or retire", revenue by plan, or a pricing review. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# plan-performance

**Product:** Billing. Also works for Pay merchants running subscriptions on Pay.
**Call budget:** 2 pre-flight calls + 6–8 calls, about 3 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies or VAT treatments. Always quote `as_of`.
- Churn means **`ended_from`/`ended_to`** (actually ended), not `cancelled_*`.

## 1. Window

Default: the **last 90 days** for growth and churn. Revenue and live counts are the current snapshot.

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `get_subscription_revenue` | `state=active`, `group_by=plan`, `group_limit=25` | MRR per plan (only `NORMALIZED` rows for monthly figures) |
| 2 | `count_subscriptions` | `state=active_non_cancelled`, `group_by=plan`, `group_limit=25` | Live subscriptions per plan |
| 3 | `count_subscriptions` | `created_from`, `created_to`, `group_by=plan`, `group_limit=25` | New subscriptions per plan (growth) |
| 4 | `count_subscriptions` | `ended_from`, `ended_to`, `group_by=plan`, `group_limit=25` | Ended per plan (churn) |
| 5 | `get_committed_recurring_revenue` | `group_by=plan`, `group_limit=25` | Revenue already asked to stop, per plan. If it fails with `error=truncated`, raise `group_limit` or drop the plan grouping |
| 6 | `list_plans` | `plan_state=active`, `limit=100` | Plan names, prices, intervals. **If empty** (the known list_plans issue), call `get_plan` for the top 5 plans by MRR instead and note it |
| 7 (optional) | `list_coupons` | `state=active`, `limit=100` | Which coupons apply to which plans (eligible plans), with redemption counts |

Per-plan revenue and counts come from calls 1–5, so a `list_plans` failure only affects display names. Never block the report on it: show plan handles if names aren't available.

**Discounts per plan:** `count_subscription_discounts` can't filter by plan. Use coupon eligibility from call 7 as the signal. For exact discounted subscriptions per plan, offer `create_report_export` with `report=subscription_discounts`.

## 3. Derive (per plan)

- **ARPU** = MRR ÷ live subscriptions (calls 1 and 2). A revenue line includes add-ons, so label it "MRR per subscription incl. add-ons".
- **Net growth (90 days)** = new − ended (calls 3 and 4).
- **Churn ratio** = ended ÷ (live now + ended − new), estimated. Mark it "≈".
- **At-risk share** = scheduled-cancellation MRR ÷ plan MRR (call 5).
- Plans with live subscriptions but marked superseded in `list_plans` / `get_plan` are **legacy plans**. Flag them.

## 4. Output

```
## Plan performance: snapshot {as_of} · growth and churn over {window}

| Plan | Live subs | MRR | Share of MRR | MRR / sub | New | Ended | Net | ≈ Churn | At risk |
| Pro Monthly | 1,240 | DKK 247,000 | 41% | 199 | +180 | −95 | +85 | 7% | 3% |

### Highlights
- Biggest: {plan} ({x}% of MRR)
- Fastest growing: {plan} (+{n} net)
- Highest churn: {plan} (≈{x}%)
- Legacy plans still billing: {list}
- Coupons tied to plans: {plan → codes}
```

## 5. Takeaways

2–4 specific, data-backed points, e.g.:
- A small plan with high churn and low MRR per subscription → candidate to review or retire.
- A growing plan with low churn → candidate to promote in the next campaign (promo-readiness).
- Legacy plans with many subscribers → plan a migration to current plans. The skill doesn't change anything; changes go through the dashboard.
- Heavy coupon use on one plan → check with promo-cohort-quality whether discounted subscribers stay.
