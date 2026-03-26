# Phase 63 — Claude as SMARTS Filter Designer

**Version:** 1.1 | **Tier:** Standard | **Date:** 2026-03-26

## Goal
Ask Claude to design SMARTS patterns and validate them with RDKit against the compound library.

CLI: `python main.py --input data/compounds.csv`

## Key Concepts
- Claude generates SMARTS as structured output
- RDKit validates via `Chem.MolFromSmarts(pattern)` and `mol.HasSubstructMatch()`
- Tests whether LLMs can produce executable cheminformatics code

## Results
| Metric | Value |
|--------|-------|
| Patterns generated | 3 |
| Valid SMARTS | 1/3 |
| Total hits | 0/45 (even valid SMARTS too restrictive) |
| Input tokens | 162 |
| Output tokens | 286 |
| Est. cost | $0.0013 |

## Key Finding
Claude generated syntactically plausible but chemically imprecise SMARTS:
- "Acrylamide warhead" `[C;H1]=[C;H1]C(=O)N` — valid but `[C;H1]` too restrictive (actual C=C has H2/H1)
- "Halogenated aniline" — invalid SMARTS syntax (unmatched bracket)
- "EWG aromatic" — invalid SMARTS (CF3 not valid SMARTS atom)

**Conclusion**: LLMs should not be trusted to generate executable SMARTS without human/RDKit validation. This validates the Phase 57 tool-use pattern where RDKit runs server-side, not as LLM-generated code.
