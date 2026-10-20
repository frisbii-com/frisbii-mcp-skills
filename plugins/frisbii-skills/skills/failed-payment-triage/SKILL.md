---
name: failed-payment-triage
description: Diagnoses failed and overdue payments on a Frisbii account. Shows how much is failing, why it fails (soft vs hard declines and top reasons), what is likely recoverable, where the money is concentrated, and what to do next. Use when a merchant asks about failed payments, declined cards, overdue invoices, money stuck after Black Friday or Cyber Monday, or "how much can I recover". Read-only, uses the Frisbii Billing & Pay MCP server.
---

# failed-payment-triage

**Product:** Pay. Also works for Billing.
**Call budget:** 2 pre-flight calls + 4–5 calls, about 2–3 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. **Never call `retry_failed_payment`**, even if asked. Point the merchant to the Frisbii dashboard for retries. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies.

## 1. Window

Default: the **last 30 days** by due date. Name the window you used. Peak-week variant: from Black Friday to today.

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `count_invoices` | `due_from`, `due_to`, `group_by=state` | Failed and dunning counts and amounts vs settled (failure rate) |
| 2 | `count_invoices` | `dunning_invoices=true` | Everything currently in the dunning flow, all time |
| 3 | `list_failed_payments` | `limit=100` | Up to 100 recent failed invoices with embedded transactions and error detail (about a one-month window; read `extra.window`) |
| 4 | `investigate_failed_or_overdue_billing` | `due_from`, `due_to` | Overdue and failed invoices with customer, amount, due date, dunning step |
| 5 (optional) | `list_dunning_plans` | – | Whether failed invoices are covered by dunning at all |

If call 3 returns more than 100 rows, classify the first page only and label it a sample: "Reasons based on the 100 most recent failures". For the full set, offer `create_report_export` with `report=open_transactions`, which carries acquirer codes for every outstanding transaction.

## 3. Classify reasons (from call 3)

Read the error detail from `card_transaction` (or the wallet variant) for cards, otherwise from `transaction_error`. Null error fields mean the method gives no codes (e.g. offline bank transfer), not missing data.

| Bucket | Typical signals | Recoverable? | Usual fix |
|---|---|---|---|
| Soft decline | `error_state: soft_declined`, insufficient funds, do not honour, temporary issuer error | **Likely** | Often clears on a later dunning retry |
| Hard decline | `error_state: hard_declined`, expired card, card closed, lost or stolen, invalid card | **Needs a new payment method** | Customer adds a new card or method |
| Processing / technical | `error_state: processing_error`, timeout, acquirer error | **Likely** | Usually clears on retry. If one acquirer or method dominates, raise it with Frisbii support |
| No code | Method without error codes | Unknown | Check the invoice in the dashboard |

Group by bucket, then the top 5 specific reasons (error code or acquirer message) by amount.

## 4. Output

```
## Failed payments: {window}
**{CUR} {amount}** failed or in recovery across {n} invoices ({x}% of invoices due in the window)

| Bucket | Invoices | Amount | Recoverable? |
| Soft decline | | | Likely |
| Hard decline | | | Needs new payment method |
| Processing | | | Likely |
| No code | | | Unknown |

### Top reasons
| Reason | Invoices | Amount |

### Largest exposures
| Customer | Invoices | Amount | Dunning step | Bucket |
(top 10 by amount, from call 4)

### Coverage
- {n} invoices are in dunning; {m} failed invoices are not in any dunning flow.
```

- Show the customer handle in the exposures table. Add name or company only if the merchant asks.
- Failed invoices outside any dunning flow mean nothing retries them automatically. Flag them clearly, and suggest checking which plans lack a dunning plan (call 5).

## 5. Next steps

End with a short, specific list based on what the data showed, for example:
- **Hard declines ({n}, {CUR}):** these customers need to add a new payment method. Offer to draft a short card-update message for the merchant to send (frisbii-core `references/recovery-next-steps.md`, customer-message rules). Mention card-expiry-sweep as prevention.
- **Soft declines and processing errors ({n}, {CUR}):** likely to recover through dunning retries. Run dunning-review to see how well the dunning plans recover.
- **Not in dunning ({n}):** assign a dunning plan in the Frisbii dashboard.

## 6. Don't

- Retry, refund, cancel or void anything, or call any write tool.
- Send messages. Drafts are for the merchant to send.
