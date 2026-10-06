"use client";

import {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";

type CitySearchSelectProps = {
  cities: string[];
  value: string;
  onChange: (city: string) => void;
  placeholder?: string;
};

export default function CitySearchSelect({
  cities,
  value,
  onChange,
  placeholder = "Search/select city",
}: CitySearchSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [activeIndex, setActiveIndex] =
    useState(-1);

  const containerRef =
    useRef<HTMLDivElement>(null);

  const inputRef =
    useRef<HTMLInputElement>(null);

  const listboxId = useId();

  const filteredCities = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return cities;
    }

    return cities.filter((city) =>
      city.toLowerCase().includes(query),
    );
  }, [cities, search]);

  /*
   * Close dropdown when clicking outside.
   */
  useEffect(() => {
    function handleClickOutside(
      event: MouseEvent,
    ) {
      if (
        containerRef.current &&
        !containerRef.current.contains(
          event.target as Node,
        )
      ) {
        setOpen(false);
        setActiveIndex(-1);
        setSearch("");
      }
    }

    document.addEventListener(
      "mousedown",
      handleClickOutside,
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleClickOutside,
      );
    };
  }, []);

  /*
   * Open the dropdown.
   */
  function handleOpen() {
    setOpen(true);
    setSearch("");
    setActiveIndex(
      cities.length > 0 ? 0 : -1,
    );
  }

  /*
   * Select a city.
   */
  function handleSelect(city: string) {
    onChange(city);
    setSearch("");
    setOpen(false);
    setActiveIndex(-1);
  }

  /*
   * Keyboard navigation.
   */
  function handleKeyDown(
    event: KeyboardEvent<HTMLInputElement>,
  ) {
    if (!open) {
      if (
        event.key === "ArrowDown" ||
        event.key === "Enter" ||
        event.key === " "
      ) {
        event.preventDefault();
        handleOpen();
      }

      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();

      if (filteredCities.length === 0) {
        return;
      }

      setActiveIndex((current) => {
        if (
          current >=
          filteredCities.length - 1
        ) {
          return 0;
        }

        return current + 1;
      });

      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();

      if (filteredCities.length === 0) {
        return;
      }

      setActiveIndex((current) => {
        if (current <= 0) {
          return (
            filteredCities.length - 1
          );
        }

        return current - 1;
      });

      return;
    }

    if (event.key === "Home") {
      event.preventDefault();

      if (filteredCities.length > 0) {
        setActiveIndex(0);
      }

      return;
    }

    if (event.key === "End") {
      event.preventDefault();

      if (filteredCities.length > 0) {
        setActiveIndex(
          filteredCities.length - 1,
        );
      }

      return;
    }

    if (event.key === "Enter") {
      event.preventDefault();

      if (
        activeIndex >= 0 &&
        activeIndex <
          filteredCities.length
      ) {
        handleSelect(
          filteredCities[activeIndex],
        );
      }

      return;
    }

    if (event.key === "Escape") {
      event.preventDefault();

      setOpen(false);
      setSearch("");
      setActiveIndex(-1);

      return;
    }
  }

  const activeCity =
    activeIndex >= 0 &&
    activeIndex < filteredCities.length
      ? filteredCities[activeIndex]
      : undefined;

  return (
    <div
      ref={containerRef}
      className="relative w-full sm:w-64"
    >
      {/* SEARCH / SELECT CONTROL */}
      <input
        ref={inputRef}
        type="text"
        role="combobox"
        aria-label={placeholder}
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-controls={listboxId}
        aria-autocomplete="list"
        aria-activedescendant={
          activeCity
            ? `${listboxId}-option-${activeIndex}`
            : undefined
        }
        value={open ? search : value}
        onFocus={handleOpen}
        onClick={handleOpen}
        onChange={(event) => {
          setSearch(event.target.value);
          setOpen(true);
          setActiveIndex(
            event.target.value
              ? 0
              : cities.length > 0
                ? 0
                : -1,
          );
        }}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="h-14 w-full rounded-lg border border-[#1F2937] bg-[#0B1117] px-4 text-sm text-white outline-none placeholder:text-slate-500 transition focus:border-[#38BDF8] focus:ring-1 focus:ring-[#38BDF8]/30"
      />

      {/* DROPDOWN */}
      {open && (
        <div
          id={listboxId}
          role="listbox"
          aria-label={`${placeholder} options`}
          className="absolute left-0 top-full z-[1000] mt-1 max-h-72 w-full overflow-y-auto rounded-lg border border-[#1F2937] bg-[#0B1117] shadow-2xl"
        >
          {filteredCities.length === 0 ? (
            <div className="px-4 py-4 text-sm text-slate-500">
              No cities found
            </div>
          ) : (
            filteredCities.map(
              (city, index) => {
                const isSelected =
                  city === value;

                const isActive =
                  index === activeIndex;

                return (
                  <button
                    key={city}
                    id={`${listboxId}-option-${index}`}
                    type="button"
                    role="option"
                    aria-selected={
                      isSelected
                    }
                    onMouseEnter={() =>
                      setActiveIndex(
                        index,
                      )
                    }
                    onMouseDown={(
                      event,
                    ) => {
                      event.preventDefault();
                    }}
                    onClick={() =>
                      handleSelect(
                        city,
                      )
                    }
                    className={`block w-full px-4 py-3 text-left text-sm transition ${
                      isActive
                        ? "bg-[#111827] text-white"
                        : isSelected
                          ? "bg-[#0D1722] text-[#38BDF8]"
                          : "text-slate-300 hover:bg-[#111827] hover:text-white"
                    }`}
                  >
                    <span className="block truncate">
                      {city}
                    </span>
                  </button>
                );
              },
            )
          )}
        </div>
      )}
    </div>
  );
}