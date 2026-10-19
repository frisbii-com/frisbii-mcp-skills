---
name: card-expiry-sweep
description: Finds stored customer cards on Frisbii that expire soon, before their next charge or renewal, so the merchant's team can fix them before payments fail. Use when a merchant asks about expiring cards, cards expiring before Black Friday or renewal, "which customers need a new card", or how to prevent failed payments from expired cards. Can draft a card-update message for the merchant to send. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# card-expiry-sweep

**Product:** Pay (cards on file). Also works for Billing merchants.
**Featured:** week 3 (9 Nov 2026, Black Friday prep #1). Refresher in week 8.
**Call budget:** 2 pre-flight calls + 1 call per 100 stored cards (capped at 10 pages) + up to 5 renewal checks. About 2–6 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.

## 1. Set the horizon

- Default horizon: cards expiring **by the end of next month** (at today's date, end of November 2026). If the merchant names a date ("before Black Friday", "before year end"), use that.
- Card expiry is month-precision: a card marked 11/26 works until the last day of November 2026.
- Tell the merchant the call estimate before paging.

## 2. Collect cards

The MCP has no expiry filter and no count tool for payment methods, so page through `list_payment_methods`:

- Pass `limit=100`. Follow `next_page_token`.
- **Stop after 10 pages (about 1,000 methods)** and say coverage was partial: "Checked the first 1,000 stored payment methods. Ask me to continue for the rest."
- Keep only rows where `state` is `active` and a card summary with `exp_date` is present. Non-card methods (MobilePay, SEPA, etc.) don't expire, so count them separately.
- `exp_date` may come as `MM-YY`, `MM/YY` or `YYYY-MM`. Parse all three. If a value can't be parsed, count it as "unknown expiry".
- Bucket each card: **already expired** · **expires this month** · **expires within horizon** · later.

## 3. Check renewals (optional, top 5 only)

For up to 5 flagged cards, call `list_subscriptions` with `customer_handle` and `state=active_non_cancelled`. Compare each card's expiry with the subscription's next renewal date, and mark cards that expire **before** the next renewal as highest priority. Skip this step for Pay-only accounts with no subscriptions.

## 4. Output

```
## Expiring cards: {account name}
Checked {n} active stored cards ({coverage: all | first 1,000}) on {date}.

**Summary**
- Already expired but still stored as active: {n}
- Expire this month: {n}
- Expire by {horizon}: {n}
- Non-card methods (don't expire): {n}

### Cards expiring by {horizon}
| Customer | Card | Expires | Next renewal (if checked) |
(top 25 by soonest expiry; offer the rest as an export or a follow-up)
```

- Show the customer handle and the masked card (brand, last 4) only. No email or phone unless the merchant asks about a specific customer.
- Close with: "Expiring cards are the most common cause of future failed payments. Want me to draft a short card-update message you can send to these customers?" If yes, follow the customer-message rules in frisbii-core `references/recovery-next-steps.md`. The merchant sends it; the skill never does.

## 5. Don't

- Show card fingerprints or compare cards across customers.
- Present a partial sweep as complete.
