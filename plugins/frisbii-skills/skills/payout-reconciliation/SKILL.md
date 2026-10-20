---
name: payout-reconciliation
description: Reconciles Frisbii payouts for a period against what was captured, refunded and charged in fees, so the merchant can match each payout to their bank statement. Lists payouts with bank reference, gross, fees and net, flags failed or pending payouts, and explains timing differences. The Pay equivalent of a month-end close. Use when a merchant asks to reconcile payouts, match bank deposits, "what did Frisbii pay me in October", fees for the month, or payout vs sales differences. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# payout-reconciliation

**Product:** Pay. Also works for Billing.
**Call budget:** 2 pre-flight calls + 3 calls + 1 per payout (max 10), about 2–6 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- **Units differ by tool.** `reconcile_payout_window`, `list_payouts`, `get_payout` and `count_transactions` use **minor units**. `get_settlement_report` and `list_settlements` use **major units** (`amount_units: "major"`). Convert everything to major units before comparing, and never divide settlement amounts by 100.

## 1. Period and currency

- Default: the **previous calendar month**, in the account timezone. Window: `from` = first day, `to` = first day of the next month.
- Currency: the account currency from `get_account`. If the merchant is paid out in several currencies, run once per currency.

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `reconcile_payout_window` | `window_from`, `window_to`, **`currency`** (always) | Payouts paid in the window (full objects) and `total_payout_amount` |
| 2 | `list_payouts` | `payout_state=failed`, `time_range=created`, `created_from`, `created_to`, `currency` | Failed payouts in the period |
| 3 | `list_payouts` | `payout_state=processing`, `currency` | Payouts on their way, not yet paid |
| 4…n | `get_settlement_report` | `payout_handle` per payout from call 1 (max 10, largest first) | Gross, net and every entry (captures, refunds, fees by type) |
| optional | `count_transactions` | `settled_from`, `settled_to`, `state=settled`, `currency` | What was captured in the period, for the timing view |

With more than 10 payouts in the window, report the remaining payouts at net amount only (from call 1) and offer to continue.

## 3. Reconcile

For each payout:
- **Net** (`net_amount`) should equal the payout amount from call 1 (after unit conversion). Flag any difference above 0.01.
- **Gross − fees − refunds = net.** Total the entries by `type`: `capture`, `refund`, and fees (`authorization_fee`, `capture_fee`, `refund_fee`, `payout_fee`, `card_scheme_fee`, `interchange_fee`, `discount_fee`, `fee_other`).
- **Bank reference** (from the payout object) is what appears on the bank statement.

Timing: payments captured near the end of the period are paid out in the next one. If the merchant compares payouts with sales, explain the gap using the optional `count_transactions` figure, not as an error.

## 4. Output

```
## Payout reconciliation: {Month YYYY} ({CUR})
**{n} payouts, {CUR} {total net}** paid · fees {CUR} {x} ({y}% of gross) · refunds {CUR} {z}
{⚠ {m} failed payout(s)} {⏳ {k} payout(s) still processing}

### Payouts
| Paid | Bank reference | Gross | Refunds | Fees | Net | Check |
| 3 Oct | FRSB-123 | 10,250.00 | −120.00 | −182.40 | 9,947.60 | ✅ |

### Fees by type
| Fee | Amount |

### Notes
- Timing differences, payouts not covered, unit conversions done
```

Offer: "Want this as a spreadsheet for your accountant?" If yes, offer `create_report_export` for refunds or settlements where available, or produce a CSV of the table above.

**Failed payouts:** tell the merchant to check their bank details in the Frisbii dashboard and contact Frisbii support. Don't change anything.
