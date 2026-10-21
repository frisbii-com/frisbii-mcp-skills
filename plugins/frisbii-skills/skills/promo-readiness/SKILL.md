---
name: promo-readiness
description: Pre-campaign check of Frisbii coupons, discounts and plans before a promotion such as Black Friday or Cyber Monday. Finds coupons that will expire mid-campaign, hit their redemption limit, point at the wrong discount or plans, or carry a surprising discount value. Use when a merchant asks "is my Black Friday promo set up right", to check coupons or discount codes, or for a campaign readiness check. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# promo-readiness

**Product:** Billing. Also works for Pay merchants using coupons on subscriptions.
**Call budget:** 2 pre-flight calls + 3–8 calls, about 2–4 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Never create, update or delete coupons, discounts or plans, even to fix a problem found. Space calls about 20 seconds apart.

## 1. Ask (one message)

- Campaign dates. Default: Black Friday to Cyber Monday, 27–30 Nov 2026.
- Which coupon codes. Default: all active coupons.
- Expected volume, if known (for redemption-limit checks).

## 2. Calls

| # | Tool | Arguments | Purpose |
|---|---|---|---|
| 1 | `list_coupons` | `state=active`, `limit=100` (or `code=` per named coupon) | Coupons, discount handle, redemptions vs limit, validity, eligible plans |
| 2 | `list_discounts` | `limit=100` | Discount values: amount or percentage, currency, state. The tool has no state filter and returns deleted discounts too; ignore `state: deleted` unless a coupon points at one (flag that) |
| 3 | `list_plans` | `plan_state=active`, `limit=100` | Active plans and their currency |
| 4+ | `get_plan` | `handle` (only for plans a coupon names that weren't in call 3, max 5) | Confirms superseded or missing plans |

If `list_plans` comes back empty although the account has subscriptions, it may be the known list_plans issue. Fall back to `get_plan` for each plan the coupons name, and add a note in the output.

## 3. Checks per coupon

| Check | Flag |
|---|---|
| Validity | Valid-until date before the campaign end ⚠, or valid-from date after the campaign start ⚠ |
| Redemptions | Limit set and (limit − redemptions) is below expected volume, or below 10% of the limit ⚠ |
| Discount link | Referenced discount missing or not active ⛔ |
| Discount value | Percentage ≥ 50% or fixed amount ≥ the cheapest eligible plan price ⚠ ("check this is intended") |
| Currency | Fixed-amount discount in a currency different from an eligible plan ⛔ |
| Eligible plans | A named plan is superseded, deleted or missing ⛔. No plan restriction at all: mention it as information |
| Duplicates | Two active coupons with the same code apart from letter case ⚠ (codes are case-sensitive) |

## 4. Output

```
## Promo readiness: {campaign} ({dates})
{n} active coupons checked · {x} ready · {y} warnings · {z} blockers

| Coupon | Discount | Valid | Redemptions | Plans | Status |
| BF2026 | 30% | to 1 Dec | 120 / 500 | 3 plans | ✅ Ready |
| CYBER  | EUR 20 | to 29 Nov | 0 / ∞ | all | ⚠ Expires before Cyber Monday |

### Fix before launch
1. {blocker, with exactly what to change in the Frisbii dashboard}

### Worth a look
- {warnings}
```

End with: "All changes are made in the Frisbii dashboard. This check doesn't change anything."
