
"use client";

import { useEffect, useMemo, useState } from "react";

type EvidenceItem = {
  factor: string;
  value: string | number | boolean | null;
};

type IntelligenceResult = {
  result_id: string;
  result_type: string;
  group_key: string;
  metric_name: string;
  result_value: number;
  result_unit?: string;
  metric_unit?: string;
  priority_rank: number;
  finding: string;
  evidence: EvidenceItem[];
  quality_status: string;
  limitation: string;
  method_version: string;
  data_version: string;
  entity_name: string;
  pollutant: string;
  is_synthetic: boolean;
  period_start?: string;
  period_end?: string;
};

type IntelligenceResponse = {
  metadata: {
    data_version: string;
    method_version: string;
    count: number;
    is_synthetic: boolean;
    quality_status: string;
    description: string;
  };
  count: number;
  results: IntelligenceResult[];
};

const API_BASE = "http://localhost:8000";

const pollutantNames: Record<string, string> = {
  no2: "NO₂",
  o3: "O₃",
  pm10: "PM10",
  "pm2.5": "PM2.5",
};

function formatValue(value: string | number | boolean | null) {
  if (value === null) return "—";

  if (typeof value === "number") {
    return value.toLocaleString("en-IN", {
      maximumFractionDigits: 3,
    });
  }

  return String(value);
}

