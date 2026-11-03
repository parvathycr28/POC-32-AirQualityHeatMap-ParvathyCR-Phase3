import Link from "next/link";

const links = [
  { label: "Map", href: "/" },
  { label: "Data Intelligence", href: "/data-intelligence" },
  { label: "Assistant", href: "/assistant" },
];

export default function PrimaryNavigation({
  current,
}: {
  current: "map" | "intelligence" | "assistant";
}) {
  return (
    <nav
      aria-label="Primary navigation"
      className="flex flex-wrap items-center gap-2"
    >
      {links.map((link) => {
        const active =
          (current === "map" && link.href === "/") ||
          (current === "intelligence" &&
            link.href === "/data-intelligence") ||
          (current === "assistant" && link.href === "/assistant");

        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={active ? "page" : undefined}
            className={`rounded-lg border px-3 py-2 text-xs font-medium transition ${
              active
                ? "border-sky-400/40 bg-sky-400/10 text-sky-300"
                : "border-slate-700 text-slate-400 hover:border-sky-400/40 hover:text-sky-300"
            }`}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}