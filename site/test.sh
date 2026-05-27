#!/usr/bin/env bash
set -euo pipefail
SITE="${1:-_site}"
PASS=0 FAIL=0

check() {
  local desc="$1" cond="$2"
  if eval "$cond"; then
    PASS=$((PASS+1))
  else
    FAIL=$((FAIL+1))
    echo "FAIL: $desc"
  fi
}

cd site
npx @11ty/eleventy 2>&1
cd ..

check "index.html exists" "[[ -f $SITE/index.html ]]"
check "facts/602-agencies.html exists" "[[ -f $SITE/facts/602-agencies.html ]]"
check "facts/44-states.html exists" "[[ -f $SITE/facts/44-states.html ]]"
check "facts/70-ice-collaborators.html exists" "[[ -f $SITE/facts/70-ice-collaborators.html ]]"
check "facts/2000-searches.html exists" "[[ -f $SITE/facts/2000-searches.html ]]"
check "facts/107-cross-agency.html exists" "[[ -f $SITE/facts/107-cross-agency.html ]]"
check "facts/nearly-two-thirds.html exists" "[[ -f $SITE/facts/nearly-two-thirds.html ]]"
check "methodology/overview.html exists" "[[ -f $SITE/methodology/overview.html ]]"
check "reproducibility.html exists" "[[ -f $SITE/reproducibility.html ]]"
check "assets/style.css exists" "[[ -f $SITE/assets/style.css ]]"

check "index.html not double-escaped" "! grep -q '&lt;div' $SITE/index.html"
check "602-agencies not double-escaped" "! grep -q '&lt;h1&gt;' $SITE/facts/602-agencies.html"
check "70-ice table not escaped" "! grep -q '&lt;table&gt;' $SITE/facts/70-ice-collaborators.html"

check "602-agencies no p-wrapped tr" "! grep -q '<p><tr>' $SITE/facts/602-agencies.html"
check "70-ice no p-wrapped tr" "! grep -q '<p><tr>' $SITE/facts/70-ice-collaborators.html"

check "index has claim-card" "grep -q 'claim-card' $SITE/index.html"
check "602-agencies shows 602" "grep -q '602' $SITE/facts/602-agencies.html"
check "44-states shows state badges" "grep -q 'state-badge' $SITE/facts/44-states.html"
check "107-cross-agency shows 107" "grep -q '107' $SITE/facts/107-cross-agency.html"
check "nearly-two-thirds shows 62.6" "grep -q '62.6' $SITE/facts/nearly-two-thirds.html"

check "index has nav" "grep -q '<nav>' $SITE/index.html"
check "index has footer" "grep -q '<footer>' $SITE/index.html"
check "nav has Facts link" "grep -q 'Facts' $SITE/index.html"

check "index links to facts/.html" "grep -q '/facts/602-agencies.html' $SITE/index.html"
check "no old claims/ links in index" "! grep -q '/claims/' $SITE/index.html"

for f in $(find $SITE -name '*.html'); do
  size=$(wc -c < "$f")
  check "$(echo $f | sed "s|$SITE/||") under 50KB" "[[ $size -lt 51200 ]]"
done

check "602-agencies has download link" "grep -q 'Download' $SITE/facts/602-agencies.html"
check "44-states has download link" "grep -q 'Download' $SITE/facts/44-states.html"
check "70-ice has download link" "grep -q 'Download' $SITE/facts/70-ice-collaborators.html"
check "2000-searches has download link" "grep -q 'Download' $SITE/facts/2000-searches.html"
check "107-cross-agency has download link" "grep -q 'Download' $SITE/facts/107-cross-agency.html"
check "nearly-two-thirds has download link" "grep -q 'Download' $SITE/facts/nearly-two-thirds.html"

check "602-agencies has step-by-step" "grep -q 'Step 3' $SITE/facts/602-agencies.html"
check "107-cross-agency has step-by-step" "grep -q 'Step 5' $SITE/facts/107-cross-agency.html"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]