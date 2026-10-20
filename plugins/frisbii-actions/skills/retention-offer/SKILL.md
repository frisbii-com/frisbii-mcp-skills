---
name: retention-offer
description: Applies a retention offer to Frisbii subscriptions at risk of cancelling: puts an existing coupon on the subscription, pauses it instead of losing the customer, or resumes a paused subscription, after previewing the effect on each subscription and getting the merchant's confirmation. Use when a merchant asks to give a customer a discount to stay, apply a coupon to a subscription, pause a subscription instead of cancelling, or resume a paused one. Changes data. Uses the Frisbii Billing & Pay MCP server.
---

# retention-offer

**Product:** Billing.
**Call budget:** 2 pre-flight calls + 2–3 reads per subscription + 1 write per subscription, about 2 minutes for one customer.
**Writes:** `apply_coupon`, `pause_subscription`, `resume_subscription`.

## Before you start

Apply **frisbii-actions-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Read the current state first, show every change as a numbered plan, and write only after the merchant replies **confirm** to that plan. At most 10 writes per confirmation, one at a time, about 20 seconds apart.
- Stop on the first failed write and never retry a write automatically.
- Use only the write tools listed under **Writes**. Never cancel a subscription; cancellations stay in the Frisbii dashboard. Never create coupons here (that is **promo-setup**).

## 1. Which subscriptions

- One customer: `get_customer_billing_overview` with `customer_handle` to find their subscriptions. Ask which one if there are several live ones.
- A list (for example the at-risk list from **churn-and-retention**): take up to 10 subscription handles per batch.

For each subscription, `get_subscription` with `handle`. Note `state`, plan, next billing date, and any `coupons` / `subscription_discounts` already on it.

## 2. Which offer

| Offer | When it fits | Tool |
|---|---|---|
| **Coupon** | Price is the reason. The merchant has (or creates with promo-setup) a coupon for this | `apply_coupon` with `subscription_handle`, `payload.code` |
| **Pause** | The customer needs a break (season, budget, holiday) | `pause_subscription` with `subscription_handle`, `payload.compensation_method` |
| **Resume** | A paused subscription should start billing again | `resume_subscription` with `subscription_handle` (optional `payload.start_date`) |

### Coupon checks
- `get_coupon` (or `list_coupons` with `code`): the coupon is `active`, `valid_until` is in the future, redemptions are below `max_redemptions`, and the subscription's plan is eligible (`all_plans` or in `eligible_plans`). Read the coupon's discount with `get_discount` so the plan can show the value.
- **Only one coupon can be active per subscription. Applying a new one replaces the existing one.** If the subscription already has a discount, show it in the plan and ask whether replacing it is intended.
- If the customer is in dunning (`get_dunning_status`), say so: a discount doesn't fix a failed card. Suggest **failed-payment-recovery** or a card update first.

### Pause checks
- Only `active` subscriptions can be paused. Billing stops immediately and no invoices are created while it is on hold.
- `compensation_method` defaults to `none` (no refund or credit for the rest of the current period). Only use `prorated_credit`, `full_credit`, `prorated_refund` or `full_refund` if the merchant asks, and show the effect. Refunds only work for card-like methods.
- The tool sets no automatic resume date. Tell the merchant the subscription stays paused until it is resumed (with this skill or in the dashboard), and offer to note the intended resume date in the summary.

### Resume checks
- Only `on_hold` subscriptions can be resumed. Billing restarts from the next billing cycle, or from `start_date` if given. A `start_date` in the past can create invoices for past periods; avoid it unless the merchant asks.

## 3. Plan

| # | Subscription | Customer | Now | Change | Effect | Reversible? |
|---|---|---|---|---|---|---|
| 1 | `sub-311` | `cust-88` | Pro Monthly DKK 299.00, no discount | Apply coupon `STAY20` (20% off next 3 invoices) | Next invoice DKK 239.20 | Yes: remove the discount in the dashboard |
| 2 | `sub-412` | `cust-91` | Active, renews 2026-11-01 | Pause, no compensation | Billing stops now | Yes: resume |

Ask for **confirm**, then execute one at a time.

## 4. After

Show the change summary. Offer to draft a short message to each customer explaining the offer, for the merchant to send. Never send it yourself.
