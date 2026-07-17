-- CCAF Module 2: Change Management & Logging Integrity - reference SQL.
-- Adapt interval, boolean, and timestamp syntax to the target database.
-- CM-06 produces recent and baseline rates for evaluation in the scoring layer.

-- CM-01: change implemented without recorded approval
SELECT change_id, system, category
FROM changes
WHERE approved_by IS NULL OR TRIM(approved_by) = '' OR approved_at IS NULL;

-- CM-02: approver and implementer are the same individual
SELECT change_id, system, approved_by
FROM changes
WHERE approved_by IS NOT NULL AND TRIM(approved_by) <> ''
  AND approved_by = implemented_by;

-- CM-03: emergency change without post-implementation review
SELECT change_id, system, implemented_at
FROM changes
WHERE emergency = TRUE AND pir_completed = FALSE;

-- CM-04: deployment event with no matching change record
SELECT d.deploy_id, d.system, d.deployed_at, d.change_id
FROM deploy_logs d
LEFT JOIN changes c ON c.change_id = d.change_id
WHERE d.change_id IS NULL
   OR TRIM(d.change_id) = ''
   OR c.change_id IS NULL;

-- CM-05: silent log source (no events for 24 hours)
SELECT source_id, system, log_source, last_event_at
FROM log_heartbeats
WHERE last_event_at <= CURRENT_TIMESTAMP - INTERVAL '24' HOUR;

-- CM-06: emergency-change rate, recent window vs baseline (feed to comparison logic).
-- Evaluate only when the recent and baseline minimums are met and the baseline
-- contains at least one emergency change.
SELECT
  AVG(CASE WHEN implemented_at >= CURRENT_DATE - INTERVAL '14' DAY
           THEN CASE WHEN emergency THEN 1.0 ELSE 0.0 END END) AS recent_rate,
  AVG(CASE WHEN implemented_at <  CURRENT_DATE - INTERVAL '14' DAY
           THEN CASE WHEN emergency THEN 1.0 ELSE 0.0 END END) AS baseline_rate
FROM changes;

-- CM-07: implemented change lacks recorded preproduction testing
SELECT change_id, system, category, test_completed, test_approved_by
FROM changes
WHERE test_completed = FALSE
   OR test_approved_by IS NULL
   OR TRIM(test_approved_by) = '';
