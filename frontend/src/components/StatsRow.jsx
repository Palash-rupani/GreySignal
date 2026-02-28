import { useStats } from "../hooks/useIPOData";

const cards = [
  { key: "total",       label: "Total IPOs",  color: "#00e6a1", sub: "tracked this session" },
  { key: "apply",       label: "Apply",       color: "#00e6a1", sub: "positive signal"       },
  { key: "neutral",     label: "Neutral",     color: "#4a9eff", sub: "watch & wait"          },
  { key: "avoid",       label: "Avoid",       color: "#ef4444", sub: "negative sentiment"    },
  { key: "articles",    label: "Articles",    color: "#eab308", sub: "news analyzed"         },
  { key: "gmp_tracked", label: "GMP Data",    color: "#a855f7", sub: "with live GMP"         },
];

export default function StatsRow() {
  const { stats, loading } = useStats();

  return (
    <div style={{
      display:             "grid",
      gridTemplateColumns: "repeat(6, minmax(0, 1fr))",
      gap:                 "14px",
      width:               "100%",
    }}>
      {cards.map(card => (
        <div key={card.key} style={{
          background:   "#0d1117",
          border:       "1px solid #1f2937",
          borderTop:    `2px solid ${card.color}`,
          borderRadius: "12px",
          padding:      "16px 20px",
        }}>
          <p style={{
            color:         "#475569",
            fontSize:      "10px",
            fontWeight:    800,
            letterSpacing: "1.5px",
            textTransform: "uppercase",
            marginBottom:  "8px",
            fontFamily:    "'JetBrains Mono', monospace",
          }}>
            {card.label}
          </p>
          <p style={{
            color:        card.color,
            fontSize:     "32px",
            fontWeight:   800,
            lineHeight:   1,
            fontFamily:   "Manrope, sans-serif",
            marginBottom: "4px",
          }}>
            {loading ? "—" : (stats?.[card.key] ?? "—").toLocaleString()}
          </p>
          <p style={{ color: "#374151", fontSize: "11px" }}>{card.sub}</p>
        </div>
      ))}
    </div>
  );
}