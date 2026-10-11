#!/bin/bash
# peek.sh <pdf> <outdir> <dpi> <page> [page...] -> side-by-side PNG of pages for visual review
pdf=$1; out=$2; dpi=$3; shift 3; mkdir -p $out; files=()
for p in "$@"; do pdftoppm -r $dpi -png -f $p -l $p -singlefile "$pdf" $out/pg$p; files+=($out/pg$p.png); done
montage "${files[@]}" -tile ${#files[@]}x -geometry +6+6 -background '#888' $out/peek.png
