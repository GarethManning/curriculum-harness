"""Reference-authoring pipeline entry point.

Sequences: inventory → KUD classifier → quality gates → output.

Usage:

    python -m curriculum_harness.reference_authoring.pipeline.run_pipeline \\
        --snapshot docs/run-snapshots/<session>-<source-slug>/ \\
        --out docs/reference-corpus/<source-slug>/

The orchestration body is wired in Step 5.
"""

from __future__ import annotations
