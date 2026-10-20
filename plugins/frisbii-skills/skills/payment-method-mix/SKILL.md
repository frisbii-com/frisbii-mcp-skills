---
name: payment-method-mix
description: Shows how a Frisbii merchant's customers pay. Covers payment-method mix by volume and count (card, MobilePay, bank transfer and others), success vs failure rate per method, outstanding failed payments per method, and where customers are based. Use when a merchant asks about payment methods, card vs MobilePay, which methods fail most, payment success rates by method, or whether to add or promote a method before a peak. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# payment-method-mix

**Product:** Pay. Also works for Billing.
**Call budget:** 2 pre-flight calls + 3–4 calls, about 2 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units of each row's currency. Never add across currencies. Always quote `as_of`.

## 1. Window

Default: the **last 90 days**. Peak variant: the same window as the merchant's last big campaign.

**Why two time bases:** `count_transactions` filters on the **settlement** date, and failed transactions never settle. A period filter therefore shows successful volume only. Success rates and failed payments per method come from an all-time breakdown instead (call 2). Label each figure with its basis. Don't use `count_open_transactions` for failures: validation showed it counts only a handful of open transactions, not failed payments.

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `count_transactions` | `settled_from`, `settled_to`, `state=settled`, `group_by=payment_type` | **Mix for the period:** settled count and volume per method |
| 2 | `count_transactions` | `group_by=payment_type,state` (no dates) | **Success rate per method, all time:** settled vs failed vs other states |
| 3 | `count_customers` | `group_by=country`, `group_limit=10` | Where customers are based |
| 4 (optional) | `count_transactions` | the previous period of the same length, `state=settled`, `group_by=payment_type` | Mix trend |

## 3. Derive

- **Share** per method = method volume ÷ total volume, **within one currency**.
- **Success rate (all time)** = settled ÷ (settled + failed) per method, from call 2. Leave `pending`, `processing`, `authorized` and `cancelled` out of the rate. `refunded` transactions succeeded first, so count them as settled for the rate.
- `payment_type` values: `CARD`, `MOBILEPAY_SUBSCRIPTIONS`, `EMV_TOKEN`, `MANUAL`, `OFFLINE_BANK_TRANSFER`, `OFFLINE_CASH`, `OFFLINE_OTHER`. Use readable labels (`MOBILEPAY_SUBSCRIPTIONS` → "MobilePay Subscriptions", `EMV_TOKEN` → "Wallet / network token").
- **By market:** transactions can't be grouped by country. Show the customer geography from call 4 next to the method mix, and say the cross-tab isn't available. Never invent per-country method shares.

## 4. Output

```
## Payment-method mix: {window}
**{CUR} {volume}** settled across {n} payments · top method {method} ({x}%)

### Mix (settled, {window})
| Method | Payments | Volume | Share | vs previous period |

### Success rate by method (all time)
| Method | Settled | Failed | Success rate |

### Failed payments by method (all time)
| Method | Failed | Failed volume |

### Customers by country (top 10)
| Country | Customers |
```

## 5. Takeaways

Give 2–3 specific points, e.g.:
- One method fails noticeably more than the others → run failed-payment-triage for reasons, and check that method's setup with Frisbii support.
- Customer geography suggests a local method that's missing or under-used (e.g. many Danish customers but little MobilePay) → mention it as an option to discuss with Frisbii.
- Before a peak, the methods carrying most volume are the ones to watch in peak-pulse.
