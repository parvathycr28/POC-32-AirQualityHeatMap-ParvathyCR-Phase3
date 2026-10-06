"use client";

import { useEffect, useState } from "react";

import {
  Circle,
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";

import type { LatLngBoundsExpression } from "leaflet";

import "leaflet/dist/leaflet.css";

import {
  getPopulation,
  type AirQualityFeature,
} from "../lib/api";

type LeafletMapProps = {
  features: AirQualityFeature[];
  pollutant: string;
  onCitySelect?: (city: string) => void;
  showSensors?: boolean;
  showHeatmap?: boolean;
};

/* =========================================================
   POLLUTION COLOR
   ========================================================= */

function getPollutionColor(
  value: number | null | undefined,
): string {
  if (
    value == null ||
    !Number.isFinite(value)
  ) {
    return "#64748B";
  }

  if (value <= 12) {
    return "#22C55E";
  }

  if (value <= 35) {
    return "#FACC15";
  }

  if (value <= 55) {
    return "#F97316";
  }

  if (value <= 150) {
    return "#EF4444";
  }

  return "#A855F7";
}

/* =========================================================
   HEATMAP RADIUS
   ========================================================= */

function getHeatmapRadius(
  value: number | null | undefined,
): number {
  if (
    value == null ||
    !Number.isFinite(value)
  ) {
    return 50000;
  }

  if (value <= 12) {
    return 45000;
  }

  if (value <= 35) {
    return 70000;
  }

  if (value <= 55) {
    return 90000;
  }

  if (value <= 150) {
    return 120000;
  }

  return 160000;
}

/* =========================================================
   FIT MAP TO FEATURES
   ========================================================= */

function FitMapToFeatures({
  features,
}: {
  features: AirQualityFeature[];
}) {
  const map = useMap();

  useEffect(() => {
    const points = features
      .map(
        (feature) =>
          feature.geometry.coordinates,
      )
      .filter(
        (
          coordinates,
        ): coordinates is [
          number,
          number,
        ] =>
          Array.isArray(coordinates) &&
          coordinates.length >= 2 &&
          Number.isFinite(
            coordinates[0],
          ) &&
          Number.isFinite(
            coordinates[1],
          ),
      )
      .map(
        ([longitude, latitude]) =>
          [
            latitude,
            longitude,
          ] as [number, number],
      );

    if (points.length === 0) {
      return;
    }

    const bounds: LatLngBoundsExpression =
      points;

    map.fitBounds(bounds, {
      padding: [50, 50],
      maxZoom: 4,
    });
  }, [features, map]);

  return null;
}

/* =========================================================
   MAIN LEAFLET MAP
   ========================================================= */

export default function LeafletMap({
  features,
  pollutant,
  onCitySelect,
  showSensors = true,
  showHeatmap = false,
}: LeafletMapProps) {
  /*
   * IMPORTANT:
   * This state MUST remain inside the component.
   * Keeping it here avoids the Invalid Hook Call error.
   */

  const [
    populationByPoint,
    setPopulationByPoint,
  ] = useState<
    Record<string, number | null>
  >({});

  /* =======================================================
     VALID FEATURES
     ======================================================= */

  const markers = features.filter(
    (feature) => {
      const [
        longitude,
        latitude,
      ] =
        feature.geometry.coordinates;

      return (
        Number.isFinite(latitude) &&
        Number.isFinite(longitude) &&
        latitude >= -90 &&
        latitude <= 90 &&
        longitude >= -180 &&
        longitude <= 180
      );
    },
  );

  return (
    <MapContainer
      center={[20, 0]}
      zoom={2}
      minZoom={2}
      scrollWheelZoom={true}
      className="h-full w-full bg-[#030712]"
    >
      {/* ===================================================
          BASE MAP
          =================================================== */}

      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* ===================================================
          AUTOMATIC MAP FIT
          =================================================== */}

      <FitMapToFeatures
        features={markers}
      />

      {/* ===================================================
          HEATMAP / INTENSITY LAYER
          =================================================== */}

      {showHeatmap &&
        markers.map(
          (feature, index) => {
            const [
              longitude,
              latitude,
            ] =
              feature.geometry.coordinates;

            const value =
              feature.properties.value;

            const color =
              getPollutionColor(
                value,
              );

            const radius =
              getHeatmapRadius(
                value,
              );

            return (
              <Circle
                key={`heat-${latitude}-${longitude}-${index}`}
                center={[
                  latitude,
                  longitude,
                ]}
                radius={radius}
                pathOptions={{
                  color,
                  fillColor: color,
                  fillOpacity: 0.12,
                  opacity: 0.25,
                  weight: 1,
                }}
              />
            );
          },
        )}

      {/* ===================================================
          SENSOR MARKERS
          =================================================== */}

      {showSensors &&
        markers.map(
          (feature, index) => {
            const [
              longitude,
              latitude,
            ] =
              feature.geometry.coordinates;

            const properties =
              feature.properties;

            const pointKey =
              `${latitude},${longitude}`;

            /*
             * IMPORTANT:
             *
             * First use population already returned
             * with the air-quality feature.
             *
             * Only use the locally loaded population
             * when the backend did not provide one.
             */

            const population =
              populationByPoint[
                pointKey
              ] ??
              properties.population ??
              null;

            const pollutionColor =
              getPollutionColor(
                properties.value,
              );

            return (
              <CircleMarker
                key={`${properties.city}-${pointKey}-${index}`}
                center={[
                  latitude,
                  longitude,
                ]}
                radius={7}
                pathOptions={{
                  color: "#E5F7FF",
                  fillColor:
                    pollutionColor,
                  fillOpacity: 0.95,
                  opacity: 1,
                  weight: 1.5,
                }}
                eventHandlers={{
                  click: () => {
                    if (
                      properties.city &&
                      onCitySelect
                    ) {
                      onCitySelect(
                        properties.city,
                      );
                    }
                  },
                }}
              >
                {/* =========================================
                    AIR QUALITY POPUP
                    ========================================= */}

                <Popup
                  closeButton={true}
                  className="air-quality-popup"
                >
                  <div className="w-[260px] overflow-hidden rounded-lg bg-[#071019] text-white">
                    {/* =====================================
                        HEADER
                        ===================================== */}

                    <div className="border-b border-[#1F2937] px-4 pb-3 pt-4">
                      <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-[#7F9AB0]">
                        AIR QUALITY
                      </p>

                      <h3 className="mt-2 text-[17px] font-bold leading-tight text-white">
                        {properties.city ||
                          "Unknown location"}
                      </h3>

                      {properties.country && (
                        <p className="mt-1 text-xs text-[#8EA6B8]">
                          {
                            properties.country
                          }
                        </p>
                      )}
                    </div>

                    {/* =====================================
                        POLLUTANT / VALUE
                        ===================================== */}

                    <div className="grid grid-cols-2 gap-4 border-b border-[#1F2937] px-4 py-4">
                      <div>
                        <p className="text-xs text-[#8EA6B8]">
                          Pollutant
                        </p>

                        <p className="mt-1 text-[16px] font-bold text-white">
                          {properties.pollutant ||
                            pollutant ||
                            "PM2.5"}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs text-[#8EA6B8]">
                          Value
                        </p>

                        <p
                          className="mt-1 text-[16px] font-bold"
                          style={{
                            color:
                              pollutionColor,
                          }}
                        >
                          {properties.value !=
                          null
                            ? Number(
                                properties.value,
                              ).toFixed(2)
                            : "—"}{" "}
                          {properties.unit ||
                            "µg/m³"}
                        </p>
                      </div>
                    </div>

                    {/* =====================================
                        TIMESTAMP
                        ===================================== */}

                    {properties.timestamp && (
                      <div className="border-b border-[#1F2937] px-4 py-4">
                        <p className="text-xs text-[#8EA6B8]">
                          Timestamp
                        </p>

                        <p className="mt-1 break-all text-[14px] font-semibold text-white">
                          {
                            properties.timestamp
                          }
                        </p>
                      </div>
                    )}

                    {/* =====================================
                        EXPOSURE / POPULATION
                        ===================================== */}

                    <div className="grid grid-cols-2 gap-4 border-b border-[#1F2937] px-4 py-4">
                      {/* EXPOSURE */}

                      <div>
                        <p className="text-xs text-[#8EA6B8]">
                          Exposure
                        </p>

                        <p className="mt-1 text-[18px] font-bold text-[#38BDF8]">
                          {properties.exposure_score ??
                            "—"}
                        </p>
                      </div>

                      {/* POPULATION */}

                      <div>
                        <p className="text-xs text-[#8EA6B8]">
                          Population
                        </p>

                        {population != null ? (
                          <p className="mt-1 text-[14px] font-bold text-[#38BDF8]">
                            {Number(
                              population,
                            ).toLocaleString()}
                          </p>
                        ) : (
                          <button
                            type="button"
                            className="mt-1 text-left text-[14px] font-semibold text-[#38BDF8] underline decoration-[#38BDF8]/50 underline-offset-2 transition hover:text-white"
                            onClick={async () => {
                              try {
                                const result =
                                  await getPopulation(
                                    latitude,
                                    longitude,
                                  );

                                if (
                                  result !=
                                    null &&
                                  Number.isFinite(
                                    result,
                                  )
                                ) {
                                  setPopulationByPoint(
                                    (
                                      current,
                                    ) => ({
                                      ...current,
                                      [pointKey]:
                                        result,
                                    }),
                                  );
                                } else {
                                  console.warn(
                                    "Population data unavailable for this location.",
                                  );
                                }
                              } catch (
                                error
                              ) {
                                console.error(
                                  "Population request failed:",
                                  error,
                                );
                              }
                            }}
                          >
                            Load population
                          </button>
                        )}
                      </div>
                    </div>

                    {/* =====================================
                        REGIONAL AVERAGE
                        ===================================== */}

                    <div className="px-4 py-4">
                      <p className="text-xs text-[#8EA6B8]">
                        Regional Average
                      </p>

                      <p className="mt-1 text-[16px] font-bold text-[#38BDF8]">
                        {properties.regional_average !=
                        null
                          ? `${Number(
                              properties.regional_average,
                            ).toFixed(
                              1,
                            )} ${
                              properties.unit ||
                              "µg/m³"
                            }`
                          : "Unavailable"}
                      </p>
                    </div>

                    {/* =====================================
                        FALLBACK NOTICE
                        ===================================== */}

                    {properties.fallback && (
                      <div className="mx-4 mb-4 rounded-md border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-xs text-yellow-300">
                        Fallback data is
                        being displayed.
                      </div>
                    )}

                    {/* =====================================
                        CITY INTELLIGENCE
                        ===================================== */}

                    {properties.city &&
                      onCitySelect && (
                        <div className="px-4 pb-4">
                          <button
                            type="button"
                            onClick={() =>
                              onCitySelect(
                                properties.city,
                              )
                            }
                            className="w-full rounded-md border border-[#38BDF8]/60 bg-[#38BDF8]/10 px-3 py-2 text-sm font-semibold text-[#38BDF8] transition hover:bg-[#38BDF8]/20 hover:text-white"
                          >
                            View city
                            intelligence
                          </button>
                        </div>
                      )}
                  </div>
                </Popup>
              </CircleMarker>
            );
          },
        )}
    </MapContainer>
  );
}