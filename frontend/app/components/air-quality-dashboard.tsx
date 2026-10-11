"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  Download,
  Layers,
  MapPin,
  RefreshCw,
  SlidersHorizontal,
  X,
} from "lucide-react";

import AirQualityMap from "./air-quality-map";
import CitySearchSelect from "./city-search-select";
import IntelligenceSidebar from "./intelligence-sidebar";

import {
  getAirQuality,
  type AirQualityFeature,
} from "../lib/api";

type PollutantOption = {
  label: string;
  value: string;
};

const POLLUTANTS: PollutantOption[] = [
  {
    label: "PM2.5",
    value: "PM2.5",
  },
  {
    label: "PM10",
    value: "PM10",
  },
  {
    label: "NO₂",
    value: "NO2",
  },
  {
    label: "SO₂",
    value: "SO2",
  },
  {
    label: "CO",
    value: "CO",
  },
  {
    label: "O₃",
    value: "O3",
  },
];

function formatValue(
  value: number | null | undefined,
): string {
  if (
    value == null ||
    !Number.isFinite(value)
  ) {
    return "—";
  }

  return value.toFixed(1);
}

function getPollutionStatus(
  value: number | null | undefined,
): {
  label: string;
  className: string;
} {
  if (
    value == null ||
    !Number.isFinite(value)
  ) {
    return {
      label: "Unavailable",
      className: "text-slate-500",
    };
  }

  if (value <= 12) {
    return {
      label: "Good",
      className: "text-green-400",
    };
  }

  if (value <= 35) {
    return {
      label: "Moderate",
      className: "text-yellow-400",
    };
  }

  if (value <= 55) {
    return {
      label: "Unhealthy (SG)",
      className: "text-orange-400",
    };
  }

  if (value <= 150) {
    return {
      label: "Unhealthy",
      className: "text-red-400",
    };
  }

  return {
    label: "Very Unhealthy",
    className: "text-purple-400",
  };
}

