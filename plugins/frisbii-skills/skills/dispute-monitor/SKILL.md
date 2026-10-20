---
name: dispute-monitor
description: Chargeback and dispute overview for a Frisbii account. Shows disputes raised in a period by reason, state and outcome, amounts and fees, disputes still waiting for a response, the dispute rate against settled payments, and a comparison with the previous period. Use when a merchant asks about chargebacks, disputes, "how many chargebacks after Black Friday", dispute rate, or which disputes need a response. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# dispute-monitor

**Product:** Pay. Also works for Billing.
**Call budget:** 2 pre-flight calls + 5 calls, about 2 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units of each row's currency. Never add across currencies. Always quote `as_of`.

## 1. Window

Default: the **last 30 days** by the date the dispute was raised. Post-peak variant: from Black Friday to today. The comparison window is the same length immediately before.

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `count_disputes` | `created_from`, `created_to`, `group_by=reason` | Disputes and amounts by reason |
| 2 | `count_disputes` | `created_from`, `created_to`, `group_by=state,outcome` | Open vs under review vs waiting for a response vs resolved, and outcomes |
| 3 | `count_disputes` | `state=waiting_for_response` (no date filter) | Everything needing the merchant's response now, all time |
| 4 | `count_disputes` | previous window, no `group_by` | Comparison |
| 5 | `count_transactions` | `settled_from`, `settled_to` (same window), `state=settled` | Denominator for the dispute rate |

Notes:
- The MCP gives counts and amounts only, with no per-dispute rows. To act on individual disputes, the merchant opens them in the Frisbii dashboard. Say so.
- An unresolved dispute has no outcome. Show those rows as "pending".
- Outcomes: `merchant_favor` = won. `customer_favor_chargeback` / `customer_favor_refund` = lost. `cancelled_by_customer` = withdrawn. `provider_payout` = covered by the provider.

## 3. Output

```
## Disputes: {window}
**{n} disputes** ({CUR} {amount}) · dispute rate {x}% of settled payments · {±y} vs previous period
**{m} waiting for your response** ({CUR} {amount})

### By reason
| Reason | Disputes | Amount |

### Status and outcomes
| State / outcome | Disputes | Amount | Fees |

Win rate on resolved disputes: {won} of {resolved} ({z}%)
```

Plain-language reason labels: `product_not_received` → "Product not received", `unauthorised` → "Unauthorised / fraud", `cancelled_recurring_billing` → "Charged after cancelling", etc.

Then tailored next steps:
- **Waiting for response > 0:** respond in the Frisbii dashboard before the deadline. Unanswered disputes are usually lost.
- **Mostly `cancelled_recurring_billing`:** check cancellation flows and that renewal reminders go out.
- **Mostly `unauthorised`:** review risk rules. `list_blocked_payments` shows what the risk filters already catch.
- **Mostly `product_not_received`:** check fulfilment times and descriptor clarity.
- A dispute rate approaching 1% of transactions is the zone where card schemes start monitoring. Flag it when close.
