
const ASSISTANT_API_URL =
  process.env.NEXT_PUBLIC_ASSISTANT_API_URL ||
  "http://127.0.0.1:8000";

export type AssistantEvidence = {
  result_id?: string;
  result_type?: string;
  entity_id?: string;
  group_key?: string;
  metric_name?: string;
  result_value?: number;
  result_unit?: string;
  priority_rank?: number;
  finding?: string;
  quality_status?: string;
  limitation?: string;
  data_version?: string;
  method_version?: string;
  [key: string]: unknown;
};

export type AssistantResponse = {
  status: string;
  answer: string;
  evidence: AssistantEvidence[];

  explanation?: {
    status?: string;
    text?: string;
    reason?: string | null;
    model?: string;
    validation?: {
      valid?: boolean;
      errors?: string[];
      warnings?: string[];
    };
  };

  validation?: {
    valid?: boolean;
    errors?: string[];
    warnings?: string[];
    record_count?: number;
  };

  grounding?: {
    mode?: string;
    gemini_attempted?: boolean;
    llm_used?: boolean;
    explanation_validated?: boolean;
    deterministic_fallback_used?: boolean;
    generated_findings?: boolean;
    source?: string;
  };
};

export async function askAssistant(
  question: string
): Promise<AssistantResponse> {
  const response = await fetch(
    `${ASSISTANT_API_URL}/api/assistant/ask`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      `Assistant request failed with HTTP ${response.status}.`
    );
  }

  return response.json();
}
