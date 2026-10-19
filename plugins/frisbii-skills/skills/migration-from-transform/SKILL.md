---
name: migration-from-transform
description: Guides Frisbii Transform customers through moving to Frisbii Billing. Covers a step-by-step migration plan, concept mapping, a readiness checklist, and a post-migration check that compares the merchant's Transform totals (customers, subscriptions per plan, recurring revenue) with what Frisbii Billing now holds. Use when a merchant mentions migrating or moving from Frisbii Transform to Frisbii Billing, a migration checklist, or checking that a migration is complete. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# migration-from-transform

**Product:** Billing, for Frisbii Transform customers.
**Featured:** week 13 (18 Jan 2027). Starts a Q1 migration mini-series.
**Call budget:** none for the guidance parts. 2 pre-flight calls + 5–7 calls for the post-migration check.

> **Content owner:** the migration specifics below (steps, mapping, what Frisbii support handles) are a draft. Frisbii's migration team must review them before release.

## Before you start

Apply **frisbii-core** first for any data calls. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` before the first data call. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. The skill never creates plans, customers or subscriptions. Setup happens in the Frisbii dashboard, by import, or with Frisbii's migration team.

The MCP only sees the **Frisbii Billing** side. Transform data comes from the merchant, as a summary or an export file they upload.

## 1. Find out where they are

Ask one question: "Are you planning the move, partway through, or checking a finished migration?" Then go to section 2, 3 or 4.

## 2. Planning: the migration plan

Walk through these phases. Tailor them to what the merchant says about their setup:

1. **Inventory (Transform).** Plans and price points, add-ons, discounts and coupons, number of customers and active subscriptions, billing cycles and renewal dates, payment methods in use, dunning settings, integrations (webhooks, accounting, CRM).
2. **Map concepts** to Frisbii Billing: plans, add-ons, discounts (templates) and coupons (codes), customers, subscriptions, dunning plans. Note anything with no direct equivalent and raise it with Frisbii early.
3. **Payment methods.** Stored cards and mandates usually move through a secure token migration run by Frisbii and the payment providers, not by export. Plan for it with Frisbii support. Never ask the merchant to send card data.
4. **Build the catalogue** in Frisbii Billing (dashboard or with Frisbii): plans, add-ons, discounts, coupons, dunning plans.
5. **Test** with a handful of customers, then compare totals (section 4).
6. **Cut over:** time it to avoid renewal peaks. Freeze changes in Transform. Import customers and subscriptions with the correct next renewal dates so nobody is double-charged or skipped.
7. **Verify and decommission:** run the post-migration check, then switch off billing in Transform.

Offer a checklist the merchant can copy, with an owner and a date per phase.

## 3. In progress: readiness check (5 calls)

| # | Tool | Arguments | Checks |
|---|---|---|---|
| 1 | `list_plans` | `plan_state=active`, `limit=100` (fallback: `get_plan` per known handle if empty) | Catalogue exists. Amounts, currency and intervals match Transform |
| 2 | `list_addons` | `addon_state=active`, `limit=100` | Add-ons exist |
| 3 | `list_coupons` | `state=active`, `limit=100` | Coupons carried over |
| 4 | `list_discounts` | `limit=100` | Discount values match |
| 5 | `list_dunning_plans` | – | A default dunning plan exists, with sensible retries |

Show it as a checklist (✅ / ⚠ / ⛔) against the merchant's Transform inventory.

## 4. Finished: post-migration check (5–7 calls)

Ask the merchant for their Transform totals (or an export): customers, active subscriptions per plan, and MRR per plan or in total.

| # | Tool | Arguments | Compare with Transform |
|---|---|---|---|
| 1 | `count_customers` | `state=active` | Customer count |
| 2 | `count_subscriptions` | `state=active_non_cancelled`, `group_by=plan` | Active subscriptions per plan |
| 3 | `get_subscription_revenue` | `state=active`, `group_by=plan` | MRR per plan |
| 4 | `count_subscriptions` | `state=pending` | Subscriptions created but not activated (often import leftovers) |
| 5 | `count_customers` | `min_active_subscriptions=1` | Customers who actually have a live subscription |
| 6 (optional) | `list_subscriptions` | `plan_handle`, `limit=20` | Spot-check next renewal dates on one plan |

Output a side-by-side table (Transform | Frisbii Billing | Difference | Status), with differences above 1% flagged. Explain likely causes: customers without subscriptions, pending imports, plan mapping, currency or VAT treatment. Point the merchant to the Frisbii migration team for any data fixes.
