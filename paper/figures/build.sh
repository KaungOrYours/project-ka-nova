#!/usr/bin/env bash
# Build every Ka-Nova figure to vector PDF.
#
# Each figure is a standalone document, so this does NOT require
# ieeeaccess.cls, which must be obtained separately from the IEEE Author
# Center and is not redistributable. The manuscript includes the PDFs this
# script produces.
#
# Usage:  ./build.sh          build all
#         ./build.sh clean    remove build artefacts, keep the PDFs
set -euo pipefail
cd "$(dirname "$0")"

FIGS=(fig1_architecture fig2_annual_sequence fig3_elite_chains fig4_cves_pipeline)

if [[ "${1:-}" == "clean" ]]; then
    rm -f ./*.aux ./*.log ./*.out ./*.fls ./*.fdb_latexmk f1.log f2.log f3.log f4.log
    echo "build artefacts removed"
    exit 0
fi

command -v pdflatex >/dev/null || { echo "pdflatex not found" >&2; exit 1; }

for f in "${FIGS[@]}"; do
    printf '%-26s ' "$f"
    if pdflatex -interaction=nonstopmode -halt-on-error "$f.tex" >"$f.buildlog" 2>&1; then
        w=$(pdfinfo "$f.pdf" 2>/dev/null \
             | awk '/Page size/ {printf "%.1f x %.1f mm", $3*25.4/72, $5*25.4/72}')
        [[ -n "$w" ]] || w="size unknown (pdfinfo not installed)"
        echo "OK   $w"
        rm -f "$f.buildlog"
    else
        echo "FAILED, see $f.buildlog"
        exit 1
    fi
done

rm -f ./*.aux ./*.log
echo
echo "IEEE Access column widths: 88.9 mm single, 182 mm double."
