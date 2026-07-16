-- CCAF Module 1: Privileged Access - reference SQL patterns.
-- Adapt interval, boolean, and timestamp syntax to the target database.
-- PA-06 produces a feature count; the robust z-score is applied in Python.

-- PA-01: terminated user retains active privileged access
SELECT g.user_id, g.entitlement, u.termination_date
FROM access_grants g
JOIN users u ON u.user_id = g.user_id
WHERE g.grant_status = 'active'
  AND g.privileged = TRUE
  AND u.status = 'terminated';

-- PA-02: privileged grant without recorded approver
SELECT g.grant_id, g.user_id, g.entitlement
FROM access_grants g
WHERE g.privileged = TRUE
  AND (g.approved_by IS NULL OR TRIM(g.approved_by) = '');

-- PA-03: self-approved grant
SELECT g.grant_id, g.user_id, g.entitlement
FROM access_grants g
WHERE g.approved_by = g.user_id;

-- PA-04: dormant privileged account (no authentication in 60 days)
SELECT g.user_id, MAX(a.timestamp) AS last_auth
FROM access_grants g
JOIN users u ON u.user_id = g.user_id AND u.status = 'active'
LEFT JOIN auth_logs a ON a.user_id = g.user_id
WHERE g.privileged = TRUE AND g.grant_status = 'active'
GROUP BY g.user_id
HAVING MAX(a.timestamp) IS NULL
    OR MAX(a.timestamp) < CURRENT_DATE - INTERVAL '60' DAY;

-- PA-05: segregation-of-duties conflict (example toxic pair)
SELECT a.user_id
FROM access_grants a
JOIN access_grants b
  ON a.user_id = b.user_id
WHERE a.grant_status = 'active' AND b.grant_status = 'active'
  AND a.entitlement = 'PAYMENT_INITIATE'
  AND b.entitlement = 'PAYMENT_APPROVE';

-- PA-06: after-hours privileged authentication counts (feed to scoring layer)
SELECT a.user_id, COUNT(*) AS night_logins
FROM auth_logs a
JOIN access_grants g
  ON g.user_id = a.user_id AND g.privileged = TRUE AND g.grant_status = 'active'
WHERE EXTRACT(HOUR FROM a.timestamp) >= 22
   OR EXTRACT(HOUR FROM a.timestamp) < 6
GROUP BY a.user_id
ORDER BY night_logins DESC;

-- PA-07: temporary privileged grant remains active after expiry
SELECT grant_id, user_id, entitlement, expires_at
FROM access_grants
WHERE grant_status = 'active'
  AND privileged = TRUE
  AND temporary = TRUE
  AND expires_at < CURRENT_TIMESTAMP;
