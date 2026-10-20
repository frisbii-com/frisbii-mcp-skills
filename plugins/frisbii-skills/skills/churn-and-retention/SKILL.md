---
name: churn-and-retention
description: Churn and retention analysis for a Frisbii Billing merchant. Shows subscriptions and MRR that ended over the last three months, the trend, churn by plan, voluntary vs involuntary (failed-payment) churn where available, revenue already scheduled to cancel, and at-risk segments such as customers in dunning or subscriptions on hold. Use when a merchant asks about churn, retention, cancellations, "why are customers leaving", January churn, or which customers are at risk of cancelling. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# churn-and-retention

**Product:** Billing. Also works for Pay merchants running subscriptions on Pay.
**Call budget:** 2 pre-flight calls + 9–10 calls, about 4 minutes.

## Before you start

Apply **frisbii-core** first, especially section 8 on subscription end dates. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Churn means **`ended_from`/`ended_to`**: the subscription actually ended. `cancelled_*` is when cancellation was requested.
- Amounts are minor units. Never add across currencies or VAT treatments. Always quote `as_of`.

## 1. Window

Default: the **last three full calendar months**, reported month by month, plus month-to-date if past the 10th.

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1–3 | `count_subscriptions` | `ended_*` = each month | Ended subscriptions per month (trend) |
| 4 | `get_subscription_revenue` | `ended_*` = whole window, `group_by=plan`, `group_limit=10` | MRR that ended, by plan |
| 5 | `count_subscriptions` | `state=active_non_cancelled` | Live base now (for the rate) |
| 6 | `get_committed_recurring_revenue` | `group_by=plan` | MRR already asked to stop: the forward view |
| 7 | `count_subscriptions` | `state=on_hold` | Paused subscriptions (an at-risk segment) |
| 8 | `count_customers` | `min_dunning_amount=1` | Customers with invoices in dunning (involuntary churn risk), with `dunning_amount_sum` |
| 9 | `count_subscriptions` | `ended_*` = whole window, `group_by=expire_reason` | Voluntary vs involuntary split. **If this group_by is refused, skip it** and use the fallback below |

**Fallback for the voluntary vs involuntary split:** offer `create_report_export` (report `subscriptions`, filters `ended_from`/`ended_to`) and read the expire reason from the rows if present. If neither works, say: "The split by reason isn't available from the MCP yet." Never guess it.

Expire reasons: `dunning` = involuntary (payment failure). Anything else (`cancelled`, `ondemand`, `fixed`, …) = voluntary or planned.

## 3. Derived

- **Monthly churn rate (estimate)** = ended in month ÷ (live now + ended since the month started − new since the month started). Fetching new subscriptions per month costs one `count_subscriptions created_*` call per month. Add those calls only if the merchant wants rates and not just counts. Label the result "≈".
- **Trend:** month-on-month change in ended count and MRR.

## 4. Output

```
## Churn and retention: {months}
**{n} subscriptions ended** in the last 3 months ({CUR} {x} MRR) · trend {↑/↓ y%} · {CUR} {z} MRR already scheduled to cancel

| Month | Ended | MRR ended | Est. churn rate |

### Where churn comes from
| Plan | Ended MRR | Share |
Voluntary vs involuntary: {split, or "not available"}

### At risk now
| Segment | Count | Amount |
| Scheduled to cancel | | CUR |
| On hold | | – |
| Customers in dunning | | CUR |
```

## 5. Takeaways and next steps

Give 2–4 specific suggestions based on the data, e.g.:
- One plan dominates churn → review that plan's pricing or onboarding. plan-performance can go deeper.
- High involuntary share, or many customers in dunning → run failed-payment-triage and dunning-review. Add recovery next steps (frisbii-core `references/recovery-next-steps.md`).
- Large scheduled-cancellation MRR → contact those accounts before their end date. renewal-radar and customer-360 help prepare. Offer to draft a retention message for the merchant to send.
