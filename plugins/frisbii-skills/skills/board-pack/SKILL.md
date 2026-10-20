---
name: board-pack
description: Quarter-end or year-end board summary for a Frisbii Billing merchant. Covers MRR and its movement, committed vs at-risk revenue, new and churned subscriptions, an estimated churn rate, monthly sign-up cohorts, plan mix, add-on revenue, invoiced and collected amounts, and active customers. Formatted as board-ready slides or a one-pager. Use when a merchant asks for a board pack, board update, investor update, QBR numbers, quarterly or year-end summary, or "the board slide". Read-only, uses the Frisbii Billing & Pay MCP server.
---

# board-pack

**Product:** Billing. Also works for Pay merchants running subscriptions on Pay.
**Featured:** week 11 (4 Jan 2027, Q4 / year-end close). Showcase for branded deck output.
**Call budget:** 2 pre-flight calls + about 12 calls, about 5 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.
- Amounts are minor units. Never add across currencies or VAT treatments. Always quote `as_of`.

## 1. Period

Default: the **last completed quarter** (in early January, Q4: 1 Oct–31 Dec). The merchant may choose a year. Window: `from` = first day, `to` = first day after the period. Tell the merchant: "About 12 calls, roughly 5 minutes."

## 2. Calls

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `get_subscription_revenue` | `state=active`, `group_by=plan`, `group_limit=10` | MRR now and plan mix |
| 2 | `get_committed_recurring_revenue` | – | Committed vs already asked to stop |
| 3 | `count_subscriptions` | `state=active_non_cancelled` | Live subscriptions now |
| 4 | `count_subscriptions` | `created_from`, `created_to` | New in the period |
| 5 | `get_subscription_revenue` | `created_from`, `created_to`, `state=active` | New MRR still active |
| 6 | `count_subscriptions` | `ended_from`, `ended_to` | Ended in the period |
| 7 | `get_subscription_revenue` | `ended_from`, `ended_to` | MRR that ended |
| 8–10 | `count_subscriptions` | `created_*` = each month of the period, `group_by=state` | Monthly cohorts: how many from each month are still live |
| 11 | `count_invoices` | `created_from`, `created_to`, `group_by=state` | Invoiced vs settled (collected) vs failed |
| 12 | `get_add_on_revenue` | `settled_from`, `settled_to` | Add-on revenue net of VAT and credits (`adjusted_amount_excl_vat_sum`) |
| 13 (optional) | `count_customers` | `min_active_subscriptions=1` | Paying customers |

## 3. Derived metrics (label each as derived)

- **Net new MRR from new minus ended** = call 5 − call 7. This leaves out upgrades, downgrades and price changes, so label it that way.
- **Estimated live subscriptions at period start** ≈ call 3 − (call 4 subscriptions still live) + call 6.
- **Estimated churn rate** = call 6 ÷ period-start estimate. Show it as "≈ x%", annualised only if the merchant asks.
- **At-risk share** = scheduled-cancellation MRR ÷ active MRR (call 2).
- **Collection rate** = settled amount ÷ invoiced amount (call 11, per currency).

Don't present derived figures as exact, and don't build a forecast. Call 2 is the closest thing to a forward view, and it is not a prediction.

## 4. Output

Ask the format: **slides** (recommended) or a **one-pager**.

**Slides.** If a slides or deck skill is available, such as the company's branded template, use it. Otherwise produce slide-by-slide content:
1. Headline: MRR, net new MRR, live subscriptions, estimated churn, with as_of
2. MRR movement: new vs ended (bar), committed vs at-risk
3. Subscriptions: new, ended, live, cohort table (month × still-live %)
4. Plan mix: top plans by MRR (table or bar)
5. Collections: invoiced, collected, failed. Add-on revenue
6. Notes and definitions: what's derived, snapshot times, currencies

**One-pager.** The same content as a compact markdown report with tables.

If failed invoices are material (> 2% of invoiced), add one line pointing to failed-payment-triage. Keep the pack board-level: no customer names.
