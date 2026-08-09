# Apply guide — post-publication C4 extension

Base repository: `papasop/Geometric-Flow`, latest `main` at application time.

This ZIP is an overlay containing only new paths. It intentionally does not
contain or replace:

- published manuscript/PDF/source archives;
- `src/` published theorem code;
- `reproduce/published_paper.py`;
- frozen reference certificates;
- `README.md`, `CITATION.cff`, `CHANGELOG.md`; or
- the repository-wide `SHA256SUMS.txt`.

Apply on a new branch from current `main`:

```bash
unzip geometric-flow-c4-control-extension.zip -d /tmp/c4-overlay
cp -R /tmp/c4-overlay/. .
python -m compileall -q research/control_extension/c4
python research/control_extension/c4/verify_c4_control_extension.py \
  --d0 results/post_publication/control_extension/c4/c4_d0_product_chart_residence_preflight_v1_0.json \
  --d1 results/post_publication/control_extension/c4/c4_d1_arb_product_tube_residence_v1_0.json
python tools/verify_release.py
python scripts/verify_reference_results.py
python reproduce/published_paper.py
sha256sum -c SHA256SUMS.txt
```

Because the existing release manifest checks only its listed frozen files,
leaving `SHA256SUMS.txt` unchanged preserves the exact published release
boundary. New C4 files are covered by `CONTROL_EXTENSION_SHA256SUMS.txt`.

Recommended branch: `codex/c4-controlled-attraction-extension`

Recommended commit message:

```text
Add post-publication C4 finite-residence certificate
```

