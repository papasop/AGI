# Lost-artifact recovery

The original `global_parameterization.json` and the raw 80/160-step result
directories were not recoverable from the available workspace or Library.
This package regenerates them from the frozen standalone programs; it does not
replace them with transcribed or synthetic data.

## One command

From the extracted package directory:

```bash
python rebuild_all_artifacts.py
```

The driver:

1. runs the complete v1.3.1 formal response-curve audit;
2. checks the canonical parameterization SHA-256 against
   `e8ad8a6fbcab626b726082b570f59df6854d4a28259177783e1f5e3274b1cb84`;
3. reconstructs and validates the 80-step curve;
4. reconstructs and validates the 160-step curve;
5. creates `recovered_artifacts/Geometric-Flow-ready-v0.2.3.zip`.

Every stage is fail-closed. A hash or scientific-gate mismatch stops packaging.
Completed valid stages are reused after an interruption. Use `--force` only
when you intentionally want to recompute everything.

## Colab

Upload and extract this ZIP, change into its directory, then run:

```python
!python rebuild_all_artifacts.py
```

The formal v1.3.1 stage is the expensive part. Depending on the Colab machine,
the complete reconstruction can take roughly 1.5–2 hours.

## Expected canonical hashes

| Artifact | SHA-256 |
|---|---|
| v1.3.1 global parameterization | `e8ad8a6fbcab626b726082b570f59df6854d4a28259177783e1f5e3274b1cb84` |
| 80-step reconstructed curve | `c05e1184d6e8e0b603f6a73323957f300291d02a78fdd950f920f0a1dc383063` |
| 160-step reconstructed curve | `b63827b54311e895a2089610575601a5c79fa43d66ddd40f9cccfb1f37c9d670` |

The 80/160-step outputs remain floating-point reconstruction evidence. They
are not a validated ODE theorem.
