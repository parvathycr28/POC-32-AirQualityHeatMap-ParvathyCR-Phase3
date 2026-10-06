"use client";

import { Info, X } from "lucide-react";
import { useState } from "react";

export default function InfocreonHeader() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <header className="pointer-events-none absolute inset-x-0 top-0 z-[1000] flex items-center justify-between border-b border-white/10 bg-[#06131b]/75 px-6 py-4 backdrop-blur-md">
        {/* BRAND */}
        <div className="pointer-events-auto">
          <div className="text-[10px] font-medium uppercase tracking-[0.28em] text-[#38BDF8]">
            INFOCREON INTERNSHIP POC-32
          </div>

          <div className="mt-1 text-sm font-semibold tracking-tight text-white">
            INTELLIGENCE LIBRARY
          </div>
        </div>

        {/* PROJECT TITLE */}
        <div className="hidden text-center md:block">
          <h1 className="text-sm font-semibold text-slate-100">
            Air Quality Heatmap
          </h1>

          <p className="mt-1 text-[10px] uppercase tracking-[0.18em] text-slate-400">
            Data & Intelligence
          </p>
        </div>

        {/* INFO BUTTON */}
        <button
          type="button"
          aria-label="Open project information"
          onClick={() => setOpen(true)}
          className="pointer-events-auto flex h-9 w-9 items-center justify-center rounded-full border border-white/15 bg-white/5 text-slate-300 transition hover:border-[#38BDF8] hover:text-[#38BDF8]"
        >
          <Info size={16} />
        </button>
      </header>

      {/* METADATA MODAL */}
      {open && (
        <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-xl border border-[#1f3744] bg-[#0b1b24] p-6 shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] uppercase tracking-[0.2em] text-[#38BDF8]">
                  INFOCREON SIGNATURE
                </p>

                <h2 className="mt-2 text-lg font-semibold text-white">
                  Project Metadata
                </h2>
              </div>

              <button
                type="button"
                aria-label="Close project information"
                onClick={() => setOpen(false)}
                className="text-slate-400 transition hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            <div className="mt-6 space-y-4 text-sm">
              <MetadataRow
                label="Architect"
                value="Parvathy C R"
              />

              <MetadataRow
                label="Batch"
                value="8,MA College"
              />

              <MetadataRow
                label="Rail"
                value="Data & Intelligence"
              />

              <MetadataRow
                label="Stack"
                value="Next.js, FastAPI, Tailwind CSS, Leaflet, Recharts"
              />
            </div>

            <div className="mt-6 border-t border-[#1f3744] pt-4 text-xs leading-5 text-slate-500">
              Intelligence Library
              <br />
              Air Quality Heatmap
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function MetadataRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="border-b border-white/5 pb-3">
      <p className="text-[10px] uppercase tracking-wider text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-slate-200">
        {value}
      </p>
    </div>
  );
}