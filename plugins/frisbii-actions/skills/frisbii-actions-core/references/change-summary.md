# Change summary

End every action run with this block, filled in from the write responses. Don't make extra calls for it.

> **Changes made** ({account name}, {date and time, account timezone})
>
> | # | Object | Change | Result |
> |---|---|---|---|
> | 1 | {type} `{handle}` | {before} → {after} | ✅ done / ⛔ failed: {error} / – not attempted |
>
> **To undo:** {one line per reversible change, e.g. "Coupon `bf-2026` can be expired in the Frisbii dashboard" or "Run dunning-tuning again with the previous schedule [3, 7, 14]"}. {Name any irreversible changes: "Charges and voided invoices cannot be undone."}

Rules:
- Keep the previous values of everything that was updated in the table. They are what the merchant needs to undo the change.
- If nothing was changed (the merchant declined, or nothing was eligible), say so in one line and skip the table.
- Leave customer personal data (email, phone, address) out of the table. Use customer handles.
