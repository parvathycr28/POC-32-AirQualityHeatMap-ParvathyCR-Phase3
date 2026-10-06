"use client";

import dynamic from "next/dynamic";
import type { AirQualityFeature } from "../lib/api";

const LeafletMap = dynamic(() => import("./leaflet-map"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center bg-[#030712] text-sm text-slate-400">
      Initializing map...
    </div>
  ),
});

type AirQualityMapProps = {
  features: AirQualityFeature[];
  pollutant: string;
  onCitySelect?: (city: string) => void;
  showSensors?: boolean;
  showHeatmap?: boolean;
};

export default function AirQualityMap({
  features,
  pollutant,
  onCitySelect,
  showSensors = true,
  showHeatmap = true,
}: AirQualityMapProps) {
  return (
    <LeafletMap
      features={features}
      pollutant={pollutant}
      onCitySelect={onCitySelect}
      showSensors={showSensors}
      showHeatmap={showHeatmap}
    />
  );
}