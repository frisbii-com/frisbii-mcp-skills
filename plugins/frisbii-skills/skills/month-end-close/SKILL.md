---
name: month-end-close
description: Month-end close report for Frisbii Billing merchants. Shows recurring revenue (MRR) as of the snapshot, new vs churned subscriptions and the MRR they added or removed, invoices raised in the month split into paid, open and failed, and refunds paid out. Use when a merchant asks to close the month, for a month-end summary, an MRR snapshot, "how did October go", or new vs churned subscriptions for a month. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# month-end-close

**Product:** Billing. It also works for Pay merchants running subscriptions on Pay.
**Call budget:** 2 pre-flight calls + 8 report calls, about 3–4 minutes at the rate limit.

## Before you start

Apply **frisbii-core** first: pre-flight, rate-limit pacing, read-only rules, money and date rules, and the recovery next steps. If frisbii-core isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies or VAT treatments. Always quote `as_of`.

## 1. Pick the month

- Default: the current month if today is on or after the 25th, otherwise the previous month. Confirm in one line: "Closing October 2026 (1–31 Oct), Europe/London time. Say if you want a different month."
- Window: `from = first day of the month`, `to = first day of the next month` (`YYYY-MM-DD`).
- Tell the merchant: "This takes about 8 calls, roughly 3 minutes."

If `count_subscriptions` with `state=active_non_cancelled` (run in frisbii-core's detection step, or as the first report call) returns 0, stop. Say the account has no live subscriptions, so a subscription close doesn't apply. For a Pay merchant, offer a payments view instead: settled volume (`count_transactions` with the `settled_*` window, `state=settled`) and refunds.

## 2. Calls (in this order)

| # | Tool | Arguments | Gives you |
|---|---|---|---|
| 1 | `get_subscription_revenue` | `state=active`, `group_by=plan`, `group_limit=10` | Current MRR (`monthly_amount_sum`), top plans |
| 2 | `get_committed_recurring_revenue` | – | Committed MRR vs MRR with a scheduled cancellation |
| 3 | `count_subscriptions` | `created_from`, `created_to`, `group_by=state` | New subscriptions in the month, and which are still live |
| 4 | `get_subscription_revenue` | `created_from`, `created_to`, `state=active` | New MRR still active |
| 5 | `count_subscriptions` | `ended_from`, `ended_to` | Subscriptions that ended in the month (churn) |
| 6 | `get_subscription_revenue` | `ended_from`, `ended_to` | MRR that ended in the month |
| 7 | `count_invoices` | `created_from`, `created_to`, `group_by=state` | Invoices raised in the month, by state, with amounts |
| 8 | `get_refunds` | `refunded_from`, `refunded_to` | Refunds paid out in the month |

Notes:
- Calls 1, 2 and 4 cover the **current** book, as of the snapshot. If the report runs after month end, say "MRR as of {as_of}", not "MRR on 31 Oct". Don't reconstruct opening MRR: upgrades, downgrades and quantity changes aren't visible here.
- Call 6 lifts the `active` default automatically because an end window is given. Check `state_filter` in the response.
- Use only rows with `normalization_status: NORMALIZED` for MRR. List any others below the table with their status.
- Rows are keyed by `currency` (and `vat_treatment` for revenue). Report each combination as its own line. Never total across them.
- If call 1 comes back `truncated`, the total is still exact. Say "top 10 plans shown".

## 3. Invoice states

Group call 7's rows like this:

| Report as | States |
|---|---|
| Paid | `settled` |
| Open (not yet due or awaiting payment) | `created`, `pending`, `authorized` |
| Failed / in recovery | `failed`, `dunning` |
| Cancelled or credited | `cancelled`, `credited` |
| Draft | `unfinalized` (mention only if non-zero) |

The count and amount fields come from the rows. Amounts are minor units of the row's currency.

## 4. Output

```
## Month-end close: {Month YYYY} ({account name})
Window {from}–{last day}, {timezone}. Snapshot as of {earliest as_of}.

**Summary**
- MRR now: {CUR} {x} across {n} revenue lines ({y} committed, {z} with a scheduled cancellation)
- New: {n} subscriptions ({m} still live), +{CUR} new MRR
- Ended: {n} subscriptions, −{CUR} MRR
- Invoices raised: {n}. Paid {CUR}, open {CUR}, failed/in recovery {CUR}
- Refunds paid out: {n}, {CUR}

### Recurring revenue by plan (top 10)
| Plan | Revenue lines | MRR |

### Subscriptions
| | Count | MRR |
| New this month |
|   of which still live |
| Ended this month |
| Net from new minus ended (excludes plan changes) |

### Invoices raised in {Month}
| Status | Count | Amount |

### Refunds
```

Close with:
- A note when `as_of` values are more than an hour apart, and on any non-normalised revenue rows.
- **Recovery next steps** (frisbii-core `references/recovery-next-steps.md`) when failed/in-recovery invoices > 0, using the counts and amounts from call 7.
- An offer: "Want the rows behind any of these? I can export them as a CSV." If the merchant says yes, use `create_report_export` with the same filters, then `get_report_export`. Present the download link labelled with the filename.

## 5. Don't

- Page through `list_subscriptions` or `list_invoices` to count anything.
- Call `count_subscriptions` with `cancelled_*` or `scheduled_end_*` for churn. Use `ended_*`.
- Present `get_subscription_revenue` without a `state` filter as MRR. Unfiltered, it includes every subscription that ever existed.
