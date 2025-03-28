"use client";
import React, { useEffect, useRef } from "react";

const GoogleTrendsWidget = () => {
  const widgetRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window !== "undefined" && widgetRef.current) {
      const script = document.createElement("script");
      script.src =
        "https://ssl.gstatic.com/trends_nrtr/4031_RC01/embed_loader.js";
      script.async = true;
      script.onload = () => {
        // TypeScript fix: Declare trends as any
        const trends = (window as any).trends;

        if (trends && trends.embed) {
          trends.embed.renderExploreWidgetTo(
            widgetRef.current,
            "RELATED_QUERIES",
            {
              comparisonItem: [{ geo: "IN", time: "today 12-m" }],
              category: 0,
              property: "",
            },
            {
              exploreQuery: "geo=IN&hl=en&date=today 12-m",
              guestPath: "https://trends.google.com:443/trends/embed/",
            }
          );
        }
      };
      document.body.appendChild(script);
    }
  }, []);

  return <div ref={widgetRef} className="w-full h-[500px]" />;
};

export default GoogleTrendsWidget;
