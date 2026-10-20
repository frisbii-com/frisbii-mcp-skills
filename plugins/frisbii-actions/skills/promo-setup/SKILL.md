---
name: promo-setup
description: Sets up a Frisbii promotion: creates the discount template and the coupon code, or extends an existing coupon (new end date, higher redemption limit, more eligible plans), after previewing every field and getting the merchant's confirmation. Checks for code clashes and invalid plans first. Use when a merchant asks to create a coupon, set up a Black Friday or campaign discount, make a promo code, or extend or change a coupon. Changes data. Uses the Frisbii Billing & Pay MCP server.
---

# promo-setup

**Product:** Billing.
**Call budget:** 2 pre-flight calls + 3–4 reads + 1–2 writes per coupon, about 3 minutes.
**Writes:** `create_discount`, `create_coupon`, `update_coupon`, and `update_discount` for name and description only.

## Before you start

Apply **frisbii-actions-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Read the current state first, show every change as a numbered plan, and write only after the merchant replies **confirm** to that plan. At most 10 writes per confirmation, one at a time, about 20 seconds apart.
- Stop on the first failed write and never retry a write automatically.
- Use only the write tools listed under **Writes**. Never delete coupons or discounts, and never apply coupons to subscriptions (that is **retention-offer**).

A **discount** is the reusable template (percentage or fixed amount, what it applies to, for how long). A **coupon** is the code customers enter; it points at exactly one discount.

## 1. Gather the promotion

Ask only for what's missing. Suggest defaults and say what you assumed.

| Field | Default | Maps to |
|---|---|---|
| Campaign name | – | discount and coupon `name` |
| Value | – | `percentage` (1–100) **or** `amount` in minor units plus `currency`, never both |
| Applies to | `plan` (the subscription price only) | discount `apply_to`, e.g. `["plan"]` or `["all"]` |
| Duration | Ask: first invoice only, N invoices, N months, or forever | `fixed_count`, or `fixed_period` + `fixed_period_unit`; none = forever |
| Code | – | coupon `code` (case-sensitive, max 100 characters) |
| Plans | Ask: all plans or a list | `all_plans=true`, or `eligible_plans` |
| Ends | Campaign end date | coupon `valid_until` |
| Limit | None | coupon `max_redemptions` |
| Once per | `once_per_customer` | coupon `redemption_strategy` |

Handles: lowercase, letters, digits, `-` and `_`, e.g. `bf-2026-20pct` for the discount and `bf-2026` for the coupon.

## 2. Check before proposing

| # | Tool | Arguments | Check |
|---|---|---|---|
| 1 | `list_coupons` | `code={CODE}` | Code not already in use. If it is, offer to extend that coupon instead (section 4) |
| 2 | `list_discounts` | `limit=100` | Reuse an existing discount with the same value, `apply_to` and duration instead of creating a duplicate |
| 3 | `list_plans` | `plan_state=active`, `limit=100` | Every eligible plan handle exists and is active. If the list is empty, check each handle with `get_plan` |

Flag anything surprising: a percentage above 50%, a fixed amount larger than a plan's price, `apply_to: all` (also discounts setup fees and add-ons), an end date in the past or more than a year away, or no end date and no limit.

## 3. Plan (new promotion)

| # | Action | Details | Reversible? |
|---|---|---|---|
| 1 | Create discount `bf-2026-20pct` | 20% off `plan` lines, first 3 invoices | Yes: can be deleted in the dashboard while no coupon uses it |
| 2 | Create coupon `bf-2026` | Code `BLACKFRIDAY26`, discount `bf-2026-20pct`, plans: `pro-monthly`, `basic-monthly`, valid until 2026-11-30 23:59, max 500, once per customer | Yes: can be expired or deleted in the dashboard |

Write order: the discount first, then the coupon (it needs the discount handle). Skip step 1 when reusing an existing discount.

## 4. Changing an existing coupon or discount

- **Coupon** (`update_coupon`): you can change the name, eligible plans, `max_redemptions` and `valid_until`. The code and the discount cannot change; for that, create a new coupon. Read it with `get_coupon` first and send the full desired state. Omitted fields are cleared, so copy `max_redemptions` and `valid_until` across even when unchanged.
- **Discount** (`update_discount`): only the name and description. A discount's value may already be in use on live subscriptions, so for a different value create a new discount and coupon instead. Read it with `get_discount` and copy every value across.

Show the before → after for every field.

## 5. After

Show the change summary, then suggest running **promo-readiness** (read-only pack) to check the whole promotion end to end.
