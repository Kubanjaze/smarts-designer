import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse, os, json, re, warnings
warnings.filterwarnings("ignore")
import pandas as pd
from dotenv import load_dotenv
import anthropic
from rdkit import Chem, RDLogger
RDLogger.DisableLog("rdApp.*")

load_dotenv()
os.environ.setdefault("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY", ""))

PROMPT = """Design 3 SMARTS patterns for filtering a CETP inhibitor compound library.
The library contains acrylamide-linked aniline derivatives with various substituents.

Provide exactly 3 SMARTS patterns as a JSON array:
1. Acrylamide warhead pattern (C=CC(=O)N motif)
2. Halogenated aniline pattern (aniline with F, Cl, or Br)
3. Electron-withdrawing group on aromatic ring (CF3, CN, NO2)

Respond ONLY with JSON:
[{"name": "...", "smarts": "...", "description": "..."}, ...]"""


def validate_and_run(smarts_list, df):
    """Validate SMARTS and run against compounds."""
    results = []
    for item in smarts_list:
        name = item.get("name", "unknown")
        pattern = item.get("smarts", "")
        desc = item.get("description", "")

        smarts_mol = Chem.MolFromSmarts(pattern)
        valid = smarts_mol is not None

        hits = []
        if valid:
            for _, row in df.iterrows():
                mol = Chem.MolFromSmiles(row["smiles"])
                if mol and mol.HasSubstructMatch(smarts_mol):
                    hits.append(row["compound_name"])

        results.append({
            "name": name,
            "smarts": pattern,
            "description": desc,
            "valid": valid,
            "n_hits": len(hits),
            "hits": hits[:10],  # first 10 for brevity
            "total_compounds": len(df),
        })
        tag = "VALID" if valid else "INVALID"
        print(f"  [{tag}] {name:30s} | SMARTS: {pattern:30s} | Hits: {len(hits)}/{len(df)}")

    return results


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input", required=True)
    parser.add_argument("--model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    df = pd.read_csv(args.input)
    client = anthropic.Anthropic()

    print(f"\nPhase 63 — Claude as SMARTS Filter Designer")
    print(f"Model: {args.model} | Compounds: {len(df)}\n")

    response = client.messages.create(
        model=args.model,
        max_tokens=512,
        messages=[{"role": "user", "content": PROMPT}],
    )

    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text = block.text
            break

    print(f"Claude's response:\n{text[:500]}\n")

    # Parse JSON array
    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    smarts_list = []
    if json_match:
        try:
            smarts_list = json.loads(json_match.group())
        except Exception as e:
            print(f"Parse error: {e}")
            return

    print(f"Patterns generated: {len(smarts_list)}\n")

    # Validate and run
    results = validate_and_run(smarts_list, df)

    n_valid = sum(1 for r in results if r["valid"])
    usage = response.usage
    cost = (usage.input_tokens / 1e6 * 0.80) + (usage.output_tokens / 1e6 * 4.0)

    report = (
        f"Phase 63 — Claude as SMARTS Filter Designer\n"
        f"{'='*50}\n"
        f"Model:          {args.model}\n"
        f"Patterns:       {len(smarts_list)}\n"
        f"Valid SMARTS:   {n_valid}/{len(smarts_list)}\n"
        f"Input tokens:   {usage.input_tokens}\n"
        f"Output tokens:  {usage.output_tokens}\n"
        f"Est. cost:      ${cost:.4f}\n"
        f"\nPer-pattern results:\n"
    )
    for r in results:
        report += f"  {r['name']}: {r['n_hits']}/{r['total_compounds']} hits ({'VALID' if r['valid'] else 'INVALID'})\n"

    print(f"\n{report}")

    with open(os.path.join(args.output_dir, "smarts_filters.json"), "w") as f:
        json.dump(results, f, indent=2)
    with open(os.path.join(args.output_dir, "smarts_report.txt"), "w") as f:
        f.write(report)
    print(f"Saved: {args.output_dir}/smarts_filters.json")
    print(f"Saved: {args.output_dir}/smarts_report.txt")
    print("\nDone.")


if __name__ == "__main__":
    main()
