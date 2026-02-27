export default function SignalBadge({ signal, size = "md" }) {
  const config = {
    APPLY:   { color: "#00e6a1", bg: "rgba(0,230,161,0.1)",   border: "rgba(0,230,161,0.25)"  },
    AVOID:   { color: "#ef4444", bg: "rgba(239,68,68,0.1)",   border: "rgba(239,68,68,0.25)"  },
    NEUTRAL: { color: "#4a9eff", bg: "rgba(74,158,255,0.1)",  border: "rgba(74,158,255,0.25)" },
  };

  const c = config[signal] || config.NEUTRAL;

  const padding = size === "lg" ? "6px 16px" : "3px 10px";
  const fontSize = size === "lg" ? "12px" : "10px";

  return (
    <span style={{
      display:        "inline-flex",
      alignItems:     "center",
      gap:            "6px",
      padding,
      borderRadius:   "999px",
      fontSize,
      fontFamily:     "'JetBrains Mono', monospace",
      fontWeight:     700,
      letterSpacing:  "1px",
      textTransform:  "uppercase",
      background:     c.bg,
      color:          c.color,
      border:         `1px solid ${c.border}`,
    }}>
      <span style={{
        width:        "6px",
        height:       "6px",
        borderRadius: "50%",
        background:   c.color,
        flexShrink:   0,
      }} />
      {signal}
    </span>
  );
}