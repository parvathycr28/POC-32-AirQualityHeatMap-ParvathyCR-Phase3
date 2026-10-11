
"use client";

import { FormEvent, useState } from "react";
import {
  askAssistant,
  AssistantResponse,
} from "../lib/assistant-api";

const SUGGESTIONS = [
  "Summarize the Track A findings",
  "Which city has the highest sampled mean for no2?",
  "Compare Delhi and Mumbai for no2",
  "Show evidence RES-0001",
  "Explain the method, data version, and limitations",
];

export default function AssistantPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AssistantResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const value = question.trim();

    if (!value) {
      setError("Please enter a question.");
      return;
    }

    if (value.length > 500) {
      setError("Questions must be 500 characters or fewer.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      setResult(await askAssistant(value));
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not contact the assistant."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-5xl px-4 py-8 sm:px-6">
      <header className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-wider text-sky-600">
          Aether Pulse · Phase 3
        </p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900">
          Grounded Data Assistant
        </h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          Ask about approved Track A findings. Answers retrieve existing
          intelligence records and do not generate predictions or
          recalculate analytical results.
        </p>
      </header>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <form onSubmit={submitQuestion} className="space-y-3">
          <label
            htmlFor="assistant-question"
            className="block text-sm font-medium text-slate-700"
          >
            Your question
          </label>

          <textarea
            id="assistant-question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            maxLength={500}
            rows={3}
            placeholder="For example: Compare Delhi and Mumbai for no2"
            className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
          />

          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs text-slate-500">
              {question.length}/500 characters
            </span>
            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 disabled:opacity-60"
            >
              {loading ? "Checking evidence..." : "Ask assistant"}
            </button>
          </div>
        </form>

        {error && (
          <p role="alert" className="mt-4 text-sm text-red-700">
            {error}
          </p>
        )}
      </section>

      <section className="mt-6">
        <h2 className="text-sm font-semibold text-slate-800">
          Suggested questions
        </h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => {
                setQuestion(suggestion);
                setError("");
              }}
              className="rounded-full border border-slate-300 bg-white px-3 py-2 text-left text-sm text-slate-700 hover:border-sky-400 hover:bg-sky-50"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </section>

      {result && (
        <section
          aria-live="polite"
          className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-slate-900">
              Assistant response
            </h2>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
              {result.status}
            </span>
          </div>

          <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-700">
            {result.answer}
          </p>

          {result.grounding && (
            <div className="mt-4 rounded-xl bg-slate-50 p-3 text-xs leading-5 text-slate-600">
              <p>Mode: {result.grounding.mode ?? "Not provided"}</p>
              <p>
                LLM used:{" "}
                {result.grounding.llm_used === undefined
                  ? "Not provided"
                  : result.grounding.llm_used
                    ? "Yes"
                    : "No"}
              </p>
              <p>
                Generated findings:{" "}
                {result.grounding.generated_findings === undefined
                  ? "Not provided"
                  : result.grounding.generated_findings
                    ? "Yes"
                    : "No"}
              </p>
            </div>
          )}

          <div className="mt-6">
            <h3 className="text-sm font-semibold text-slate-900">
              Supporting evidence ({result.evidence?.length ?? 0})
            </h3>

            {result.evidence?.length ? (
              <div className="mt-3 space-y-3">
                {result.evidence.map((record, index) => (
                  <details
                    key={record.result_id ?? `record-${index}`}
                    className="rounded-xl border border-slate-200"
                  >
                    <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-slate-800">
                      {record.result_id ?? `Evidence ${index + 1}`}
                      {record.entity_id ? ` · ${record.entity_id}` : ""}
                      {record.metric_name ? ` · ${record.metric_name}` : ""}
                    </summary>

                    <div className="space-y-3 border-t border-slate-200 px-4 py-3 text-sm">
                      {record.finding && (
                        <p className="leading-6 text-slate-700">
                          {record.finding}
                        </p>
                      )}

                      {record.result_value !== undefined && (
                        <p className="text-slate-700">
                          Recorded value: {record.result_value}{" "}
                          {record.result_unit ?? ""}
                        </p>
                      )}

                      {record.priority_rank !== undefined && (
                        <p className="text-slate-700">
                          Recorded rank: {record.priority_rank}
                        </p>
                      )}

                      {record.data_version && (
                        <p className="text-slate-700">
                          Data version: {record.data_version}
                        </p>
                      )}

                      {record.method_version && (
                        <p className="text-slate-700">
                          Method version: {record.method_version}
                        </p>
                      )}

                      {record.quality_status && (
                        <p className="text-slate-700">
                          Quality status: {record.quality_status}
                        </p>
                      )}

                      {record.limitation && (
                        <p className="rounded-lg bg-amber-50 p-3 text-xs leading-5 text-amber-800">
                          Limitation: {record.limitation}
                        </p>
                      )}
                    </div>
                  </details>
                ))}
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-500">
                No supporting evidence was returned.
              </p>
            )}
          </div>
        </section>
      )}

      <footer className="mt-8 border-t border-slate-200 pt-4 text-xs leading-5 text-slate-500">
        The data is synthetic and intended for descriptive comparison only.
        It is not a verified real-world measurement, health-risk assessment,
        regulatory assessment, or prediction.
      </footer>
    </main>
  );
}
