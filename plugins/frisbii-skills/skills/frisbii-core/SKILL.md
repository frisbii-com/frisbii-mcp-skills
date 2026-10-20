---
name: frisbii-core
description: Foundation rules for every Frisbii skill. Use before any Frisbii Billing or Frisbii Pay question answered with the Frisbii Billing & Pay MCP server (subscriptions, invoices, MRR, payments, payouts, customers, disputes). Checks the connection and MCP entitlement, works out whether the account is Pay, Billing or both, paces calls for the rate limit, keeps everything read-only, and formats money and dates consistently. Other Frisbii skills (month-end-close, customer-360, …) depend on it.
---

# frisbii-core

The shared rules for the Frisbii skills pack. Job skills run these steps first and follow these rules throughout. If a merchant asks a Frisbii data question without naming a skill, apply this skill on its own.

Always use the tools the connected Frisbii Billing & Pay MCP server exposes **right now**, with their live descriptions. If a tool's description disagrees with this file or any other document, follow the tool description.

## 1. Pre-flight (once per conversation)

Make these two calls, in this order, before any other Frisbii call:

1. `get_account`: confirms the connection. Note `handle`, `name`, `currency` (account currency), `timezone`, `locale`, `country` and `state`.
   - If `state` is `test`, tell the merchant once: "This is a test account, so the figures are test data."
2. `get_token_allowance`: confirms MCP access.
   - `blocked: true` with `blocked_reason: no_mcp_entitlement` means MCP is not on the merchant's plan. Stop. Say: "MCP access isn't part of this account's Frisbii plan yet. Your account manager can enable it." Don't retry. Don't guess figures.
   - `additional_cap_reached` means the allowance is used up until `period_ends_at`. Stop and give that date.
   - `entitlement_unknown` is temporary. Wait about a minute and try once more.
   - A null `tokens_remaining` means *unknown*, not unlimited.

Any later call that returns `success: false` with `error: usage_blocked` gets the same handling. Stop and explain. Don't loop.

## 2. Pay, Billing or both

Work out which product the merchant uses before choosing what to report. Spend at most two calls on it, and run them only when the job skill needs the answer:

- `count_subscriptions` with `state=active_non_cancelled`. A non-zero count means subscriptions are in use (**Billing**, or Pay running subscriptions).
- `count_transactions` with `state=settled` and a `settled_from` 90 days ago. A non-zero count means payments are flowing.

| Subscriptions | Transactions | Treat as |
|---|---|---|
| > 0 | any | Billing (subscription reports apply) |
| 0 | > 0 | Pay (payments-only reports) |
| 0 | 0 | New or dormant account. Say so and ask what they want to look at. |

If a Billing skill runs on a Pay account that has subscriptions, run it and add one line: "Your account runs subscriptions on Frisbii Pay, so this Billing report covers them."

## 3. Rate limit and call budget

The server allows about **3 calls per minute**.

- Prefer the snapshot tools (`count_*`, `get_subscription_revenue`, `get_committed_recurring_revenue`, `get_add_on_revenue`, `get_refunds`). One call with `group_by` returns a complete, exact breakdown. Never page through a `list_*` tool to count or total something.
- Use `list_*` and `get_*` only for named rows (one customer, one invoice, a top-10 list). Ask for `limit` 10–20 and stop paging once you have what the answer needs.
- Before a multi-call report, tell the merchant roughly how long it takes ("This takes about 8 calls, roughly 3 minutes").
- Space calls about 20 seconds apart. If a call fails with a rate-limit error, wait 60 seconds and retry once. If it fails again, report what you have so far and name what is missing.
- `error: report_pending` ("the report is being computed") means the snapshot report is still building. Wait about a minute and retry once; if it is still pending, skip that figure and say it wasn't ready.
- `error: invalid_group_by` lists the columns the report can group by. Don't retry with a guess; drop the breakdown or use one of the listed columns.
- `list_*` tools return about 10 rows per page whatever `limit` you pass. Follow `next_page_token` only as far as the answer needs.
- Never fire the same call twice to "check". Reuse results you already have in this conversation.

## 4. Read-only

