---
name: failed-payment-recovery
description: Retries failed Frisbii payments that are likely to succeed (soft declines, or customers who have added a new card since the failure), after showing the merchant each invoice and getting their confirmation. Skips hard declines, recent failures and anything that would just fail again. Use when a merchant asks to retry failed payments, re-run declined charges, recover failed invoices or "try the card again". Changes data: each retry is a real charge attempt. Uses the Frisbii Billing & Pay MCP server.
---

# failed-payment-recovery

**Product:** Pay and Billing.
**Call budget:** 2 pre-flight calls + 2–3 reads + 1 read per candidate customer (up to 10) + 1 write per confirmed retry. A batch of 10 takes about 8–10 minutes.
**Writes:** `retry_failed_payment` only.

## Before you start

Apply **frisbii-actions-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Read the current state first, show every change as a numbered plan, and write only after the merchant replies **confirm** to that plan. At most 10 writes per confirmation, one at a time, about 20 seconds apart.
- Stop on the first failed write and never retry a write automatically.
- Use only the write tools listed under **Writes**. Never refund, charge, or change payment methods.

Every retry **charges the customer now**. It is irreversible. A pointless retry (same expired card, hard decline) can hurt the merchant's standing with card schemes and annoys the customer.

## 1. Find candidates

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `list_failed_payments` | `limit=50` (or `customer_handle` if the merchant named a customer) | Failed invoices with embedded transactions and error detail. Without a customer it covers about the last month; read `extra.window` and say so |
| 2 | `investigate_failed_or_overdue_billing` | `due_from` 60 days ago, `due_to` today | Failed and dunning invoices with dunning step, for invoices outside call 1's window |

If the merchant named specific invoices, use `get_invoice` for each instead.

## 2. Eligibility

Read the decline from `card_transaction` (or the wallet variant) for cards, otherwise from `transaction_error`.

| Rule | Retry? |
|---|---|
| Invoice state is `failed` or `dunning` | Required |
| Last failure is a **soft decline** (`error_state: soft_declined`, insufficient funds, do not honour, temporary issuer or processing error) | Yes |
| Last failure is a **hard decline** (expired card, closed account, lost or stolen, invalid card, fraud suspected) | **No**, unless the customer has added a new active payment method after the failure (see call 3) |
| Last attempt less than 24 hours ago | **No**. Too soon; banks usually decline again |
| Invoice `cancelled`, `settled` or `credited` | No |
| Error fields null (e.g. offline bank transfer) | No. There is nothing to retry automatically |
| Invoice is already in `dunning` and the next automatic retry is within 48 hours | Skip by default and say so. Dunning will retry anyway |

**Call 3, per candidate customer (max 10):** `list_payment_methods` with `customer_handle`. Check there is at least one `active` method. Note whether the newest active method was created **after** the failed attempt.

Take the top 10 eligible invoices by amount. Mention how many more were eligible.

## 3. Plan

| # | Invoice | Customer | Amount | Last failure | Payment method used | Effect |
|---|---|---|---|---|---|---|
| 1 | `inv-1042` | `cust-88` | DKK 499.00 (49900) | Soft decline, insufficient funds, 3 days ago | Existing card •••• 4242 | **Irreversible**: charges now |

- Retry with the existing method: `retry_failed_payment` with `invoice_id` only.
- Customer added a new card after the failure: `retry_failed_payment` with `payload.payment_method="auto"` (the newest active method). Say so in the row.

List the invoices you left out, grouped by reason (hard decline with no new card, too recent, dunning retries soon). For hard declines, offer to draft a "please update your card" message for the merchant to send.

Ask: "Reply **confirm** to retry these {n} payments now. Each one charges the customer immediately."

## 4. Execute and report

One retry at a time, about 20 seconds apart. Read the returned invoice `state`:
- `settled`: recovered.
- `failed` or `dunning`: still failing. Don't retry again in this conversation.
- `pending`: the method settles asynchronously. Say it may take a while.

Stop on the first error response (not on a declined payment; a decline is a normal result). Then show the change summary, with totals recovered per currency, and end with: "Still failing: {n} invoices, {CUR amount}. Customers with hard declines need to add a new payment method."
