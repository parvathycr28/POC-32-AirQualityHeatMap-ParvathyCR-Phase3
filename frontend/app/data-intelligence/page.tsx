
"use client";

import Link from "next/link";
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
  generated_at: string;
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
    approved_track: string;
    generated_at: string;
    freshness_status: string;
    freshness_age_hours: number;
    stale_after_hours: number;
    validation_result: string;
  };
  count: number;
  results: IntelligenceResult[];
};

type IntelligenceSummary = {
  project_id: string;
  project_title: string;
  approved_track: string;
  primary_analytical_question: string;
  decision_to_be_supported: string;
  data_version: string;
  method_version: string;
  result_count: number;
  key_findings: unknown[];
  priority_items: unknown[];
  validation_result: string;
  important_limitations: string[];
  generated_at: string;
};

const DATA_INTELLIGENCE_API_BASE = (
  process.env.NEXT_PUBLIC_DATA_INTELLIGENCE_API_URL ??
  "http://localhost:8000"
).replace(/\/$/, "");

const EXPECTED_DATA_VERSION = "phase3-v1.1";
const EXPECTED_METHOD_VERSION = "track-a-comparative-v1.0.0";
const EXPECTED_RESULT_COUNT = 32;

const ALLOWED_QUALITY_STATUSES = new Set([
  "validated",
  "conditional",
  "rejected",
]);

