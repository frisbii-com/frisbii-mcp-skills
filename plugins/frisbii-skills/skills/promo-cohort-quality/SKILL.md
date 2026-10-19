---
name: promo-cohort-quality
description: Compares subscribers acquired with a discount (e.g. a Black Friday coupon) against full-price subscribers who joined in the same window. Shows how many are still active, how many have already ended, and the recurring revenue the cohort brings. Use when a merchant asks "were my Black Friday customers worth the discount", "did promo sign-ups stick", how a coupon cohort performs, or discounted vs full-price retention. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# promo-cohort-quality

**Product:** Billing. Also works for Pay merchants running subscriptions on Pay.
**Featured:** week 7 (7 Dec 2026, post-BFCM). Early read in December. Repeat in February for a fuller picture.
**Call budget:** 2 pre-flight calls + 6–8 calls, about 3 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies. Always quote `as_of`.

## 1. Define the cohort

- **Window:** default Black Friday to Cyber Monday plus one day (`created_from=2026-11-27`, `created_to=2026-12-01`). Use the merchant's dates if given.
- **Promo discounts:** ask which coupon codes were the promo. Default: every coupon redeemed in the window. Call `list_coupons` (`state=active`, `limit=100`) to map coupon codes to discount handles.
- Say upfront: "It's {n} days since the promo, so this is an early read. Most cancellations show up after the first renewal."

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `list_coupons` | `state=active`, `limit=100` (or `code=` per promo code) | Promo coupon to discount handle mapping, redemption counts |
| 2 | `count_subscriptions` | `created_from`, `created_to`, `group_by=state` | All subscriptions created in the window, by state |
| 3 | `count_subscription_discounts` | `subscription_created_from`, `subscription_created_to`, `discount_handle` (promo) | Discounted subscriptions created in the window |
| 4 | same as 3 | + `subscription_state=active` | …of which still active |
| 5 | same as 3 | + `subscription_state=expired` | …of which already ended |
| 6 | `get_subscription_revenue` | `created_from`, `created_to`, `state=active` | MRR of the whole cohort still active |
| 7 (optional) | `count_subscriptions` | same length window, 4 weeks earlier, `group_by=state` | A non-promo baseline cohort |

With more than one promo discount, repeat calls 3–5 for at most 2 discounts. Otherwise drop `discount_handle` to cover all discounts.

## 3. Derive

- **Full-price cohort** = total from call 2 − discounted total from call 3. Still active and ended likewise (call 2 `active` + `cancelled` rows vs call 4; call 2 `expired` vs call 5).
- `count_subscription_discounts` counts **applications**, not subscriptions. A subscription with two discounts counts twice. Say so if more than one promo discount applies, since the split is then approximate.
- **Retention so far** = still active ÷ total, per cohort. `state=cancelled` means still active but a cancellation is scheduled. Show those separately as "leaving".
- MRR can't be split by discount from the snapshot. Show the cohort total. If the merchant wants the split, offer `create_report_export` with `report=subscription_discounts`.

## 4. Output

```
## Promo cohort: {window} · early read, {n} days in
| Cohort | Joined | Still active | Leaving (cancellation scheduled) | Already ended | Retention so far |
| Discounted ({codes}) | | | | | x% |
| Full price | | | | | y% |
| Baseline (4 weeks earlier, optional) | | | | | z% |

Cohort MRR still active: {CUR} {x} (as of {as_of})
Coupon redemptions: {code}: {n} of {limit}
```

Then 2–3 plain-language takeaways, e.g. "Discounted sign-ups are ending 2× faster than full-price ones so far". Caveat the early read, and suggest re-running after the first renewal date.
