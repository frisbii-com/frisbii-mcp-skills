---
name: peak-pulse
description: Near-live pulse of payments and sign-ups during a peak such as Black Friday or Cyber Monday. Shows settled payment volume by payment method, payment success vs failure for the day, new subscriptions, and how today compares with a normal day, with as few calls as possible. Use when a merchant asks "how is Black Friday going", "how are payments doing today", for a live view, or to refresh the peak numbers. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# peak-pulse

**Product:** Pay. The sign-up view also covers Billing.
**Featured:** week 5 (23 Nov 2026, Black Friday). Used heavily 27–30 Nov.
**Call budget:** 2 pre-flight calls (once) + 3 calls per refresh, about 1 minute. A baseline adds 2 calls, once.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies. Always quote `as_of`.

**This is near-live, not live.** The figures come from snapshots that usually lag by a few minutes. Show `as_of` prominently and never call it "real time".

## 1. Window

- Default: **today**, from 00:00 in the account timezone, to tomorrow's date as the exclusive `*_to`.
- The merchant may ask for "since Friday" or "the whole weekend". Use that window instead.

## 2. Calls per refresh

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `count_transactions` | `settled_from`, `settled_to`, `group_by=payment_type` | Settled payment count and amount by method |
| 2 | `count_invoices` | `created_from`, `created_to`, `group_by=state` | Payment outcomes for invoices raised in the window: settled vs failed/dunning vs pending |
| 3 | `count_subscriptions` | `created_from`, `created_to` | New subscriptions (skip if the account has no subscriptions) |

Success rate = settled ÷ (settled + failed + dunning) from call 2. Leave pending and authorized invoices out of the rate and show them as "in progress". A transaction filtered by settlement date excludes failures by definition, so never compute a success rate from call 1.

## 3. Baseline (first run only)

Repeat calls 1 and 2 for the **same weekday one week earlier**, to compare with a normal day. Skip if the merchant says no or the call budget is tight. Reuse the baseline on later refreshes; never re-fetch it.

## 4. Refreshing

- When the merchant asks to refresh, run calls 1–3 again only. Never re-run pre-flight or the baseline.
- Don't refresh more than once every 5 minutes. If asked sooner, say the snapshot probably hasn't moved and give its `as_of`.
- Show what changed since the last refresh.

## 5. Output

```
## Peak pulse: {date}, as of {as_of HH:MM} ({timezone})
**{CUR} {settled amount}** settled from {n} payments · success rate **{x}%** · {m} new subscriptions

| Method | Payments | Settled | vs last {weekday} |
| CARD | | | |
| MOBILEPAY_SUBSCRIPTIONS | | | |

Invoice outcomes today: settled {n} · failed/in recovery {n} · in progress {n}
Since last refresh ({HH:MM}): +{n} payments, +{CUR}
```

- If the success rate is 5+ points below the baseline, flag it plainly: "Success rate is below a normal {weekday}." Point to failed-payment-triage after the peak. Don't diagnose during the pulse.
- If failed/in-recovery > 0, add a one-line Kvitora mention (frisbii-core `references/kvitora-handoff.md`, short form).
