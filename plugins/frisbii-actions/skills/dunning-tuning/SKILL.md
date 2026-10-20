---
name: dunning-tuning
description: Changes a Frisbii dunning plan's retry schedule, grace period or final action (put on hold, expire or nothing) after showing the current settings, the proposed ones and why, and getting the merchant's confirmation. Keeps the old settings so the change can be undone. Use when a merchant asks to change retry timing, add or remove retries, set a grace period, or change what happens when dunning fails. Changes data. Uses the Frisbii Billing & Pay MCP server.
---

# dunning-tuning

**Product:** Pay and Billing.
**Call budget:** 2 pre-flight calls + 2–3 reads + 1 write per dunning plan, about 2 minutes.
**Writes:** `update_dunning_plan` only.

## Before you start

Apply **frisbii-actions-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Read the current state first, show every change as a numbered plan, and write only after the merchant replies **confirm** to that plan. At most 10 writes per confirmation, one at a time, about 20 seconds apart.
- Stop on the first failed write and never retry a write automatically.
- Use only the write tools listed under **Writes**. Never create or delete dunning plans, and never change which plan is the default unless the merchant asks for exactly that.

## 1. Current settings

| # | Tool | Arguments | Gives |
|---|---|---|---|
| 1 | `list_dunning_plans` | – | Every dunning plan: `schedule` (days between retries), `grace_period`, `no_grace_hard_decline`, `final_subscription_action`, `default_plan` |
| 2 | `count_invoices` | `dunning_invoices=true` | How many invoices are in dunning now, and their amounts per currency |
| 3 (optional) | `investigate_dunning_invoices` | `limit=50` | Where those invoices sit (dunning step, next retry) |

If **dunning-review** (read-only pack) ran earlier in the conversation, use its recovery rate and its suggestions as the starting point.

## 2. Proposing a change

Explain each change in one line. Guidance:

- **Schedule**: a list of intervals in days, e.g. `[3, 5, 7]` = retries 3, 8 and 15 days after the first failure. Spread retries over 2–4 weeks; retrying every day mostly re-declines and can annoy customers. Soft declines (insufficient funds) often clear around paydays, so a retry 5–10 days in helps.
- **Grace period**: an ISO-8601 duration before dunning starts, e.g. `P3D` for 3 days. Keep `no_grace_hard_decline=true` (the default), so hard declines skip the grace period and the customer is asked for a new card sooner.
- **Final action**: `on_hold` pauses the subscription and keeps the customer easy to win back; `expire` ends it; `none` leaves it running with the invoice unpaid. Changing this changes what happens to real customers at the end of dunning, so say that plainly.

Don't propose more than the merchant asked for. If they asked only to "add one more retry", change only the schedule.

## 3. Plan

`update_dunning_plan` **replaces the whole plan**: any field left out is cleared. The payload must contain `name`, `schedule`, `default_plan` and `final_subscription_action`, plus `grace_period` and `no_grace_hard_decline` copied from the current plan unless they are being changed.

| Field | Now | New |
|---|---|---|
| name | Standard | Standard |
| schedule | [1, 1, 1] | [3, 5, 7] |
| grace_period | – | – |
| no_grace_hard_decline | true | true |
| final_subscription_action | expire | on_hold |
| default_plan | true | true |

Say: "This applies to every plan and subscription that uses this dunning plan ({n} invoices are in dunning now). Invoices already in dunning may move to the new schedule." Mark the change **Reversible**: the old values above restore it. Ask for **confirm**.

## 4. After

Show the change summary with the full old settings. Suggest running **dunning-review** in 4–6 weeks to see whether recovery improved.
