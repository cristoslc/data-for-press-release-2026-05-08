module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("assets");

  const csv = require("csv-parse/sync");
  const fs = require("fs");
  const path = require("path");

  eleventyConfig.addGlobalData("agencies", () => {
    const raw = fs.readFileSync(
      path.resolve(__dirname, "../data/derived/sppd-shared-networks/sppd-shared-networks-normalized.csv"),
      "utf8"
    );
    return csv.parse(raw, { columns: true, skip_empty_lines: true });
  });

  eleventyConfig.addGlobalData("states", () => {
    const raw = fs.readFileSync(
      path.resolve(__dirname, "../outputs/sppd-sharing-states/states.csv"),
      "utf8"
    );
    return csv.parse(raw, { columns: true, skip_empty_lines: true }).map((r) => r.state);
  });

  eleventyConfig.addGlobalData("crossindex", () => {
    const raw = fs.readFileSync(
      path.resolve(__dirname, "../outputs/sppd-287g-crossindex/crossindex_results.csv"),
      "utf8"
    );
    const rows = csv.parse(raw, { columns: true, skip_empty_lines: true });
    const exactCount = rows.filter((r) => r.confidence === "1.0").length;
    const fuzzyCount = rows.filter((r) => r.confidence !== "1.0" && r.match_method !== "manual").length;
    const manualCount = rows.filter((r) => r.match_method === "manual").length;
    rows.forEach((r) => {
      if (r.confidence === "1.0") r.confClass = "confidence-high";
      else if (parseFloat(r.confidence) >= 0.75) r.confClass = "confidence-med";
      else r.confClass = "confidence-low";
    });
    return { rows, exactCount, fuzzyCount, manualCount, total: rows.length };
  });

  eleventyConfig.addGlobalData("assistOther", () => {
    const raw = fs.readFileSync(
      path.resolve(__dirname, "../outputs/assist-other-agencies/assist-other-agencies.csv"),
      "utf8"
    );
    const rows = csv.parse(raw, { columns: true, skip_empty_lines: true, relax_quotes: true });
    const assistOtherCount = rows.filter((r) => r.assist_label === "assist-other").length;
    const statewideCount = rows.filter((r) => r.assist_label === "statewide-system").length;
    const total = rows.length;
    const assistOtherPct = ((assistOtherCount / total) * 100).toFixed(1);
    const statewidePct = ((statewideCount / total) * 100).toFixed(1);
    const assistOtherBarPct = Math.round((assistOtherCount / total) * 100);
    return {
      total,
      assistOtherCount,
      statewideCount,
      assistOtherPct,
      statewidePct,
      assistOtherBarPct,
      rows,
    };
  });

  eleventyConfig.addGlobalData("dedupedStats", () => {
    const raw = fs.readFileSync(
      path.resolve(__dirname, "../outputs/audit-logs-deduplicated/sopo-flock-audit-deduped.csv"),
      "utf8"
    );
    const rows = csv.parse(raw, { columns: true, skip_empty_lines: true, relax_quotes: true });
    return { deduped: rows.length };
  });

  eleventyConfig.setNunjucksEnvironmentOptions({
    throwOnUndefined: false,
  });

  eleventyConfig.addFilter("number", (val) => {
    return Number(val).toLocaleString();
  });

  return {
    dir: {
      input: ".",
      output: "../_site",
    },
    pathPrefix: "/data-for-press-release-2026-05-08/",
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};