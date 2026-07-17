# Publication Checklist

Public availability is established by the repository and identifiable version tag. The remaining steps strengthen reproducibility, preservation, and independent review; they are not evidence of institutional adoption or operational impact.

- [x] Publish the repository under the author's account with the Apache-2.0 license.
- [x] Confirm that no client, employer, production, or identifying data is present.
- [x] Run `python -m unittest discover -s tests -v` and retain the successful output.
- [x] Run `python run_all.py --regenerate` and confirm the generated audit artifacts.
- [ ] Confirm that the GitHub Actions test workflow passes on the release commit.
- [ ] Create an identifiable annotated `v1.3.1` version tag for the maintenance release.
- [x] Record the final version-tag URL and methodology SHA-256 in the methodology PDF.
- [ ] Archive the release with a permanent identifier if available.
- [ ] Ask independent reviewers to evaluate the released version, not an unpublished draft.
- [ ] Preserve authentic reviewer correspondence and any public issue or discussion history.

Do not claim adoption, institutional use, external validation, or impact unless independently documented.
