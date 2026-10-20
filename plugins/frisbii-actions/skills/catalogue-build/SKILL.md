---
name: catalogue-build
description: Builds a Frisbii Billing product catalogue (subscription plans and add-ons) from a list the merchant provides, such as a Frisbii Transform export, a pasted price list or a description. Maps prices, billing intervals, trials, setup fees and notice periods, checks for handle clashes, previews every plan and add-on, and creates them after the merchant confirms. Use when a merchant asks to create plans or add-ons, set up their catalogue, or rebuild their Transform catalogue in Frisbii Billing. Changes data. Uses the Frisbii Billing & Pay MCP server.
---

# catalogue-build

**Product:** Billing. Often used during a move from Frisbii Transform.
**Call budget:** 2 pre-flight calls + 3 reads + 1 write per plan or add-on (up to 10 per batch), about 5–7 minutes for a batch.
**Writes:** `create_plan`, `create_addon`.

## Before you start

Apply **frisbii-actions-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Read the current state first, show every change as a numbered plan, and write only after the merchant replies **confirm** to that plan. At most 10 writes per confirmation, one at a time, about 20 seconds apart.
- Stop on the first failed write and never retry a write automatically.
- Use only the write tools listed under **Writes**. Never change or delete existing plans; a price change on an existing plan needs a new plan version, which is done in the Frisbii dashboard.

This skill creates catalogue items only. Customers, subscriptions and stored payment methods are moved by Frisbii's migration team, not by this skill. Never ask for card data.

## 1. Gather the catalogue

Accept a Transform export, a pasted table or a description. For each plan, collect:

| Field | Maps to | Notes |
|---|---|---|
| Name | `name` | |
| Handle | `handle` | Lowercase, letters, digits, `-` `_` `.` `@`. Keep the Transform ID in it if the merchant wants traceability, e.g. `pro-monthly` |
| Price | `amount` | **Minor units**: DKK 299.00 → `29900` |
| Price includes VAT? | `amount_incl_vat` | Default `true`. Ask; getting this wrong changes every invoice |
| Currency | `currency` | Default: the account currency from `get_account` |
| Billing interval | `schedule_type` + `interval_length` | Monthly from signup date: `month_startdate`, 1. Quarterly: `month_startdate`, 3. Yearly: `month_startdate`, 12. Fixed day of month: `month_fixedday` + `schedule_fixed_day` (1–28). Weekly: `weekly_fixedday` + `schedule_fixed_day` (1–7) |
| Free trial | `trial_interval_length` + `trial_interval_unit` (`days`/`months`) | |
| Setup fee | `setup_fee` (minor units) | Optional |
| Notice period | `notice_periods` (+ `notice_period_unit_type`) | Optional |
| Minimum term | `fixation_periods` (+ `fixation_period_unit_type`) | Optional |
| Dunning plan | `dunning_plan` | Optional; the default dunning plan is used if left out |

For each add-on: `name`, `handle`, `type` (`on_off` or `quantity`), `amount` (minor units), `amount_incl_vat`, `currency`, and `all_plans=true` or `eligible_plans`.

Anything in the source with no clear equivalent (usage-based pricing, tiered prices, custom proration rules): list it under **Not mapped**, and suggest setting it up in the dashboard or with Frisbii's migration team. Don't guess.

## 2. Check before proposing

| # | Tool | Arguments | Check |
|---|---|---|---|
| 1 | `list_plans` | `limit=100` | No plan handle already exists, in any state. A clash is skipped, not overwritten |
| 2 | `list_addons` | `limit=100` | No add-on handle already exists |
| 3 | `list_dunning_plans` | – | Any `dunning_plan` handle named in the source exists |

Flag: prices of 0, prices that look like major units (e.g. `299` for DKK 299.00), duplicate handles in the source, and add-ons that name plans not in the catalogue.

## 3. Plan

| # | Create | Handle | Price | Interval | Trial / setup / notice | Reversible? |
|---|---|---|---|---|---|---|
| 1 | Plan | `pro-monthly` | DKK 299.00 (29900) incl. VAT | Monthly from signup | 14-day trial | Yes: delete in the dashboard while unused |
| 2 | Add-on (quantity) | `extra-seat` | DKK 49.00 (4900) incl. VAT | With the plan | Eligible: `pro-monthly` | Yes, while unused |

Write order: all plans first, then add-ons (add-ons reference plan handles). At most 10 creations per confirmation. Ask for **confirm**.

## 4. After

Show the change summary. For a Transform move, suggest the readiness check in **migration-from-transform** (read-only pack), which compares the new catalogue with the Transform inventory.
