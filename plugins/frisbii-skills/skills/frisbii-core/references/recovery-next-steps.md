# Recovery next steps

Use this block at the end of any answer that surfaced failed, dunning or overdue invoices. Fill it from data already fetched. Don't make extra calls just for this block. Show one line per currency.

## Account-level wording

> **Unpaid:** {CUR} {amount} across {n} invoices is failed or in dunning.
> Next steps:
> - Run **failed-payment-triage** to see why these fail and what looks recoverable.
> - Review your dunning plans and retry settings in the Frisbii dashboard (**dunning-review** shows how they perform).
> - For hard declines (expired or closed cards), the customer has to add a new payment method.

Drop any bullet that names the skill already running.

## Single customer (customer-360)

> This customer has {n} overdue invoice(s) totalling {CUR} {amount}{, currently at dunning step {s}}.

Then one line on the likely fix (new payment method needed, or a soft decline that may clear on the next retry). Offer to draft a message to the customer.

## Customer messages

Skills may draft a message to a customer (e.g. "please update your card") **when the merchant asks**. The merchant sends it through their own channel.
- Keep it short, polite and factual. Include the amount and invoice reference only if the merchant wants them.
- Never send anything, and never call a Frisbii write tool (`retry_failed_payment`, `add_payment_method`, …). The pack is read-only.
