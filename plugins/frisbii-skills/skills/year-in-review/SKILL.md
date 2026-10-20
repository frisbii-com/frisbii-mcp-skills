---
name: year-in-review
description: Shareable annual recap of a merchant's year on Frisbii. Covers payment volume and payment-method mix (Pay), recurring revenue growth, new subscribers and top plans (Billing), customer growth and standout moments, plus an optional ready-to-post LinkedIn summary. Use when a merchant asks for their year in review, an annual recap or wrap-up, "how was 2026", or something to share about their year. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# year-in-review

**Product:** Both. Pay and Billing sections are chosen automatically.
**Call budget:** 2 pre-flight calls + 2 detection calls + 5–8 calls, about 3–4 minutes.

## Before you start

Apply **frisbii-core** first, including the Pay vs Billing detection. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies. Always quote `as_of`.

## 1. Window

Default: **1 Jan to today** of the current year (`*_from=2026-01-01`, `*_to=tomorrow`). Comparison: the same span last year. If run in January, offer the full previous year.

## 2. Calls

**Payments (always, if transactions > 0):**

| # | Tool | Arguments | Gives |
|---|---|---|---|
| P1 | `count_transactions` | `settled_from`, `settled_to`, `state=settled`, `group_by=payment_type` | Volume and count by method |
| P2 | `count_transactions` | same, `group_by=settled_month` | Month-by-month volume and the best month. If this `group_by` is refused, skip the monthly view and say so |
| P3 | `count_transactions` | last year's span, `state=settled` | Year-on-year growth |

**Subscriptions (if live subscriptions > 0):**

| # | Tool | Arguments | Gives |
|---|---|---|---|
| B1 | `get_subscription_revenue` | `state=active`, `group_by=plan`, `group_limit=5` | MRR now and the top 5 plans |
| B2 | `get_subscription_revenue` | `created_from=Jan 1`, `created_to`, `state=active` | MRR from subscriptions started this year |
| B3 | `count_subscriptions` | `created_from`, `created_to` | New subscriptions this year |
| B4 | `count_subscriptions` | `ended_from`, `ended_to` | Subscriptions that ended this year |

**Customers (always):**

| # | Tool | Arguments | Gives |
|---|---|---|---|
| C1 | `count_customers` | `created_from`, `created_to` | New customers this year |

## 3. Output

```
## {Account name}: {year} in review
(as of {as_of})

### Headlines
- {CUR} {volume} processed across {n} payments ({±x}% vs {last year})
- {n} new customers · {m} new subscriptions
- MRR {CUR} {x}, of which {CUR} {y} from subscriptions started this year
- Best month: {month} ({CUR} {amount})
- Most-used payment method: {method} ({x}% of payments)

### Payments by method
| Method | Payments | Volume | Share |

### Top plans
| Plan | MRR | Share |

### Month by month (if available)
```

## 4. Shareable version (offer, don't assume)

Ask: "Want a short LinkedIn-ready version? I can use percentages instead of exact amounts if you'd rather not share revenue."

Draft 4–6 lines: the growth percentages, customer milestones and best month, written in the first person plural ("We…"), with no customer names. The merchant posts it themselves. Never include customer data or exact revenue unless the merchant explicitly says to.
