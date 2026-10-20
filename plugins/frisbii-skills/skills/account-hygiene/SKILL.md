---
name: account-hygiene
description: Housekeeping check of a Frisbii account. Finds subscriptions stuck in pending or on hold, draft invoices never finalised, old invoices still unpaid, customers holding unused credit, active coupons past their useful life, and how many customers have no live subscription. Use when a merchant asks to tidy up their account, for an account health check, about stale or stuck subscriptions, leftover test data, or before a busy period. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# account-hygiene

**Product:** Both. Strongest for Billing.
**Call budget:** 2 pre-flight calls + 7 checks, about 3 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls (no cancelling, voiding or deleting, even when something looks like junk). Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies. Always quote `as_of`.

## 1. Checks (in this order)

| # | Check | Tool and arguments | Flag when |
|---|---|---|---|
| 1 | Subscription states | `count_subscriptions group_by=state` | `pending` or `on_hold` > 0 |
| 2 | Draft invoices | `count_invoices state=unfinalized` | > 0 |
| 3 | Old unpaid invoices | `count_invoices state=pending`, `due_to` = 30 days ago | > 0: due over 30 days ago and still pending |
| 4 | Failed / in-recovery invoices | `count_invoices group_by=state`, `due_to` = 30 days ago (reuse the dunning and failed rows) | > 0 → recovery next steps |
| 5 | Customers holding credit | `count_customers min_credit_balance=1` | > 0 (report `credit_balance_sum` per currency) |
| 6 | Customers with no live subscription | `count_customers state=active`, then `count_customers state=active min_active_subscriptions=1` | Report the difference as "customers without an active subscription". Context, not a problem in itself |
| 7 | Coupons | `list_coupons state=active limit=50` | Valid-until date already passed, or redemptions at the limit |

If the account has no subscriptions (Pay only), skip checks 1 and 6. Say they don't apply.

## 2. Output

```
## Account hygiene: {account name}
Snapshot as of {as_of}.

| Check | Result | What it usually means |
|---|---|---|
| Pending subscriptions | {n} | Created but never activated, often abandoned sign-ups or test data |
| On-hold subscriptions | {n} | Paused; check they are meant to be |
| Draft invoices | {n} | Never finalised, so never sent or charged |
| Pending invoices due 30+ days ago | {n} / {CUR} | Awaiting payment well past due |
| Failed / in recovery (30+ days) | {n} / {CUR} | See recovery note below |
| Customers holding credit | {n} / {CUR} | Credit that will offset future invoices |
| Customers without an active subscription | {n} of {total} | Former or one-off customers |
| Coupons needing attention | {n} | Expired or exhausted but still marked active |
```

Then:
- A short **Suggested clean-up** list for the merchant to do in the Frisbii dashboard, e.g. "Review the 14 pending subscriptions older than 30 days". Don't do any of it.
- To look for leftover test data, offer `list_customers` for the newest customers (the `test` field). Run it only on request.
- If check 4 found failed or dunning invoices, add the **recovery next steps** (frisbii-core `references/recovery-next-steps.md`).

## 3. Don't

- Cancel, void, delete or edit anything.
