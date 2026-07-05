# LaTeX Report

This folder contains an Overleaf-ready visual report generated from the analysis
CSV outputs.

## Generate

Run from the repository root:

```powershell
python analysis/generate_latex_report.py
```

The generator reads:

- `analysis/out/bridge-analysis-overview.csv`
- `analysis/out/topology-three-mode-comparison.csv`

and writes:

- `analysis/latex/main.tex`
- `analysis/latex/sigrok-pylon-bms-capture-analysis.pdf` after local compile

## Overleaf

Upload `analysis/latex/main.tex` as the main document. It is self-contained and
does not require the CSV files on Overleaf.

## Local Compile

If a LaTeX distribution is installed:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=analysis/latex/build analysis/latex/main.tex
```

Build outputs are ignored by git. The final compiled report is copied into
`analysis/latex/sigrok-pylon-bms-capture-analysis.pdf` and committed for easy
review from the repository.
