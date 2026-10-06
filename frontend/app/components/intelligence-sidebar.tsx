"use client";

import {
  Activity,
  Globe,
  MapPin,
  ShieldAlert,
  Users,
  X,
} from "lucide-react";

import type { AirQualityFeature } from "../lib/api";

type IntelligenceSidebarProps = {
  features: AirQualityFeature[];
  loading: boolean;
  selectedCity?: string;
  onClose?: () => void;
};

type ExtendedProperties = AirQualityFeature["properties"] & {
  locality?: string | null;
  location_name?: string | null;
};

function getLocationName(
  properties: ExtendedProperties,
): string {
  const possibleNames = [
    properties.locality,
    properties.city,
    properties.location_name,
  ];

  const validName = possibleNames.find((name) => {
    if (!name || !name.trim()) {
      return false;
    }

    return !/^OpenAQ Location \d+$/i.test(name.trim());
  });

  return validName?.trim() || "Unknown Location";
}

function formatPopulation(
  population: number | null | undefined,
): string {
  if (typeof population !== "number" || !Number.isFinite(population)) {
    return "Unavailable";
  }

  return population.toLocaleString("en-US");
}

function formatValue(
  value: number | null | undefined,
): string {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "Unavailable";
  }

  return value.toLocaleString("en-US", {
    maximumFractionDigits: 2,
  });
}

