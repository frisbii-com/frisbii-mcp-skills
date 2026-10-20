---
name: account-cleanup
description: Tidies up a Frisbii account: voids stale unpaid draft and pending invoices and cancels subscriptions stuck in pending that never started, after listing every item and getting the merchant's confirmation. Never touches settled invoices or live subscriptions, and leaves customer debts (failed or dunning invoices) alone unless the merchant names them one by one. Use when a merchant asks to clean up old invoices, void draft or duplicate invoices, remove stuck pending subscriptions, or act on an account health check. Changes data. Uses the Frisbii Billing & Pay MCP server.
---

# account-cleanup

**Product:** Billing and Pay.
**Call budget:** 2 pre-flight calls + 4 reads + 1 write per item (up to 10 per batch), about 6–8 minutes for a full batch.
**Writes:** `void_invoice`, `cancel_subscription`.

## Before you start

Apply **frisbii-actions-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Read the current state first, show every change as a numbered plan, and write only after the merchant replies **confirm** to that plan. At most 10 writes per confirmation, one at a time, about 20 seconds apart.
- Stop on the first failed write and never retry a write automatically.
- Use only the write tools listed under **Writes**. Never refund, never delete customers, never touch active subscriptions.

**Voiding is irreversible.** A voided invoice can't be reopened; to bill again, a new invoice is needed.

## 1. Find candidates

Default age threshold: **60 days** (ask the merchant if they want another).

| # | Tool | Arguments | Finds |
|---|---|---|---|
| 1 | `count_invoices` | `group_by=state` | How many invoices sit in each state, to size the job |
| 2 | `list_invoices` | `state=created`, `due_to` = today − 60 days, `limit=20` | Old draft invoices never sent for payment |
| 3 | `list_invoices` | `state=pending`, `due_to` = today − 60 days, `limit=20` | Old pending invoices with no settlement |
| 4 | `list_subscriptions` | `state=pending`, `created_to` = today − 60 days, `limit=20` | Subscriptions created but never activated |

If the merchant ran **account-hygiene** (read-only pack) earlier in the conversation, start from its findings instead.

## 2. Eligibility

**Invoices** (void):
- State `created`, `pending` or `unfinalized`, older than the threshold, `settled_amount` 0.
- **Not** `settled`, `authorized`, `credited` or `cancelled`. A paid invoice needs a refund, which this skill doesn't do.
- `failed` and `dunning` invoices are money the customer owes. Leave them out by default. Void one only if the merchant names that invoice and confirms it should be written off; list it on its own row marked "write-off".
- If the invoice belongs to a subscription that is still live, flag it and leave it out unless the merchant confirms.

**Subscriptions** (cancel):
- State `pending`, created before the threshold. Check with `get_subscription` that it has no settled invoices.
- Use `cancel_subscription` with an empty `payload` (`{}`). If Frisbii refuses to cancel a pending subscription, report it and leave it for the dashboard. Don't try another tool.
- Never cancel `active`, `on_hold` or `cancelled` subscriptions here.

## 3. Plan

| # | Object | Customer | State, age | Amount | Change | Reversible? |
|---|---|---|---|---|---|---|
| 1 | Invoice `inv-208` | `cust-12` | created, due 2026-06-02 | EUR 49.00 (4900) | Void | **Irreversible** |
| 2 | Subscription `sub-77` | `cust-40` | pending since 2026-05-11 | – | Cancel | **Irreversible** |

Show how many more candidates exist beyond this batch. Ask for **confirm**.

## 4. After

Show the change summary. Suggest running **account-hygiene** again later to confirm the account is clean.