export default function DataIntelligencePage() {
  const [data, setData] = useState<IntelligenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pollutant, setPollutant] = useState("all");
  const [city, setCity] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadResults() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE}/api/intelligence/results`,
          {
            signal: controller.signal,
            cache: "no-store",
          }
        );

        if (!response.ok) {
          throw new Error(`The API returned HTTP ${response.status}.`);
        }

        const payload: unknown = await response.json();

        if (
          !payload ||
          typeof payload !== "object" ||
          !("results" in payload) ||
          !Array.isArray(payload.results)
        ) {
          throw new Error("The API response has an unexpected format.");
        }

        setData(payload as IntelligenceResponse);
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load intelligence results."
        );
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadResults();

    return () => controller.abort();
  }, []);

  const allResults = data?.results ?? [];

  const cities = useMemo(
    () =>
      [...new Set(allResults.map((result) => result.entity_name))].sort(
        (a, b) => a.localeCompare(b)
      ),
    [allResults]
  );

  const pollutants = useMemo(
    () =>
      [...new Set(allResults.map((result) => result.pollutant))].sort(),
    [allResults]
  );

  const filteredResults = useMemo(() => {
    const term = search.trim().toLowerCase();

    return allResults
      .filter(
        (result) =>
          pollutant === "all" || result.pollutant === pollutant
      )
      .filter(
        (result) => city === "all" || result.entity_name === city
      )
      .filter(
        (result) =>
          !term ||
          [
            result.entity_name,
            result.pollutant,
            result.finding,
            result.result_id,
          ].some((value) => value.toLowerCase().includes(term))
      )
      .sort(
        (a, b) =>
          a.pollutant.localeCompare(b.pollutant) ||
          a.priority_rank - b.priority_rank
      );
  }, [allResults, pollutant, city, search]);

  return (
    <main className="min-h-screen bg-[#030712] px-4 py-8 text-slate-100 sm:px-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="border-b border-slate-800 pb-6">
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-sky-400">
            INFOCREON / AETHER PULSE
          </p>

          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            Data Intelligence
          </h1>

          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
            Explore the approved Phase 3 comparative rankings, inspect
            supporting evidence, and review the limitations of each result.
          </p>
        </header>

        <section
          className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4"
          aria-label="Synthetic data notice"
        >
          <p className="text-sm font-semibold text-amber-300">
            Synthetic sample · Conditional quality
          </p>

          <p className="mt-2 text-sm leading-6 text-slate-300">
            These results are descriptive comparisons from a synthetic
            sample. They are not verified real-world measurements,
            regulatory assessments, health-risk assessments, or predictions.
            Rankings should not be interpreted as evidence of safety or
            danger.
          </p>
        </section>

        {loading && (
          <div className="rounded-xl border border-slate-800 p-8 text-slate-300">
            Loading approved intelligence results…
          </div>
        )}

        {!loading && error && (
          <section
            className="rounded-xl border border-rose-500/30 bg-rose-500/5 p-5"
            role="alert"
          >
            <h2 className="font-semibold text-rose-300">
              Results could not be loaded
            </h2>

            <p className="mt-2 text-sm text-slate-300">{error}</p>

            <p className="mt-2 text-sm text-slate-400">
              Check that the backend is running and the API URL is correct.
            </p>

            <button
              className="mt-4 rounded-lg border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
          </section>
        )}

        {!loading && !error && data && (
          <>
            <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                { label: "Published results", value: data.count },
                { label: "Cities", value: cities.length },
                { label: "Pollutants", value: pollutants.length },
                {
                  label: "Quality status",
                  value: data.metadata.quality_status,
                },
              ].map((item) => (
                <article
                  key={item.label}
                  className="rounded-xl border border-slate-800 bg-[#0B1117] p-5"
                >
                  <p className="text-sm text-slate-400">{item.label}</p>

                  <p className="mt-3 text-2xl font-semibold text-sky-300">
                    {item.value}
                  </p>
                </article>
              ))}
            </section>

            <section className="rounded-xl border border-slate-800 bg-[#0B1117] p-5">
              <h2 className="text-lg font-semibold">Explore results</h2>

              <div className="mt-4 grid gap-4 md:grid-cols-3">
                <label className="text-sm text-slate-300">
                  Pollutant
                  <select
                    value={pollutant}
                    onChange={(event) => setPollutant(event.target.value)}
                    className="mt-2 block w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
                  >
                    <option value="all">All pollutants</option>
                    {pollutants.map((value) => (
                      <option key={value} value={value}>
                        {pollutantNames[value] ?? value}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="text-sm text-slate-300">
                  City
                  <select
                    value={city}
                    onChange={(event) => setCity(event.target.value)}
                    className="mt-2 block w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
                  >
                    <option value="all">All cities</option>
                    {cities.map((value) => (
                      <option key={value} value={value}>
                        {value}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="text-sm text-slate-300">
                  Search
                  <input
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="City, pollutant, finding…"
                    className="mt-2 block w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 placeholder:text-slate-500"
                  />
                </label>
              </div>

              <p className="mt-4 text-xs text-slate-400" aria-live="polite">
                Showing {filteredResults.length} of {allResults.length} results
              </p>
            </section>

            <section className="space-y-4">
              {filteredResults.map((result) => (
                <article
                  key={result.result_id}
                  className="rounded-xl border border-slate-800 bg-[#0B1117] p-5 sm:p-6"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <p className="text-xs uppercase tracking-wider text-sky-400">
                        {pollutantNames[result.pollutant] ?? result.pollutant}
                        {" · "}Rank {result.priority_rank}
                      </p>

                      <h2 className="mt-2 text-xl font-semibold">
                        {result.entity_name}
                      </h2>

                      <p className="mt-1 text-xs text-slate-500">
                        Result ID: {result.result_id}
                      </p>
                    </div>

                    <div className="rounded-lg border border-amber-500/30 px-3 py-2">
                      <p className="text-xs text-amber-300">
                        {result.quality_status}
                      </p>
                    </div>
                  </div>

                  <div className="mt-5">
                    <p className="text-sm text-slate-400">
                      Sampled mean ·{" "}
                      {result.result_unit ??
                        result.metric_unit ??
                        "unit not specified"}
                    </p>

                    <p className="mt-1 text-3xl font-semibold tabular-nums">
                      {formatValue(result.result_value)}
                    </p>
                  </div>

                  <p className="mt-4 text-sm leading-6 text-slate-300">
                    {result.finding}
                  </p>

                  <details className="mt-5 border-t border-slate-800 pt-4">
                    <summary className="cursor-pointer text-sm font-medium text-sky-300">
                      View evidence and methodology
                    </summary>

                    <div className="mt-4 overflow-x-auto">
                      <table className="w-full text-left text-sm">
                        <thead className="text-slate-400">
                          <tr>
                            <th className="py-2 pr-4 font-medium">
                              Evidence
                            </th>
                            <th className="py-2 font-medium">Value</th>
                          </tr>
                        </thead>

                        <tbody>
                          {result.evidence.map((item, index) => (
                            <tr
                              key={`${result.result_id}-${item.factor}-${index}`}
                              className="border-t border-slate-800"
                            >
                              <td className="py-2 pr-4 text-slate-300">
                                {item.factor.replaceAll("_", " ")}
                              </td>

                              <td className="py-2 text-slate-100">
                                {formatValue(item.value)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <div className="mt-4 grid gap-3 text-sm text-slate-400 sm:grid-cols-2">
                      <p>
                        <span className="text-slate-200">Method:</span>{" "}
                        {result.method_version}
                      </p>

                      <p>
                        <span className="text-slate-200">Data version:</span>{" "}
                        {result.data_version}
                      </p>

                      {result.period_start && (
                        <p>
                          <span className="text-slate-200">Period start:</span>{" "}
                          {result.period_start}
                        </p>
                      )}

                      {result.period_end && (
                        <p>
                          <span className="text-slate-200">Period end:</span>{" "}
                          {result.period_end}
                        </p>
                      )}
                    </div>

                    <p className="mt-4 text-sm leading-6 text-amber-200/90">
                      Limitation: {result.limitation}
                    </p>
                  </details>
                </article>
              ))}

              {filteredResults.length === 0 && (
                <div className="rounded-xl border border-slate-800 p-8 text-center text-slate-400">
                  No results match these filters. Try a different city,
                  pollutant, or search term.
                </div>
              )}
            </section>

            <footer className="border-t border-slate-800 py-5 text-xs leading-5 text-slate-500">
              Data version: {data.metadata.data_version} · Method version:{" "}
              {data.metadata.method_version}. Rankings describe this
              synthetic sample only and must not be treated as regulatory or
              health advice.
            </footer>
          </>
        )}
      </div>
    </main>
  );
}
