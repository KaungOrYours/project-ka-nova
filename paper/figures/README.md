# Figures

Source for Figures 1 to 4 of Access-2026-37966, rebuilt 2026-11-25 in response
to Reviewer 1, concern 6.

## What concern 6 asked for

> "Several figures are of insufficient quality for an IEEE journal and some
> graphical elements appear highly stylized or synthetic... regenerated
> directly from the underlying data/model as publication-quality vector or
> high-resolution graphics. Fonts, labels, symbols, line weights, and overall
> graphical style should also be made consistent."

## How this directory answers it

**Vector.** Every figure is TikZ compiled to PDF. There is no raster element in
any of them, at any zoom.

**Consistency is structural, not maintained by eye.** All four figures
`\input{kanova-figstyle}` and none defines a local colour, font or line width.
Changing a line weight in that one file changes it in all four. The style file
permits exactly three line weights and one arrow-tip shape across the whole set.

**Greyscale safe.** IEEE Access prints in colour but is widely read in
greyscale. Civilian and military elements in Figure 3 are separated by fill
lightness *and* border dash pattern, never by hue alone, so the distinction
survives a monochrome printer.

**Width.** All four are inside IEEE Access's 182 mm double-column measure, so
none needs downscaling at typesetting time and figure text stays at its
designed size.

| figure | file | size |
|---|---|---|
| 1 | `fig1_architecture.pdf` | 172.1 x 108.8 mm |
| 2 | `fig2_annual_sequence.pdf` | 146.2 x 87.0 mm |
| 3 | `fig3_elite_chains.pdf` | 158.1 x 146.9 mm |
| 4 | `fig4_cves_pipeline.pdf` | 175.3 x 105.9 mm |

## Provenance, for the concern 7 disclosure

**No generative AI was used to produce any figure in this directory.** Each is
hand-authored TikZ source, and the source is in this repository and readable.
This is the point of the format: a reviewer can diff the drawing against the
code it depicts, which is not possible with an exported bitmap.

Concern 6 noted that elements "appear highly stylized or synthetic". The
original Figures 1 to 4 were schematics authored in a drawing tool; they were
stylised, which is what the reviewer saw. They were not AI generated.

## What each figure asserts, and where that was verified

Every figure carries a header comment naming the file and line it was checked
against on 2026-11-25. Summary:

- **Figure 1**, architecture. Roster from `config/scenario_registry.py`;
  external-vector counts read back through `engine/external_layer.py`'s
  `EXTERNAL_LAYER_REGISTRY` rather than transcribed.
- **Figure 2**, the annual sequence. `model_phase3.py` `step()`, lines 542-643.
- **Figure 3**, the elite chains. `CHAIN_ORDER_CIVILIAN` and
  `CHAIN_ORDER_MILITARY` in `engine/elite_agents_v3.py`; country titles read
  back through `AGENT_DISPLAY_NAMES_BY_SCENARIO`.
- **Figure 4**, CVES. Layer entry points in `engine/cves.py`; call sites and
  cadence in `engine/elite_agents_v3.py`.

## Four corrections these figures carry

These are not restylings. The redrawn figures state something different from
the submitted ones, and each difference is a correction the manuscript body
must match.

1. **Figure 2 is a ten-step sequence, not nine.** The submitted caption said
   nine. The live method runs steps 0 to 9 plus the year increment.
2. **Figure 2 step 7 now includes the constitutional court.** At submission the
   judicial layer was never called; it was dead code. It is now executed every
   year (`model_phase3.py:628`). This is new behaviour, not a redrawn label.
3. **Figure 3 no longer rests on Scenario A.** The submitted figure showed the
   chain "under Scenario A (civilian)". Scenario A is the self-designed
   constitution and is dropped from the reported roster. The figure now shows
   South Korea 1987 against Pakistan 1973 with the 8th Amendment, two real
   enacted constitutions, which is where the differential-constraint claim now
   lives.
4. **Figure 1 does not say "eleven external vectors".** That constant is in the
   submitted manuscript and is wrong. The count is per country and is 17 for
   Myanmar: SK 9, DE 9, TH 11, CL 11, PK 12, MM 17.

## Deliberately absent

**Figure 3 carries no interception or emission counts.** The only figures
available are smoke-test lower bounds produced on superseded code. The figure
asserts the mechanism, which is structural; magnitudes belong in a table the
campaign will populate. Do not add counts to this figure from smoke-test data.

## Building

```
./build.sh          # build all four, report page sizes
./build.sh clean    # remove build artefacts, keep the PDFs
```

Requires `pdflatex` with TikZ. It does **not** require `ieeeaccess.cls`, since
each figure is a `standalone` document. That class must be obtained from the
IEEE Author Center to build the manuscript itself.

## Still outstanding

Figures 5 to 8 are data figures and are blocked on the campaign. `charts/
visualize.py` now reads `results_phase3/`, so it can see Phase 3 data, but its
output has not been brought up to the standard in this directory.
