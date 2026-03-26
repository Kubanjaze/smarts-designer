# Phase 63 — Claude as SMARTS Filter Designer

**Version:** 1.0 | **Tier:** Standard | **Date:** 2026-03-26

## Goal
Ask Claude to design SMARTS patterns for filtering compounds by structural features.
Validate the generated SMARTS by running them against our compound library with RDKit.

CLI: `python main.py --input data/compounds.csv`

Outputs: smarts_filters.json, smarts_report.txt

## Logic
- Ask Claude to generate 3 SMARTS patterns: one for acrylamide warheads, one for halogenated anilines, one for electron-withdrawing groups
- Parse the SMARTS from Claude's response
- Validate each SMARTS with RDKit (Chem.MolFromSmarts)
- Run each SMARTS against all 45 compounds, record matches
- Report: valid SMARTS count, hit counts per pattern, overlap analysis

## Key Concepts
- Claude generates SMARTS as structured tool output
- RDKit validates SMARTS via `Chem.MolFromSmarts(pattern)`
- `mol.HasSubstructMatch(smarts_mol)` to check matches
- Demonstrates Claude generating domain-specific code (SMARTS) that gets executed

## Verification Checklist
- [ ] Claude generates valid SMARTS patterns
- [ ] RDKit successfully parses all SMARTS
- [ ] Hit counts reported per pattern
