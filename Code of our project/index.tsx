import { createFileRoute } from "@tanstack/react-router";
import { Explorer } from "@/components/Explorer";
import { Landing } from "@/components/Landing";

type Search = { world?: "moon" | "mars" };

export const Route = createFileRoute("/")({
  ssr: false,
  validateSearch: (s: Record<string, unknown>): Search => {
    const w = s["world"];
    return w === "mars" || w === "moon" ? { world: w } : {};
  },
  head: ({ match }) => {
    const world = (match.search as Search).world;
    const name = world === "mars" ? "Mars" : world === "moon" ? "Moon" : null;
    const title = name ? `${name} Explorer · Space2Earth` : "Space2Earth · Your adventure to the Moon or Mars starts on Earth";
    const description = name
      ? `Pick a ${name} region and find matching Earth analog places, search ${name} from Earth, or get landing recommendations.`
      : "Select a region on the 3D Moon or Mars, choose criteria, and see the closest Earth analog places on a second globe.";
    return {
      meta: [
        { title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        { property: "og:type", content: "website" },
        { name: "twitter:card", content: "summary_large_image" },
      ],
    };
  },
  component: Page,
});

function Page() {
  const { world } = Route.useSearch();
  return world ? <Explorer world={world} /> : <Landing />;
}
