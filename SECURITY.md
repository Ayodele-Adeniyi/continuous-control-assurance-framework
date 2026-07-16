# Security and Data Handling

CCAF is a reference implementation, not a production security service. Do not place credentials, secrets, personal information, client records, employer records, or production extracts in a public repository, issue, pull request, or test fixture.

## Responsible reporting

Report a suspected security issue privately to the repository maintainer through GitHub's private vulnerability-reporting feature when it is enabled. Do not open a public issue containing exploit details, credentials, or sensitive data.

## Production use

An institution considering operational use must independently address authorization, privacy, secure transfer, encryption, access control, retention, environment segregation, dependency management, source completeness and accuracy, configuration approval, monitoring, exception handling, and remediation governance.

The bundled synthetic data is safe for public demonstration. The presence of a file hash proves file identity after extraction; it does not prove that an extract was complete, accurate, authorized, or correctly filtered.