const pollutantNames: Record<string, string> = {
  no2: "NO₂",
  o3: "O₃",
  pm10: "PM10",
  "pm2.5": "PM2.5",
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function requireString(
  record: Record<string, unknown>,
  key: string,
  label: string
): string {
  const value = record[key];

  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${label} is missing or invalid.`);
  }

  return value;
}

function validateSummary(payload: unknown): IntelligenceSummary {
  if (!isRecord(payload)) {
    throw new Error(
      "The intelligence summary must be a JSON object."
    );
  }

  const requiredStringFields = [
    "project_id",
    "project_title",
    "approved_track",
    "primary_analytical_question",
    "decision_to_be_supported",
    "data_version",
    "method_version",
    "validation_result",
    "generated_at",
  ];

  for (const field of requiredStringFields) {
    requireString(
      payload,
      field,
      `Summary field '${field}'`
    );
  }

  if (payload.data_version !== EXPECTED_DATA_VERSION) {
    throw new Error(
      "The summary data version is not the expected version."
    );
  }

  if (payload.method_version !== EXPECTED_METHOD_VERSION) {
    throw new Error(
      "The summary method version is not the expected version."
    );
  }

  if (payload.validation_result !== "PASS") {
    throw new Error(
      "The analytical summary has not passed validation."
    );
  }

  if (
    !Number.isInteger(payload.result_count) ||
    payload.result_count !== EXPECTED_RESULT_COUNT
  ) {
    throw new Error(
      "The summary result count is inconsistent."
    );
  }

  if (
    !Array.isArray(payload.key_findings) ||
    !Array.isArray(payload.priority_items) ||
    !Array.isArray(payload.important_limitations)
  ) {
    throw new Error(
      "The summary findings, priorities, or limitations are invalid."
    );
  }

  if (
    !payload.important_limitations.every(
      (item) =>
        typeof item === "string" && item.trim() !== ""
    )
  ) {
    throw new Error(
      "The summary contains an invalid analytical limitation."
    );
  }

  const generatedAt = payload.generated_at as string;

  if (
    !Number.isFinite(Date.parse(generatedAt)) ||
    !/(Z|[+-]\d{2}:\d{2})$/i.test(generatedAt)
  ) {
    throw new Error(
      "The summary timestamp must be valid and include a timezone."
    );
  }

  return payload as unknown as IntelligenceSummary;
}

function validateResults(
  payload: unknown,
  summaryData: IntelligenceSummary
): IntelligenceResponse {
  if (!isRecord(payload) || !isRecord(payload.metadata)) {
    throw new Error(
      "The intelligence results response has an invalid structure."
    );
  }

  if (!Array.isArray(payload.results)) {
    throw new Error(
      "The API results field must be an array."
    );
  }

  const metadata = payload.metadata;
  const results = payload.results;

  if (
    payload.count !== results.length ||
    metadata.count !== results.length ||
    results.length !== EXPECTED_RESULT_COUNT ||
    results.length !== summaryData.result_count
  ) {
    throw new Error(
      "The summary, metadata, and results counts do not match."
    );
  }

  if (
    metadata.data_version !== EXPECTED_DATA_VERSION ||
    metadata.data_version !== summaryData.data_version ||
    metadata.method_version !== EXPECTED_METHOD_VERSION ||
    metadata.method_version !== summaryData.method_version
  ) {
    throw new Error(
      "The results and summary versions do not match."
    );
  }

  if (
    metadata.validation_result !== "PASS" ||
    metadata.generated_at !== summaryData.generated_at ||
    metadata.approved_track !== summaryData.approved_track ||
    metadata.is_synthetic !== true ||
    typeof metadata.quality_status !== "string" ||
    typeof metadata.description !== "string"
  ) {
    throw new Error(
      "The results metadata does not match the approved summary."
    );
  }

  if (
    !["CURRENT", "STALE"].includes(
      String(metadata.freshness_status)
    ) ||
    typeof metadata.freshness_age_hours !== "number" ||
    !Number.isFinite(metadata.freshness_age_hours) ||
    typeof metadata.stale_after_hours !== "number" ||
    !Number.isFinite(metadata.stale_after_hours)
  ) {
    throw new Error(
      "The data freshness metadata is invalid."
    );
  }

  const seenIds = new Set<string>();

  for (const item of results) {
    if (!isRecord(item)) {
      throw new Error(
        "A result record is not a valid object."
      );
    }

    const requiredStringFields = [
      "result_id",
      "result_type",
      "group_key",
      "metric_name",
      "finding",
      "quality_status",
      "limitation",
      "method_version",
      "data_version",
      "generated_at",
      "entity_name",
      "pollutant",
    ];

    for (const field of requiredStringFields) {
      requireString(
        item,
        field,
        `Result field '${field}'`
      );
    }

    if (item.result_type !== "ranking") {
      throw new Error(
        "A result has an unsupported result type."
      );
    }

    if (
      item.data_version !== summaryData.data_version ||
      item.method_version !== summaryData.method_version ||
      item.generated_at !== summaryData.generated_at
    ) {
      throw new Error(
        "A result's version or timestamp is inconsistent."
      );
    }

    if (item.is_synthetic !== true) {
      throw new Error(
        "A result is missing the synthetic-data flag."
      );
    }

    if (
      typeof item.result_value !== "number" ||
      !Number.isFinite(item.result_value)
    ) {
      throw new Error(
        "A result contains an invalid numeric value."
      );
    }

    if (
      !Number.isInteger(item.priority_rank) ||
      (item.priority_rank as number) < 1
    ) {
      throw new Error(
        "A result contains an invalid priority rank."
      );
    }

    if (
      typeof item.quality_status !== "string" ||
      !ALLOWED_QUALITY_STATUSES.has(item.quality_status)
    ) {
      throw new Error(
        "A result contains an unsupported quality status."
      );
    }

    const resultId = item.result_id as string;

    if (seenIds.has(resultId)) {
      throw new Error(
        "Duplicate result IDs were found."
      );
    }

    seenIds.add(resultId);

    if (
      !Array.isArray(item.evidence) ||
      item.evidence.length === 0
    ) {
      throw new Error(
        "A result is missing its supporting evidence."
      );
    }

    for (const evidence of item.evidence) {
      if (
        !isRecord(evidence) ||
        typeof evidence.factor !== "string" ||
        evidence.factor.trim() === "" ||
        !("value" in evidence)
      ) {
        throw new Error(
          "A result contains an invalid evidence item."
        );
      }

      const evidenceValue = evidence.value;

      if (
        evidenceValue !== null &&
        typeof evidenceValue !== "string" &&
        typeof evidenceValue !== "number" &&
        typeof evidenceValue !== "boolean"
      ) {
        throw new Error(
          "An evidence item contains an unsupported value."
        );
      }

      if (
        typeof evidenceValue === "number" &&
        !Number.isFinite(evidenceValue)
      ) {
        throw new Error(
          "An evidence item contains a non-finite number."
        );
      }
    }
  }

  return payload as unknown as IntelligenceResponse;
}

function formatValue(
  value: string | number | boolean | null
) {
  if (value === null) return "—";

  if (typeof value === "number") {
    return value.toLocaleString("en-IN", {
      maximumFractionDigits: 3,
    });
  }

  return String(value);
}

export default function DataIntelligencePage() {
  const [data, setData] =
    useState<IntelligenceResponse | null>(null);

  const [summary, setSummary] =
    useState<IntelligenceSummary | null>(null);

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

        const [resultsResponse, summaryResponse] =
          await Promise.all([
            fetch(
              `${DATA_INTELLIGENCE_API_BASE}/api/intelligence/results`,
              {
                cache: "no-store",
                signal: controller.signal,
              }
            ),
            fetch(
              `${DATA_INTELLIGENCE_API_BASE}/api/intelligence/summary`,
              {
                cache: "no-store",
                signal: controller.signal,
              }
            ),
          ]);

        if (!resultsResponse.ok) {
          throw new Error(
            `The results API returned HTTP ${resultsResponse.status}.`
          );
        }

        if (!summaryResponse.ok) {
          throw new Error(
            `The summary API returned HTTP ${summaryResponse.status}.`
          );
        }

        const [
          resultsPayload,
          summaryPayload,
        ]: [unknown, unknown] = await Promise.all([
          resultsResponse.json(),
          summaryResponse.json(),
        ]);

        const validatedSummary =
          validateSummary(summaryPayload);

        const validatedResults = validateResults(
          resultsPayload,
          validatedSummary
        );

        setSummary(validatedSummary);
        setData(validatedResults);
      } catch (err) {
        if (
          err instanceof Error &&
          err.name === "AbortError"
        ) {
          return;
        }

        setData(null);
        setSummary(null);

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

  const allResults = useMemo(
    () => data?.results ?? [],
    [data]
  );

  const cities = useMemo(
    () =>
      [
        ...new Set(
          allResults.map((result) => result.entity_name)
        ),
      ].sort((a, b) => a.localeCompare(b)),
    [allResults]
  );

  const pollutants = useMemo(
    () =>
      [
        ...new Set(
          allResults.map((result) => result.pollutant)
        ),
      ].sort(),
    [allResults]
  );

  const filteredResults = useMemo(() => {
    const term = search.trim().toLowerCase();

    return allResults
      .filter(
        (result) =>
          pollutant === "all" ||
          result.pollutant === pollutant
      )
      .filter(
        (result) =>
          city === "all" ||
          result.entity_name === city
      )
      .filter(
        (result) =>
          !term ||
          [
            result.entity_name,
            result.pollutant,
            result.finding,
            result.result_id,
          ].some((value) =>
            value.toLowerCase().includes(term)
          )
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
          <nav
            aria-label="Primary navigation"
            className="mb-5"
          >
            <Link
              href="/"
              className="text-sm text-sky-300 hover:text-sky-200"
            >
              ← Operational View
            </Link>
          </nav>

          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-sky-400">
            INFOCREON / AETHER PULSE
          </p>

          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            Data Intelligence
          </h1>

          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
            Explore the approved Phase 3 comparative rankings,
            inspect supporting evidence, and review the
            limitations of each result.
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
            These results are descriptive comparisons from a
            synthetic sample. They are not verified real-world
            measurements, regulatory assessments, health-risk
            assessments, or predictions. Rankings should not be
            interpreted as evidence of safety or danger.
          </p>
        </section>

        {loading && (
          <div
            className="rounded-xl border border-slate-800 p-8 text-slate-300"
            role="status"
            aria-live="polite"
          >
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

            <p className="mt-2 text-sm text-slate-300">
              {error}
            </p>

            <p className="mt-2 text-sm text-slate-400">
              Check that the backend is running, both API
              endpoints are available, and the API URL is correct.
            </p>

            <button
              className="mt-4 rounded-lg border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
          </section>
        )}

        {!loading && !error && data && summary && (
          <>
            <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                {
                  label: "Published results",
                  value: data.count,
                },
                {
                  label: "Cities",
                  value: cities.length,
                },
                {
                  label: "Pollutants",
                  value: pollutants.length,
                },
                {
                  label: "Quality status",
                  value: data.metadata.quality_status,
                },
              ].map((item) => (
                <article
                  key={item.label}
                  className="rounded-xl border border-slate-800 bg-[#0B1117] p-5"
                >
                  <p className="text-sm text-slate-400">
                    {item.label}
                  </p>

                  <p className="mt-3 text-2xl font-semibold text-sky-300">
                    {item.value}
                  </p>
                </article>
              ))}
            </section>

            <section className="rounded-xl border border-slate-800 bg-[#0B1117] p-5">
              <h2 className="text-lg font-semibold">
                Methodology and data provenance
              </h2>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-slate-400">
                    Approved analytical track
                  </p>
                  <p className="mt-1 text-sm text-slate-100">
                    {summary.approved_track}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Validation result
                  </p>
                  <p className="mt-1 font-semibold text-emerald-300">
                    {summary.validation_result}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Data version
                  </p>
                  <p className="mt-1 text-sm text-slate-100">
                    {summary.data_version}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Method version
                  </p>
                  <p className="mt-1 text-sm text-slate-100">
                    {summary.method_version}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Results generated (UTC)
                  </p>
                  <p className="mt-1 break-words text-sm text-slate-100">
                    <time dateTime={summary.generated_at}>
                      {new Date(
                        summary.generated_at
                      ).toISOString()}
                    </time>
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-400">
                    Data freshness
                  </p>

                  <p
                    className={`mt-1 font-semibold ${
                      data.metadata.freshness_status === "STALE"
                        ? "text-amber-300"
                        : "text-emerald-300"
                    }`}
                  >
                    {data.metadata.freshness_status}
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    Age:{" "}
                    {data.metadata.freshness_age_hours.toFixed(1)}{" "}
                    hours · Threshold:{" "}
                    {data.metadata.stale_after_hours} hours
                  </p>
                </div>
              </div>

              <div className="mt-5 border-t border-slate-800 pt-4">
                <h3 className="text-sm font-semibold text-slate-200">
                  Primary analytical question
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {summary.primary_analytical_question}
                </p>

                <h3 className="mt-4 text-sm font-semibold text-slate-200">
                  Decision supported
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {summary.decision_to_be_supported}
                </p>
              </div>

              <details className="mt-5 border-t border-slate-800 pt-4">
                <summary className="cursor-pointer text-sm font-medium text-sky-300">
                  Important analytical limitations
                </summary>

                <ul className="mt-3 list-disc space-y-2 pl-5 text-sm leading-6 text-slate-400">
                  {summary.important_limitations.map(
                    (limitation, index) => (
                      <li key={`${index}-${limitation}`}>
                        {limitation}
                      </li>
                    )
                  )}
                </ul>
              </details>
            </section>

            <section className="rounded-xl border border-slate-800 bg-[#0B1117] p-5">
              <h2 className="text-lg font-semibold">
                Explore results
              </h2>

              <div className="mt-4 grid gap-4 md:grid-cols-3">
                <label className="text-sm text-slate-300">
                  Pollutant
                  <select
                    value={pollutant}
                    onChange={(event) =>
                      setPollutant(event.target.value)
                    }
                    className="mt-2 block w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
                  >
                    <option value="all">
                      All pollutants
                    </option>

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
                    onChange={(event) =>
                      setCity(event.target.value)
                    }
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
                    onChange={(event) =>
                      setSearch(event.target.value)
                    }
                    placeholder="City, pollutant, finding…"
                    className="mt-2 block w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 placeholder:text-slate-500"
                  />
                </label>
              </div>

              <p
                className="mt-4 text-xs text-slate-400"
                aria-live="polite"
              >
                Showing {filteredResults.length} of{" "}
                {allResults.length} results
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
                        {pollutantNames[result.pollutant] ??
                          result.pollutant}
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
                            <th className="py-2 font-medium">
                              Value
                            </th>
                          </tr>
                        </thead>

                        <tbody>
                          {result.evidence.map(
                            (item, index) => (
                              <tr
                                key={`${result.result_id}-${item.factor}-${index}`}
                                className="border-t border-slate-800"
                              >
                                <td className="py-2 pr-4 text-slate-300">
                                  {item.factor.replaceAll(
                                    "_",
                                    " "
                                  )}
                                </td>

                                <td className="py-2 text-slate-100">
                                  {formatValue(item.value)}
                                </td>
                              </tr>
                            )
                          )}
                        </tbody>
                      </table>
                    </div>

                    <div className="mt-4 grid gap-3 text-sm text-slate-400 sm:grid-cols-2">
                      <p>
                        <span className="text-slate-200">
                          Method:
                        </span>{" "}
                        {result.method_version}
                      </p>

                      <p>
                        <span className="text-slate-200">
                          Data version:
                        </span>{" "}
                        {result.data_version}
                      </p>

                      <p>
                        <span className="text-slate-200">
                          Generated at (UTC):
                        </span>{" "}
                        {new Date(
                          result.generated_at
                        ).toISOString()}
                      </p>

                      {result.period_start && (
                        <p>
                          <span className="text-slate-200">
                            Period start:
                          </span>{" "}
                          {result.period_start}
                        </p>
                      )}

                      {result.period_end && (
                        <p>
                          <span className="text-slate-200">
                            Period end:
                          </span>{" "}
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
                  No results match these filters. Try a different
                  city, pollutant, or search term.
                </div>
              )}
            </section>

            <footer className="border-t border-slate-800 py-5 text-xs leading-5 text-slate-500">
              Data version: {data.metadata.data_version} ·
              Method version: {data.metadata.method_version}.
              Rankings describe this synthetic sample only and
              must not be treated as regulatory or health advice.
            </footer>
          </>
        )}
      </div>
    </main>
  );
}