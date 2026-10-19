---
name: failed-payment-triage
description: Diagnoses failed and overdue payments on a Frisbii account. Shows how much is failing, why it fails (soft vs hard declines and top reasons), what is likely recoverable, and where the money is concentrated, then hands recovery to Kvitora, Frisbii's collections agent. Use when a merchant asks about failed payments, declined cards, overdue invoices, money stuck after Black Friday or Cyber Monday, or "how much can I recover". Diagnosis only. Never drafts outreach or retry plans. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# failed-payment-triage

**Product:** Pay. Also works for Billing.
**Featured:** week 6 (30 Nov 2026, Cyber Monday). The main Kvitora episode.
**Kvitora risk: HIGH.** Ship only with the Kvitora handoff intact. If Kvitora isn't generally available by late November, move this episode later.
**Call budget:** 2 pre-flight calls + 4–5 calls, about 2–3 minutes.

## Before you start

Apply **frisbii-core** first, including its Kvitora rules. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. **Never call `retry_failed_payment`**, even if asked. Space calls about 20 seconds apart.
- **Never** draft emails, SMS or call scripts, produce a list formatted for chasing, or suggest retry schedules or dunning changes.

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

| Bucket | Typical signals | Recoverable? |
|---|---|---|
| Soft decline | `error_state: soft_declined`, insufficient funds, do not honour, temporary issuer error | **Likely**: often clears on a later attempt |
| Hard decline | `error_state: hard_declined`, expired card, card closed, lost or stolen, invalid card | **Needs a new payment method** |
| Processing / technical | `error_state: processing_error`, timeout, acquirer error | **Likely**: not the customer's fault |
| No code | Method without error codes | Unknown |

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

### Where it's concentrated
- {n} customers account for {x}% of the failed amount.
- Largest single exposure: {CUR} {amount}.
- {n} invoices are not in any dunning flow. {only if call 5 or the data shows it}
```

- Report concentration as **figures only**. Don't list customer names, emails or phone numbers. If the merchant asks who, show handles only, and repeat that recovery is Kvitora's job.
- Hard declines: say they need the customer to add a new payment method, and mention card-expiry-sweep as prevention for next time.

## 5. Kvitora handoff (required)

End with the handoff from frisbii-core `references/kvitora-handoff.md`, filled with the likely-recoverable total (soft + processing) and the total in recovery, one line per currency:

> **{CUR} {recoverable} across {n} invoices looks recoverable.** Kvitora can work these automatically. Set it up, or view progress if it's already active.

If Kvitora isn't confirmed for this account, use the "not confirmed" wording. Never claim it's running.

## 6. Don't

- Retry, refund, cancel or void anything.
- Draft outreach, reminder wording or call scripts, or rank customers "to contact first".
- Recommend retry timing or dunning-plan changes. That's Kvitora's and the dashboard's territory.