This pack is read-only. Never call a tool that creates, updates, deletes, cancels, pauses, resumes, refunds, retries, voids, charges or applies anything. That includes every `create_*`, `update_*`, `delete_*`, `cancel_*`, `pause_*`, `resume_*`, `refund_*`, `retry_*`, `void_*`, `apply_*`, `remove_*`, `add_payment_method` and `set_default_payment_method` tool. The one exception is `create_report_export`, which only builds a file and changes nothing. Use it only when the merchant asks for the rows behind a figure.

If the merchant asks for a change, explain that this skill only reads data. Point them to the Frisbii dashboard, or to the separate **frisbii-actions** plugin if it is installed (it makes changes only after the merchant confirms each one).

## 5. Failed and overdue payments

1. Whenever an answer surfaces failed, dunning or overdue invoices, end with the recovery next steps in [references/recovery-next-steps.md](references/recovery-next-steps.md).
2. Skills may suggest actions the merchant can take in the Frisbii dashboard, and may draft customer messages when asked. They never send anything or make changes themselves (see section 4).

## 6. Money

- All amounts are **integer minor units** (cents, øre) **except** `list_settlements`, `get_settlement_report` and `get_settlement_entry`, which return **major units** (`amount_units: "major"`). Never divide those by 100.
- Snapshot rows are keyed by `currency`, and the revenue tools also by `vat_treatment`. **Never add amounts across currencies or across VAT treatments.** Show one line per currency, with the account currency first.
- Revenue tools: only rows with `normalization_status: NORMALIZED` have a meaningful `monthly_amount_sum`. Report the other rows separately, with their status.
- `reconcile_payout_window.total_payout_amount` sums across currencies. Always pass `currency`.
- Format money as the ISO code followed by the amount with two decimals and thousands separators, e.g. `EUR 12,480.50`. Use the account `locale` for separators only when the merchant writes in that language.

## 7. Dates and snapshots

- Interpret "this month", "last month" and similar phrases in the account `timezone`. State the exact window you used, e.g. "1–31 October 2026".
- Pass dates as `YYYY-MM-DD`. For a calendar month, send the first day of the month as `*_from` and the first day of the next month as `*_to`. Then read `extra.window` (where returned) and quote the range the server actually applied.
- Snapshot tools return `as_of`. Always show it ("as of 19 Oct 2026, 14:05"). If two figures in one report have `as_of` values more than an hour apart, say so.
- Live (`list_*`/`get_*`) and snapshot (`count_*`) figures can differ slightly. That is expected; don't try to reconcile them.
- `list_failed_payments`, `list_charges`, `list_settlements`, `list_payment_methods` and `investigate_dunning_invoices` default to roughly the **last month** (by creation date) when called without a date filter and without `customer_handle`. Read `extra.window`. Never present those results as all-time figures; use a `count_*` tool for totals.
- Snapshots can lag by **hours**, not minutes (about 1h45m to 3h20m in validation on 20 Oct 2026). Say how old each snapshot is when it matters, e.g. on a busy day.
- Snapshot rows return states in upper case (`ACTIVE`, `SETTLED`, `FAILED`). Treat them the same as the lower-case filter values.
- `count_open_transactions` counts only a few transactions still open on unsettled invoices. It is not a measure of failed payments; use `count_transactions` with `state=failed` or `count_invoices` instead.

## 8. Subscription end dates: pick the right one

- `ended_from`/`ended_to`: the subscription **actually ended**. **Use this for churn.**
- `cancelled_from`/`cancelled_to`: cancellation was **requested** (billing usually continues through the notice period).
- `scheduled_end_from`/`scheduled_end_to`: a diarised end date. Not a churn filter.
- `state=cancelled` means still active with a cancellation scheduled, not ended.

## 9. Output style

- Lead with a 2–4 line summary of the key numbers, then the detail.
- Use tables for breakdowns. Label every figure with what it measures and its source window or `as_of`.
- If a figure couldn't be fetched, write "not available" with the reason. Never estimate it.
- Keep customer personal data (email, phone, address) out of the output unless the merchant asked about that one customer.
