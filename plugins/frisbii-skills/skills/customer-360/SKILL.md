---
name: customer-360
description: One-page briefing on a single Frisbii customer before a call or meeting. Covers profile, subscriptions and plan, recurring revenue, invoice and payment history, outstanding balance or credit, stored payment methods and card expiry, and overdue or dunning status. Use when a merchant asks "tell me about customer X", "brief me on X before my call", "what's going on with this account", or pastes a customer handle, email or company name. Works for Frisbii Pay and Billing. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# customer-360

**Product:** Both (Pay and Billing).
**Call budget:** 2 pre-flight calls + 2–5 lookup calls, about 1–2 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies.

## 1. Find the customer

Use the first rule that matches what the merchant gave you:

| Merchant gave | Call |
|---|---|
| An exact handle (`cust-0042`) | Go straight to step 2. If that returns `not_found`, try `resolve_handle`. |
| An email address | `list_customers` with `email=` (exact match) |
| A company name | `list_customers` with `company=` (substring), `limit=10` |
| A person's name | `list_customers` with `customer_name=` (substring), `limit=10` |
| An invoice, subscription or charge handle | `resolve_handle`, then use its customer |

If more than one customer matches, list up to 10 (handle, name, company, country, created) and ask which one. Don't fetch all of them.
If none match, say so. Suggest a different spelling or the exact email.

## 2. Core lookup (1 call)

`get_customer_billing_overview` with `customer_handle`. This returns:
- the profile
- **all** subscriptions, in every state
- `open_invoices` (pending, dunning, failed)
- `recent_invoices` (never overlaps open_invoices)
- payment methods, in every state, including deleted ones. Only `state=active` methods can be charged.

For most briefings this one call is enough.

## 3. Add-ons (only when relevant)

| When | Call |
|---|---|
| The customer has any active subscription | `get_subscription_revenue` with `customer_handle`, `state=active`: their recurring revenue, normalised monthly |
| You need outstanding debt or credit balance | `get_customer_balance` with `handle`. Debt = pending + dunning + failed amounts. Credit = `pending_credit_amount` / `transferred_credit_amount`. There is no single "balance" figure. |
| `open_invoices` holds a dunning invoice | `get_dunning_status` with `customer_handle`: dunning step, earliest due date |
| The merchant asks why a payment failed | `list_failed_payments` with `customer_handle` (covers all time when scoped to a customer) |

Don't call `get_subscription`, `get_invoice` or `list_charges` unless the merchant asks about one specific item.

## 4. Card expiry

For each active card payment method, compare its expiry date with the next renewal date of each live subscription. Flag it when the card expires **before** the next renewal: "Card ending 4242 expires 11/26, before the 1 Dec renewal." Offer to draft a short "please update your card" message for the merchant to send.

## 5. Output

```
## {Name / Company} ({handle})
{country} · customer since {created} · {email if the merchant asked for contact details}

**At a glance**
- Status: {Live subscriber | Former subscriber | No subscriptions} · MRR {CUR x}
- Open invoices: {n} ({CUR}) · In recovery: {yes/no}
- Payment method: {type, masked, exp} {⚠ expires before next renewal}

### Subscriptions
| Plan | State | Started | Next renewal / Ended | Monthly |

### Invoices
Open:   | Invoice | Due | Amount | State |
Recent (last 5): | Invoice | Date | Amount | State |

### Payment methods
| Type | Card / account | Expiry | State |

### Notes
- Credit on account, scheduled cancellations, trials ending, deleted customer, etc.
```

Rules:
- Show at most 5 recent invoices and say if more exist.
- If the customer has a `deleted` timestamp, say so at the top.
- Give scheduled cancellations their own line ("Cancellation requested on X, ends on Y").
- If open invoices include `dunning` or `failed`, end with the single-customer **recovery next steps** from frisbii-core `references/recovery-next-steps.md`.

## 6. Don't

- Show card fingerprints, or compare cards across customers. That's fraud tooling and out of scope here.
- Make any write call, even when the merchant asks ("update their email"). Point them to the Frisbii dashboard.
