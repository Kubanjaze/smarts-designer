# Phase 63 — Claude as SMARTS Filter Designer

**Version:** 1.1 | **Tier:** Standard | **Date:** 2026-03-26

## Goal
Ask Claude to design SMARTS patterns and validate them with RDKit against the compound library.

CLI: `python main.py --input data/compounds.csv`

## Logic
- Define a prompt asking Claude for 3 specific SMARTS patterns: acrylamide warhead, halogenated aniline, EWG aromatic
- Parse JSON array of `{name, smarts, description}` from Claude's response
- Validate each SMARTS with `Chem.MolFromSmarts(pattern)` — returns None if invalid
- Run valid patterns against all 45 compounds using `mol.HasSubstructMatch()`
- Report: valid count, hit counts per pattern, pattern quality assessment

## Key Concepts
- Claude generates SMARTS as structured output
- RDKit validates via `Chem.MolFromSmarts(pattern)` and `mol.HasSubstructMatch()`
- Tests whether LLMs can produce executable cheminformatics code

## Verification Checklist
- [x] Claude generates 3 SMARTS patterns in JSON format
- [x] RDKit validation attempted for each pattern
- [x] 1/3 valid SMARTS — honest reporting of failures
- [x] 0/45 hits even for valid pattern (too restrictive)
- [x] Key finding documented: LLMs need SMARTS validation

## Risks (materialized)
- Generated SMARTS may be syntactically invalid — 2/3 were invalid (unmatched bracket, invalid atom)
- Valid SMARTS may be too restrictive — confirmed ([C;H1] matcher too narrow)
- This is the expected finding: validates the tool-use pattern (Phase 57) over code generation

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
