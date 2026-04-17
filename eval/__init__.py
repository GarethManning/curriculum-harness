"""Judge-side evaluation utilities.

Anything in this package is a *judge* — code that reads pipeline output
and tests whether it matches its primary-source artefact. Judges are
separate from the harness (`kaku_decomposer/`). Session rule:
harness code changes never live here; judge code changes never live
in the harness.
"""
