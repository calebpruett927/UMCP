# Build Instructions

## Requirements
- TeXLive with REVTeX 4.2, `amsmath`, `amssymb`, `physics`, `microtype`, `hyperref`, `booktabs`.
- The main source: `collapse_calculus_revtex_frontmatter.tex` (or your merged file).

## Compile
```bash
pdflatex collapse_calculus_revtex_frontmatter.tex
bibtex   collapse_calculus_revtex_frontmatter   # if you add a .bib
pdflatex collapse_calculus_revtex_frontmatter.tex
pdflatex collapse_calculus_revtex_frontmatter.tex
```

## Include the frozen tables
In the body (e.g., after `\maketitle`):
```latex
\input{MANIFEST_TABLE.tex}
\input{CHANNELS_AB_TABLE.tex}
```

## Replacing the manifest snapshot
- Update `compiled_manifest.json` and re-export `MANIFEST_TABLE.tex` if any key changes.
