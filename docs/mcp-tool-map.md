# Skill → MCP tool map

Mapped on 19 Oct 2026 from the **live tool schemas** of the connected Frisbii Billing & Pay MCP server, not from historical docs. When the server changes, re-check against the live tool list and update this file.

**Validation status:** none of these mappings has been run against real data yet. The connected test account (`francois-s-company`, `state: test`) returns `usage_blocked / no_mcp_entitlement` for every data tool. Only `get_account` and `get_token_allowance` respond. Next step: get an account with MCP entitlement, one Billing and one Pay, and run each skill.

## What changed vs the handoff assumptions

1. **The server has snapshot `count_*` and revenue tools with `group_by`** (`count_subscriptions`, `count_invoices`, `count_transactions`, `count_disputes`, `count_customers`, `count_open_transactions`, `count_subscription_discounts`, `get_subscription_revenue`, `get_committed_recurring_revenue`, `get_add_on_revenue`, `get_refunds`). One call returns an exact, complete breakdown. This removes most of the rate-limit risk, including for `peak-pulse`.
2. **New-subscription counts:** the live descriptions say to use `count_subscriptions` (with `created_*`) for "how many", not to count rows from `list_subscriptions`. The handoff's `list_subscriptions` + `active_non_cancelled` approach is superseded.
3. **Open item 2 is answered: payout, dispute and payment-method data are exposed.** Payouts: `list_payouts`, `get_payout`, `reconcile_payout_window`, `list_settlements`, `get_settlement_report`. Disputes: `count_disputes` (counts and amounts only, no row-level list). Payment method: `count_transactions group_by=payment_type`. All three proposed Pay skills are feasible.
4. **`plan-performance` may no longer depend on `list_plans`.** `get_subscription_revenue group_by=plan` and `count_subscriptions group_by=plan` give per-plan figures directly. `list_plans` is still needed only for plan names and intervals. Its bug status is untested (blocked account).
5. **Kvitora status is not exposed by the MCP.** Skills can't tell whether Kvitora is active, so the handoff uses "not confirmed" wording (see `frisbii-core/references/kvitora-handoff.md`). A Kvitora status or recovery-metrics tool is a prerequisite for `dunning-review` in its Kvitora-report framing.
6. **Entitlement gating:** `get_token_allowance` reports `blocked` / `no_mcp_entitlement`. `frisbii-core` checks this up front so merchants get a clear message instead of failing tool calls. This also matters for the launch: every merchant in the campaign needs the MCP entitlement on their plan.

## Per skill

Feasibility: ✅ the tools cover it · 🟡 partly, see gap · ⛔ blocked

| Skill | Product | Main tools | Feasibility | Gaps / notes |
|---|---|---|---|---|
| frisbii-core | Both | `get_account`, `get_token_allowance`, `count_subscriptions`, `count_transactions` | ✅ | Pay/Billing detection is a heuristic (live subscriptions vs settled transactions) |
| month-end-close | Billing | `get_subscription_revenue`, `get_committed_recurring_revenue`, `count_subscriptions`, `count_invoices`, `get_refunds` | ✅ | MRR is "as of snapshot", not "at month end". Opening MRR not derivable |
| customer-360 | Both | `get_customer_billing_overview`, `list_customers`, `resolve_handle`, `get_customer_balance`, `get_subscription_revenue`, `get_dunning_status` | ✅ | |
| card-expiry-sweep | Pay | `list_payment_methods` (has `exp_date`), `list_subscriptions` | 🟡 | No expiry filter or count tool, so it means paging every payment method at 3 calls/min. Check whether `create_report_export` offers a payment-method report; otherwise limit to the top N customers by revenue |
| account-hygiene | Both | `count_subscriptions` (`state=pending,on_hold`), `list_customers` (`test` flag), `count_customers` | 🟡 | "Subscription with no payment method" isn't filterable |
| promo-readiness | Billing | `list_coupons state=active`, `list_discounts`, `get_plan`, `list_plans` | ✅ | Plan names need `list_plans` (bug status untested) |
| payment-method-mix | Pay | `count_transactions group_by=payment_type,state`, `count_customers group_by=country` | 🟡 | Transactions can't be grouped by country, so "by market" isn't available. Mix and success rate by method is |
| peak-pulse | Pay | `count_transactions` (settled window, `group_by=payment_type,state`), `count_subscriptions` (created window) | ✅ | Snapshot lag is "typically minutes", so it isn't truly live. Say so in the episode. 2–3 calls per refresh |
| failed-payment-triage | Pay | `count_invoices state=failed/dunning`, `count_open_transactions`, `investigate_failed_or_overdue_billing`, `list_failed_payments`, `create_report_export report=open_transactions` | ✅ | Grouping failures by reason means the export (acquirer codes) or paging `list_failed_payments` (one-month default). Kvitora handoff required |
| dunning-review | Pay | `investigate_dunning_invoices`, `list_dunning_plans`, `count_invoices dunning_invoices=true` | ⛔ | The Kvitora-report framing needs Kvitora recovery metrics, which the MCP doesn't expose |
| payout-reconciliation | Pay | `reconcile_payout_window` (pass `currency`), `list_payouts`, `list_settlements` (major units), `get_settlement_report` | ✅ | Keep major- and minor-unit sources apart |
| dispute-monitor | Pay | `count_disputes group_by=reason,outcome,state` | ✅ | Aggregates only, no per-dispute rows |
| promo-cohort-quality | Billing | `count_subscription_discounts`, `create_report_export report=subscription_discounts`, `count_subscriptions` | 🟡 | No direct discounted vs full-price filter on `count_subscriptions`. Needs the export joined to subscription state |
| renewal-radar | Billing | `list_subscriptions` (next renewal), `get_plan` (interval), `get_committed_recurring_revenue` | 🟡 | No renewal-date filter, so it pages subscriptions per annual plan |
| year-in-review | Both | `count_transactions` (year, `group_by=payment_type`), `get_subscription_revenue`, `count_subscriptions`, `count_customers` | ✅ | |
| board-pack | Billing | as month-end-close over a quarter, plus `count_customers`, `get_add_on_revenue` | ✅ | |
| churn-and-retention | Billing | `count_subscriptions ended_*`, `get_subscription_revenue ended_*`, `get_committed_recurring_revenue` | 🟡 | The voluntary vs involuntary split (`expire_reason=dunning`) isn't a count filter. Check `group_by` options or the export. Kvitora handoff required |
| migration-from-transform | Billing | `get_account`, `count_*` for a post-migration check | 🟡 | Mostly guidance content. The MCP has no Transform-side data |
| plan-performance | Billing | `get_subscription_revenue group_by=plan`, `count_subscriptions group_by=plan,state`, `count_subscription_discounts` | ✅ (likely) | No longer blocked by `list_plans` except for display names |
