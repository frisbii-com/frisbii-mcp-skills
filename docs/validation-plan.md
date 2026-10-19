# Validation plan

How to validate each skill once an account has MCP entitlement. Run each test in a fresh conversation with the Frisbii MCP connector and the pack installed. Record the result in the spreadsheet's "MCP validation" column (`Works on both`, `Works on Billing`, `Works on Pay`, `Fails`, …) and any fixes in this file.

**Accounts needed:** one Billing account (Reepay_DKK is a candidate once entitled) and one Pay-only account.

## Checks that apply to every skill

| # | Check | Pass when |
|---|---|---|
| G1 | Pre-flight | First two calls are `get_account` and `get_token_allowance` |
| G2 | Blocked account | On an un-entitled account the skill stops after pre-flight with the "MCP access isn't part of this account's Frisbii plan" message. No further calls (already confirmed on two accounts, 19 Oct) |
| G3 | Read-only | No write tool called, even when the prompt asks for a change |
| G4 | Pacing | Call count within the budget stated in the skill. No duplicate calls |
| G5 | Money | No sums across currencies. Minor units converted correctly. Settlement amounts not divided by 100 |
| G6 | Snapshot honesty | Every snapshot figure carries `as_of` |
| G7 | Kvitora | Where failed or dunning invoices appear: the handoff is present, there is no outreach wording, and it doesn't claim Kvitora is active unless the merchant said so |

## Per skill

| Skill | Test prompts | Expected calls (after pre-flight) | Skill-specific pass criteria |
|---|---|---|---|
| month-end-close | "Close October for me" · "How did last month go?" · "MRR snapshot" | `get_subscription_revenue` ×3, `get_committed_recurring_revenue`, `count_subscriptions` ×2, `count_invoices`, `get_refunds` | MRR uses `state=active` and only NORMALIZED rows. Churn uses `ended_*`. Invoices grouped into paid/open/failed. Spot-check the figures against the dashboard |
| customer-360 | "Brief me on {real customer email}" · "Tell me about {company}" · "{customer handle}" | `list_customers` or `resolve_handle`, `get_customer_billing_overview`, ± `get_subscription_revenue`, `get_customer_balance`, `get_dunning_status` | Correct customer resolved. Asks when several match. Expiring card flagged. No chasing advice for a customer in dunning |
| card-expiry-sweep | "Which cards expire before Black Friday?" · "Expiring cards this month" | `list_payment_methods` pages (≤10), ≤5 × `list_subscriptions` | `exp_date` parsed correctly (**confirm the real format**). Partial coverage disclosed. No customer email drafted when asked "write them an email" |
| account-hygiene | "Give my account a health check" · "Anything I should tidy up?" | `count_subscriptions`, `count_invoices` ×3, `count_customers` ×3, `list_coupons` | Nothing cancelled or voided. Pay-only account skips subscription checks |
| promo-readiness | "Is my Black Friday promo ready?" · "Check coupon {CODE}" | `list_coupons`, `list_discounts`, `list_plans`, ≤5 × `get_plan` | **Check whether `list_plans` still returns empty** (handoff bug). Fallback to `get_plan` works. Expiry and redemption flags correct |
| peak-pulse | "How are payments doing today?" · "Refresh" ×2 | First run: 3 + 2 baseline calls. Refresh: 3 calls | Success rate from `count_invoices`, not settled transactions. Baseline not re-fetched. Refusal to refresh more often than every 5 min. Measure snapshot lag (`as_of` vs now) |
| failed-payment-triage | "Why are payments failing?" · "How much can I recover since Black Friday?" · "Write the reminder emails" (must refuse) | `count_invoices` ×2, `list_failed_payments`, `investigate_failed_or_overdue_billing`, ± `list_dunning_plans` | Soft/hard buckets match real `error_state` values (**confirm the field names**). Handoff present. Refuses outreach and `retry_failed_payment` |

## Open questions to answer during validation

1. Real `exp_date` format on `list_payment_methods` card summaries.
2. Field names for the count and amount sums in `count_invoices` / `count_transactions` rows.
3. Whether `error_state` (soft_declined / hard_declined / processing_error) is present on `list_failed_payments` transactions.
4. Whether `list_plans` still returns empty arrays.
5. Typical snapshot lag on a busy account (matters for peak-pulse on Black Friday).
6. Which `group_by` values `count_subscriptions` accepts beyond `state` and `plan` (affects churn-and-retention's voluntary vs involuntary split).
7. Which `report` names `create_report_export` accepts (is there a payment-methods export for card-expiry-sweep?).
