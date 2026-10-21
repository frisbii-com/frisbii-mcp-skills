---
name: card-expiry-sweep
description: Finds stored customer cards on Frisbii that expire soon, before their next charge or renewal, so the merchant's team can fix them before payments fail. Use when a merchant asks about expiring cards, cards expiring before Black Friday or renewal, "which customers need a new card", or how to prevent failed payments from expired cards. Can draft a card-update message for the merchant to send. Read-only, uses the Frisbii Billing & Pay MCP server.
---

# card-expiry-sweep

**Product:** Pay (cards on file). Also works for Billing merchants.
**Call budget:** 2 pre-flight calls + 1 call for recent failures + 1 call per customer checked (up to 20) + up to 5 renewal checks. About 2–8 minutes.

## Before you start

Apply **frisbii-core** first. If it isn't installed, still follow these minimum rules:
- Call `get_account` and `get_token_allowance` first. Stop on `usage_blocked` or `no_mcp_entitlement`.
- Make no write calls. Space calls about 20 seconds apart.

## 1. Set the horizon

- Default horizon: cards expiring **by the end of next month** (at today's date, end of November 2026). If the merchant names a date ("before Black Friday", "before year end"), use that.
- Card expiry is month-precision: a card marked 11/26 works until the last day of November 2026.
- Tell the merchant the call estimate before paging.

## 2. Collect cards

**What the server allows (validated 20 Oct 2026):** `list_payment_methods` without `customer_handle` only returns cards **created in the last 30 days** (see `extra.window`), and there is no payment-method export. An account-wide sweep of every stored card is therefore not possible. Say so plainly in the output; don't present a partial list as complete. Cards are checked per customer instead:

1. **Which customers.** Use the customers the merchant names (key accounts, a list from customer-360 or their CRM), up to 20. If they name none, ask once. Without names, run only step 3 and offer to check key accounts.
2. **Per customer:** `list_payment_methods` with `customer_handle` (covers all time). Keep rows where `state` is `active` and a card summary with `exp_date` is present. Non-card methods (offline bank transfer, MobilePay, etc.) don't expire; count them separately.
3. **Recent expired-card failures (account-wide, reactive):** `list_failed_payments` with `limit=50`. Count failures whose `card_transaction` shows an expired card or a hard decline. These are customers whose card has already failed; list them as "already failing" (about the last month, per `extra.window`).

- `exp_date` comes as `MM-YY` (e.g. `06-27` = June 2027). Parse `MM/YY` and `YYYY-MM` too, in case. If a value can't be parsed, count it as "unknown expiry".
- A card can be `active` and already past its expiry date. Treat it as **already expired**.
- Bucket each card: **already expired** · **expires this month** · **expires within horizon** · later.

## 3. Check renewals (optional, top 5 only)

For up to 5 flagged cards, call `list_subscriptions` with `customer_handle` and `state=active_non_cancelled`. Compare each card's expiry with the subscription's next renewal date, and mark cards that expire **before** the next renewal as highest priority. Skip this step for Pay-only accounts with no subscriptions.

## 4. Output

```
## Expiring cards: {account name}
Checked {n} active stored cards for {k} customers on {date}. An account-wide check of every stored card isn't available from the Frisbii MCP server.

**Summary**
- Already expired but still stored as active: {n}
- Expire this month: {n}
- Expire by {horizon}: {n}
- Non-card methods (don't expire): {n}
- Already failing with an expired or hard-declined card (last month, account-wide): {n}

### Cards expiring by {horizon}
| Customer | Card | Expires | Next renewal (if checked) |
(top 25 by soonest expiry; offer the rest as an export or a follow-up)
```

- Show the customer handle and the masked card (brand, last 4) only. No email or phone unless the merchant asks about a specific customer.
- Close with: "Expiring cards are the most common cause of future failed payments. Want me to draft a short card-update message you can send to these customers?" If yes, follow the customer-message rules in frisbii-core `references/recovery-next-steps.md`. The merchant sends it; the skill never does.

## 5. Don't

- Show card fingerprints or compare cards across customers.
- Present a partial sweep as complete.
