-- CCAF Module 3: Transaction Reconciliation & Payment Anomaly - reference SQL.
-- Adapt interval, boolean, and timestamp syntax to the target database.
-- TR-04 assumes an institution-maintained business_calendar table.
-- TR-05 produces feature counts; the robust z-score is applied in Python.

-- TR-01: due ledger item with no processor settlement record.
-- Add the institution-approved settlement grace period to the ledger filter.
SELECT l.txn_id, l.account_id, l.amount
FROM ledger l
LEFT JOIN processor_settlement p ON p.txn_id = l.txn_id
WHERE p.txn_id IS NULL;

-- TR-02: amount mismatch beyond tolerance (0.01)
SELECT l.txn_id, l.amount AS ledger_amount, p.settle_amount
FROM ledger l
JOIN processor_settlement p ON p.txn_id = l.txn_id
WHERE ABS(l.amount - p.settle_amount) > 0.01;

-- TR-03: duplicate transaction identifier
SELECT txn_id, COUNT(*) AS postings, MAX(amount) AS amount
FROM ledger
GROUP BY txn_id
HAVING COUNT(*) > 1;

-- TR-04: unreconciled item aged beyond 5 business days
SELECT txn_id, account_id, amount, booked_at
FROM ledger l
WHERE l.reconciled = FALSE
  AND (
    SELECT COUNT(*)
    FROM business_calendar c
    WHERE c.calendar_date >= CAST(l.booked_at AS DATE)
      AND c.calendar_date < CURRENT_DATE
      AND c.is_business_day = TRUE
  ) > 5;

-- TR-05: account velocity, last 14 days (feed to comparison logic).
-- Evaluate only when the institution-approved minimum comparison population is met.
SELECT account_id, COUNT(*) AS txn_count_14d
FROM ledger
WHERE booked_at >= CURRENT_DATE - INTERVAL '14' DAY
GROUP BY account_id
ORDER BY txn_count_14d DESC;

-- TR-06: threshold hovering just below the 10,000 approval limit
SELECT account_id, COUNT(*) AS hover_count
FROM ledger
WHERE amount >= 0.97  * 10000
  AND amount <  0.999 * 10000
GROUP BY account_id
HAVING COUNT(*) >= 3;