export default function AirQualityDashboard() {
  /*
   * =========================================================
   * STATE
   * =========================================================
   */

  const [features, setFeatures] =
    useState<AirQualityFeature[]>([]);

  const [pollutant, setPollutant] =
    useState("PM2.5");

  const [selectedCity, setSelectedCity] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [refreshKey, setRefreshKey] =
    useState(0);

  const [intelligenceOpen, setIntelligenceOpen] =
    useState(false);

  const [showSensors, setShowSensors] =
    useState(true);

  const [showHeatmap, setShowHeatmap] =
    useState(false);

  /*
   * =========================================================
   * LOAD AIR QUALITY DATA
   * =========================================================
   */

  const loadData = useCallback(
    async () => {
      setLoading(true);
      setError(null);

      try {
        const response =
          await getAirQuality(pollutant);

        setFeatures(
          response.features ?? [],
        );
      } catch (requestError) {
        console.error(
          "Air-quality request failed:",
          requestError,
        );

        setFeatures([]);

        setError(
          requestError instanceof Error
            ? requestError.message
            : "Unable to load air-quality data.",
        );
      } finally {
        setLoading(false);
      }
    },
    [pollutant],
  );

    useEffect(() => {
  let active = true;

  const run = async () => {
    if (active) await loadData();
  };

  void run();

  return () => {
    active = false;
  };
}, [loadData, refreshKey]);

  /*
   * =========================================================
   * AVAILABLE CITIES
   * =========================================================
   */

  const cities = useMemo(() => {
    return Array.from(
      new Set(
        features
          .map(
            (feature) =>
              feature.properties.city,
          )
          .filter(
            (
              city,
            ): city is string =>
              Boolean(city),
          ),
      ),
    ).sort((a, b) =>
      a.localeCompare(b),
    );
  }, [features]);

  /*
   * =========================================================
   * SELECTED CITY FEATURE
   * =========================================================
   */

  const selectedFeature = useMemo(() => {
    if (!selectedCity) {
      return null;
    }

    return (
      features.find(
        (feature) =>
          feature.properties.city ===
          selectedCity,
      ) ?? null
    );
  }, [features, selectedCity]);

  /*
   * =========================================================
   * CURRENT FEATURE
   * =========================================================
   */

  const currentFeature =
    selectedFeature ??
    features[0] ??
    null;

  /*
   * =========================================================
   * CITY OVERVIEW
   *
   * This is a single-city overview.
   * There is NO City A / City B comparison.
   * =========================================================
   */

  const displayedCities = useMemo(() => {
    return cities
      .map((city) => {
        const feature = features.find(
          (item) =>
            item.properties.city ===
            city,
        );

        if (!feature) {
          return null;
        }

        return {
          city,
          value: feature.properties.value,
          unit: feature.properties.unit,
          feature,
        };
      })
      .filter(
        (
          item,
        ): item is {
          city: string;
          value: number;
          unit: string;
          feature: AirQualityFeature;
        } => item !== null,
      )
      .sort(
        (a, b) => b.value - a.value,
      )
      .slice(0, 6);
  }, [cities, features]);

  /*
   * =========================================================
   * SELECT CITY FROM MAP
   * =========================================================
   */

  const handleCitySelect = (
    city: string,
  ) => {
    setSelectedCity(city);
    setIntelligenceOpen(true);
  };

  /*
   * =========================================================
   * SELECT CITY FROM SEARCH
   * =========================================================
   */

  const handleCityChange = (
    city: string,
  ) => {
    setSelectedCity(city);

    if (city) {
      setIntelligenceOpen(true);
    }
  };

  /*
   * =========================================================
   * DOWNLOAD CSV
   * =========================================================
   */

  const downloadCsv = () => {
    if (features.length === 0) {
      return;
    }

    const headers = [
      "City",
      "Country",
      "Pollutant",
      "Value",
      "Unit",
      "Timestamp",
      "Population",
      "Exposure Score",
      "Regional Average",
    ];

    const rows = features.map(
      (feature) => {
        const properties =
          feature.properties;

        return [
          properties.city ?? "",
          properties.country ?? "",
          properties.pollutant ??
            pollutant,
          properties.value ?? "",
          properties.unit ?? "",
          properties.timestamp ?? "",
          properties.population ?? "",
          properties.exposure_score ?? "",
          properties.regional_average ?? "",
        ];
      },
    );

    const csv = [
      headers,
      ...rows,
    ]
      .map((row) =>
        row
          .map(
            (value) =>
              `"${String(value).replaceAll(
                '"',
                '""',
              )}"`,
          )
          .join(","),
      )
      .join("\n");

    const blob = new Blob(
      [csv],
      {
        type: "text/csv;charset=utf-8;",
      },
    );

    const url =
      URL.createObjectURL(blob);

    const link =
      document.createElement("a");

    link.href = url;

    link.download =
      `air-quality-${pollutant.toLowerCase()}.csv`;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  /*
   * =========================================================
   * CURRENT POLLUTION STATUS
   * =========================================================
   */

  const currentStatus =
    getPollutionStatus(
      currentFeature?.properties.value,
    );

  /*
   * =========================================================
   * RENDER
   * =========================================================
   */

  return (
    <main className="min-h-screen overflow-x-hidden bg-[#030712] text-white">

      {/* =====================================================
          TOP HEADER
          ===================================================== */}

      <header className="border-b border-[#1F2937] bg-[#07111B]">
        <div className="flex min-h-[80px] flex-col gap-4 px-5 py-4 xl:flex-row xl:items-center xl:justify-between">

          {/* BRAND */}

          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-[#38BDF8]/40 bg-[#38BDF8]/5">
              <Activity className="h-7 w-7 text-[#38BDF8]" />
            </div>

            <div>
              <h1 className="text-xl font-bold tracking-wide">
                REAL RAILS
              </h1>

              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
                Intelligence Library
              </p>
            </div>
          </div>

          {/* TITLE */}

          <div className="flex-1 xl:px-8">
            <h2 className="text-lg font-semibold">
              Air Quality Heatmap
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Real-time Pollution & Exposure
              Intelligence
            </p>
          </div>

          {/* FILTERS */}

          <div className="flex flex-col gap-3 sm:flex-row">

            {/* POLLUTANT */}

            <label className="relative min-w-[180px]">
              <span className="absolute left-4 top-2 z-10 text-[11px] text-slate-500">
                Pollutant
              </span>

              <select
                value={pollutant}
                onChange={(event) => {
                  setPollutant(
                    event.target.value,
                  );

                  setSelectedCity("");

                  setIntelligenceOpen(
                    false,
                  );
                }}
                className="h-14 w-full appearance-none rounded-lg border border-[#1F2937] bg-[#0B1117] px-4 pb-1 pt-5 text-sm font-semibold text-white outline-none transition focus:border-[#38BDF8] focus:ring-1 focus:ring-[#38BDF8]/30"
                aria-label="Select pollutant"
              >
                {POLLUTANTS.map(
                  (option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  ),
                )}
              </select>
            </label>

            {/* CITY SEARCH */}

            <CitySearchSelect
              cities={cities}
              value={selectedCity}
              onChange={
                handleCityChange
              }
              placeholder="Search city"
            />

            {/* REFRESH */}

            <button
              type="button"
              onClick={() =>
                setRefreshKey(
                  (value) =>
                    value + 1,
                )
              }
              className="flex h-14 items-center justify-center rounded-lg border border-[#1F2937] bg-[#0B1117] px-4 text-slate-300 transition hover:border-[#38BDF8] hover:text-[#38BDF8] focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/40"
              aria-label="Refresh air quality data"
              title="Refresh data"
            >
              <RefreshCw
                className={
                  loading
                    ? "h-5 w-5 animate-spin"
                    : "h-5 w-5"
                }
              />
            </button>
          </div>
        </div>
      </header>

      {/* =====================================================
          SOURCE BAR
          ===================================================== */}

      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#1F2937] bg-[#050D16] px-5 py-3">

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="h-2.5 w-2.5 rounded-full bg-green-400 shadow-[0_0_10px_rgba(74,222,128,0.6)]" />

          <span>
            Source: OpenAQ
            {features.some(
              (feature) =>
                feature.properties
                  .fallback,
            )
              ? " • Fallback data"
              : " • Live"}
          </span>
        </div>

        <button
          type="button"
          onClick={() =>
            setIntelligenceOpen(true)
          }
          className="flex items-center gap-2 rounded-lg border border-[#38BDF8]/40 px-4 py-2 text-xs font-semibold text-[#38BDF8] transition hover:bg-[#38BDF8]/10 focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/40"
        >
          <SlidersHorizontal className="h-4 w-4" />

          Intelligence Panel
        </button>
      </div>

      {/* =====================================================
          MAP
          ===================================================== */}

      <section className="relative border-b border-[#1F2937] bg-[#07131F]">

        <div className="relative h-[calc(138vh-235px)] min-h-[500px] w-full overflow-hidden">

          {/* ERROR */}

          {error ? (
            <div className="flex h-full items-center justify-center px-6 text-center">
              <div>
                <p className="text-red-400">
                  {error}
                </p>

                <button
                  type="button"
                  onClick={() =>
                    setRefreshKey(
                      (value) =>
                        value + 1,
                    )
                  }
                  className="mt-4 rounded-lg border border-[#38BDF8] px-4 py-2 text-sm text-[#38BDF8] transition hover:bg-[#38BDF8]/10 focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/40"
                >
                  Try again
                </button>
              </div>
            </div>

          ) : loading ? (

            /* LOADING */

            <div className="flex h-full items-center justify-center">
              <div className="text-center">

                <RefreshCw className="mx-auto h-8 w-8 animate-spin text-[#38BDF8]" />

                <p className="mt-4 text-sm text-slate-400">
                  Loading global air-quality
                  observations...
                </p>
              </div>
            </div>

          ) : features.length === 0 ? (

            /* EMPTY */

            <div className="flex h-full items-center justify-center px-6 text-center text-sm text-slate-400">
              No air-quality observations
              available.
            </div>

          ) : (

            /* MAP */

            <AirQualityMap
              features={features}
              pollutant={pollutant}
              onCitySelect={
                handleCitySelect
              }
              showSensors={
                showSensors
              }
              showHeatmap={
                showHeatmap
              }
            />
          )}

          {/* =================================================
              MAP LEGEND
              ================================================= */}

          <div className="absolute right-4 top-4 z-[400] w-48 rounded-lg border border-slate-700/80 bg-[#0A1B29]/95 p-4 shadow-xl backdrop-blur">

            <p className="text-xs font-semibold text-white">
              {pollutant} (μg/m³)
            </p>

            <div className="mt-3 space-y-3 text-xs">

              {[
                {
                  color:
                    "bg-green-500",
                  range: "0 - 12",
                  label: "Good",
                },
                {
                  color:
                    "bg-yellow-400",
                  range: "12 - 35",
                  label: "Moderate",
                },
                {
                  color:
                    "bg-orange-400",
                  range: "35 - 55",
                  label:
                    "Unhealthy (SG)",
                },
                {
                  color:
                    "bg-red-500",
                  range: "55 - 150",
                  label: "Unhealthy",
                },
                {
                  color:
                    "bg-purple-500",
                  range: "150+",
                  label:
                    "Very Unhealthy",
                },
              ].map(
                (item) => (
                  <div
                    key={item.range}
                    className="flex items-center gap-2"
                  >
                    <span
                      className={`h-3.5 w-3.5 rounded-full ${item.color} border border-white/30`}
                    />

                    <span className="text-slate-200">
                      {item.range}
                    </span>

                    <span className="ml-auto text-[10px] text-slate-500">
                      {item.label}
                    </span>
                  </div>
                ),
              )}
            </div>
          </div>

          {/* =================================================
              MAP CONTROLS
              ================================================= */}

          <div className="absolute bottom-4 left-4 z-[400] flex flex-col gap-2">

            {/* SENSOR */}

            <button
              type="button"
              onClick={() =>
                setShowSensors(
                  (value) =>
                    !value,
                )
              }
              className={`rounded-lg border p-3 shadow-lg backdrop-blur transition focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/50 ${
                showSensors
                  ? "border-[#38BDF8] bg-[#38BDF8]/20 text-[#38BDF8]"
                  : "border-slate-600 bg-[#0A1B29]/90 text-slate-400"
              }`}
              aria-label="Toggle sensors"
              aria-pressed={
                showSensors
              }
              title={
                showSensors
                  ? "Hide sensors"
                  : "Show sensors"
              }
            >
              <MapPin className="h-5 w-5" />
            </button>

            {/* HEATMAP */}

            <button
              type="button"
              onClick={() =>
                setShowHeatmap(
                  (value) =>
                    !value,
                )
              }
              className={`rounded-lg border p-3 shadow-lg backdrop-blur transition focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/50 ${
                showHeatmap
                  ? "border-[#38BDF8] bg-[#38BDF8]/20 text-[#38BDF8]"
                  : "border-slate-600 bg-[#0A1B29]/90 text-slate-400"
              }`}
              aria-label="Toggle heatmap"
              aria-pressed={
                showHeatmap
              }
              title={
                showHeatmap
                  ? "Hide heatmap"
                  : "Show heatmap"
              }
            >
              <Layers className="h-5 w-5" />
            </button>
          </div>

          {/* =================================================
              CURRENT OBSERVATION
              ================================================= */}

          {currentFeature && (
            <div className="absolute bottom-4 right-4 z-[400] hidden rounded-lg border border-[#1F2937] bg-[#0A1B29]/95 px-4 py-3 shadow-xl backdrop-blur sm:block">

              <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500">
                Current observation
              </p>

              <div className="mt-1 flex items-baseline gap-2">

                <span className="text-lg font-semibold text-white">
                  {formatValue(
                    currentFeature
                      .properties
                      .value,
                  )}
                </span>

                <span className="text-xs text-slate-500">
                  {currentFeature
                    .properties
                    .unit ||
                    "—"}
                </span>
              </div>

              <p
                className={`mt-1 text-xs ${currentStatus.className}`}
              >
                {currentStatus.label}
              </p>
            </div>
          )}
        </div>
      </section>

      {/* =====================================================
          CITY OVERVIEW
          ===================================================== */}

      <section className="border-b border-[#1F2937] bg-[#050D16] px-5 py-5">

        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-[#38BDF8]">
              City Overview
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Select a city to open its
              intelligence profile.
            </p>
          </div>

          <button
            type="button"
            onClick={downloadCsv}
            disabled={
              features.length === 0
            }
            className="flex items-center gap-2 rounded-lg border border-[#38BDF8]/60 px-4 py-2 text-xs font-semibold text-[#38BDF8] transition hover:bg-[#38BDF8]/10 disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/40"
          >
            <Download className="h-4 w-4" />

            Download CSV
          </button>
        </div>

        {/* CITY CARDS */}

        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">

          {displayedCities.map(
            (item) => {
              const status =
                getPollutionStatus(
                  item.value,
                );

              const isSelected =
                item.city ===
                selectedCity;

              return (
                <button
                  key={item.city}
                  type="button"
                  onClick={() =>
                    handleCitySelect(
                      item.city,
                    )
                  }
                  className={`rounded-lg border p-4 text-left transition focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/50 ${
                    isSelected
                      ? "border-[#38BDF8] bg-[#0C1C2B]"
                      : "border-[#203447] bg-[#091521] hover:border-[#38BDF8]/70 hover:bg-[#0C1C2B]"
                  }`}
                  aria-label={`View air quality details for ${item.city}`}
                >

                  <div className="truncate text-sm font-semibold text-slate-200">
                    {item.city}
                  </div>

                  <div
                    className={`mt-2 text-2xl font-medium ${status.className}`}
                  >
                    {formatValue(
                      item.value,
                    )}
                  </div>

                  <div
                    className={`mt-1 text-xs ${status.className}`}
                  >
                    {status.label}
                  </div>

                </button>
              );
            },
          )}
        </div>

        {displayedCities.length ===
          0 && (
          <p className="py-6 text-center text-sm text-slate-500">
            City data is unavailable.
          </p>
        )}
      </section>

      {/* =====================================================
          INTELLIGENCE SLIDE-OVER
          ===================================================== */}

      {intelligenceOpen && (
        <div className="fixed inset-0 z-[1000] flex justify-end">

          {/* MAP-SIDE OVERLAY */}

          <div
            className="absolute inset-0 bg-black/20"
            onClick={() =>
              setIntelligenceOpen(
                false,
              )
            }
            aria-hidden="true"
          />

          {/* PANEL */}

          <div className="relative z-[1001] h-full w-full max-w-xl border-l border-[#203447] bg-[#071019] shadow-2xl">

            <IntelligenceSidebar
              features={
                selectedFeature
                  ? [selectedFeature]
                  : []
              }
              onClose={() =>
                setIntelligenceOpen(
                  false,
                )
              }
              loading={loading}
              selectedCity={
                selectedCity
              }
            />
          </div>
        </div>
      )}

      {/* =====================================================
          SELECTED CITY INDICATOR
          ===================================================== */}

      {selectedCity &&
        !intelligenceOpen && (
          <button
            type="button"
            onClick={() =>
              setIntelligenceOpen(
                true,
              )
            }
            className="fixed bottom-5 right-5 z-[900] flex items-center gap-2 rounded-full border border-[#38BDF8]/50 bg-[#0A1B29] px-5 py-3 text-sm text-[#38BDF8] shadow-xl focus:outline-none focus:ring-2 focus:ring-[#38BDF8]/50"
          >

            <MapPin className="h-4 w-4" />

            {selectedCity}

            <span
              role="button"
              tabIndex={0}
              aria-label="Clear selected city"
              onClick={(event) => {
                event.stopPropagation();

                setSelectedCity("");
              }}
              onKeyDown={(event) => {
                if (
                  event.key ===
                    "Enter" ||
                  event.key ===
                    " "
                ) {
                  event.preventDefault();

                  event.stopPropagation();

                  setSelectedCity("");
                }
              }}
              className="rounded-full p-1 transition hover:bg-white/10"
            >
              <X className="h-4 w-4" />
            </span>
          </button>
        )}
    </main>
  );
}