export default function IntelligenceSidebar({
  features,
  loading,
  selectedCity,
  onClose,
}: IntelligenceSidebarProps) {
  const selectedFeature =
    features.find(
      (feature) =>
        feature.properties.city?.toLowerCase() ===
        selectedCity?.toLowerCase(),
    ) ?? features[0];

  const properties = selectedFeature?.properties as
    | ExtendedProperties
    | undefined;

  const locationName = properties
    ? getLocationName(properties)
    : "Unknown Location";

  const country = properties?.country?.trim() || "Unknown";

  const population = properties?.population;

  return (
    <aside className="flex h-full min-h-0 flex-col overflow-hidden border-l border-[#1F2937] bg-[#071019] text-white">
      {/* HEADER */}
      <div className="flex items-center justify-between border-b border-[#1F2937] px-7 py-6">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-[#38BDF8]">
            Real-Time Context
          </p>

          <h2 className="mt-3 text-xl font-semibold">
            Intelligence panel
          </h2>
        </div>

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close intelligence panel"
            className="rounded-xl border border-[#26384A] p-3 text-slate-400 transition hover:border-[#38BDF8] hover:text-white"
          >
            <X size={22} />
          </button>
        )}
      </div>

      {/* CONTENT */}
      <div className="min-h-0 flex-1 overflow-y-auto px-7 py-10">
        {loading ? (
          <div className="flex min-h-40 items-center justify-center">
            <p className="text-sm text-slate-400">
              Loading intelligence data...
            </p>
          </div>
        ) : !selectedFeature || !properties ? (
          <div className="flex min-h-40 items-center justify-center">
            <p className="text-sm text-slate-400">
              No air-quality data available.
            </p>
          </div>
        ) : (
          <>
            {/* LOCATION */}
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-[#38BDF8]">
                Intelligence Layer
              </p>

              <div className="mt-5 flex items-start gap-3">
                <MapPin
                  size={26}
                  className="mt-1 shrink-0 text-[#00D9FF]"
                />

                <div>
                  <h3 className="text-3xl font-bold leading-tight text-white">
                    {locationName}
                  </h3>

                  <p className="mt-2 text-base text-slate-500">
                    {country}
                  </p>
                </div>
              </div>
            </div>

            {/* POLLUTION & EXPOSURE */}
            <section className="mt-9 rounded-2xl border border-[#293847] bg-[#0B131D] p-5">
              <div className="flex items-center gap-3">
                <Activity
                  size={23}
                  className="text-[#00D9FF]"
                />

                <h4 className="text-base font-semibold tracking-wide text-slate-200">
                  POLLUTION & EXPOSURE
                </h4>
              </div>

              <p className="mt-7 text-xs uppercase tracking-wide text-slate-500">
                Current Measurement
              </p>

              <div className="mt-3 flex items-baseline gap-3">
                <span className="text-5xl font-bold text-white">
                  {formatValue(properties.value)}
                </span>

                <span className="text-sm text-slate-400">
                  {properties.unit || "—"}
                </span>
              </div>

              <p className="mt-4 text-base text-slate-500">
                {properties.pollutant?.toUpperCase() || "UNKNOWN"}
              </p>
            </section>

            {/* EXPOSURE SCORE */}
            <section className="mt-5 rounded-2xl border border-[#293847] bg-[#0B131D] p-5">
              <div className="flex items-center gap-3">
                <ShieldAlert
                  size={23}
                  className="text-yellow-400"
                />

                <h4 className="text-base font-semibold tracking-wide text-slate-200">
                  EXPOSURE SCORE
                </h4>
              </div>

              <p className="mt-6 text-4xl font-bold text-white">
                {properties.exposure_score ?? "Unavailable"}
              </p>

              <p className="mt-4 text-sm leading-6 text-slate-500">
                This score provides contextual information
                about the observed pollution level and
                potential population exposure.
              </p>
            </section>

            {/* POPULATION CONTEXT */}
            <section className="mt-5 rounded-2xl border border-[#293847] bg-[#0B131D] p-5">
              <div className="flex items-center gap-3">
                <Users
                  size={23}
                  className="text-[#00D9FF]"
                />

                <h4 className="text-base font-semibold tracking-wide text-slate-200">
                  POPULATION CONTEXT
                </h4>
              </div>

              <p className="mt-6 text-3xl font-bold text-white">
                {formatPopulation(population)}
              </p>

              <p className="mt-4 text-sm leading-6 text-slate-500">
                Population context helps interpret the
                potential scale of exposure in the observed
                location.
              </p>
            </section>

            {/* REGIONAL CONTEXT */}
            <section className="mt-5 rounded-2xl border border-[#293847] bg-[#0B131D] p-5">
              <div className="flex items-center gap-3">
                <Globe
                  size={23}
                  className="text-[#00D9FF]"
                />

                <h4 className="text-base font-semibold tracking-wide text-slate-200">
                  REGIONAL CONTEXT
                </h4>
              </div>

              <div className="mt-6 space-y-5">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    Regional Average
                  </p>

                  <p className="mt-2 text-xl font-semibold text-white">
                    {properties.regional_average != null
                      ? `${formatValue(
                          properties.regional_average,
                        )} ${properties.unit || ""}`
                      : "Unavailable"}
                  </p>
                </div>

                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    Above Regional Average
                  </p>

                  <p className="mt-2 text-xl font-semibold text-white">
                    {properties.percentage_above_regional_average !=
                    null
                      ? `${formatValue(
                          properties.percentage_above_regional_average,
                        )}%`
                      : "Unavailable"}
                  </p>
                </div>
              </div>
            </section>

            {/* SOURCE */}
            <section className="mt-5 border-t border-[#1F2937] pt-6">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Data Source
              </p>

              <p className="mt-3 text-sm text-slate-300">
                {properties.source || "Unknown"}
              </p>

              {properties.timestamp && (
                <>
                  <p className="mt-5 text-xs uppercase tracking-wide text-slate-500">
                    Timestamp
                  </p>

                  <p className="mt-3 text-sm text-slate-300">
                    {new Date(
                      properties.timestamp,
                    ).toLocaleString("en-US")}
                  </p>
                </>
              )}

              {properties.fallback && (
                <p className="mt-4 rounded-lg border border-yellow-900/50 bg-yellow-950/20 p-3 text-xs text-yellow-300">
                  Fallback data is being displayed.
                </p>
              )}
            </section>
          </>
        )}
      </div>
    </aside>
  );
}