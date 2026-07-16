# Publication Checklist

Do not describe CCAF as publicly disseminated until the following steps are complete.

- [ ] Publish the repository under the author's account with the Apache-2.0 license.
- [ ] Confirm that no client, employer, production, or identifying data is present.
- [ ] Run `python -m unittest discover -s tests -v` and retain the successful output.
- [ ] Run `python run_all.py --regenerate` and confirm the generated audit artifacts.
- [ ] Confirm that the GitHub Actions test workflow passes on the release commit.
- [ ] Create a signed or otherwise identifiable `v1.3.0` release.
- [ ] Record the repository URL, release URL, and commit hash in the methodology PDF.
- [ ] Archive the release with a permanent identifier if available.
- [ ] Ask independent reviewers to evaluate the released version, not an unpublished draft.
- [ ] Preserve authentic reviewer correspondence and any public issue or discussion history.

After publication, replace the release-status statement in the PDF with the permanent repository and release identifiers. Do not claim adoption, use, validation, or impact unless independently documented.
