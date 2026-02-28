import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import SignalBadge from "./SignalBadge";

const PAGE_SIZE = 20;

function sigColor(s) { return s==="APPLY"?"#00e6a1":s==="AVOID"?"#ef4444":"#4a9eff"; }
function confColor(c){ return c==="HIGH"?"#eab308":c==="MEDIUM"?"#a855f7":"#475569"; }
function confBg(c)   { return c==="HIGH"?"rgba(234,179,8,0.1)":c==="MEDIUM"?"rgba(168,85,247,0.1)":"rgba(71,85,105,0.1)"; }
function sentColor(v){ return v>0.05?"#00e6a1":v<-0.05?"#ef4444":"#475569"; }
function gmpColor(v) {
  if (v === null || v === undefined) return "#475569";
  return v > 0 ? "#00e6a1" : v < 0 ? "#ef4444" : "#475569";
}

export default function IPOTable({ data, loading }) {
  const navigate = useNavigate();
  const [signal, setSignal] = useState("ALL");
  const [conf,   setConf]   = useState("ALL");
  const [sort,   setSort]   = useState("score_desc");
  const [search, setSearch] = useState("");
  const [page,   setPage]   = useState(1);

  const filtered = useMemo(() => {
    let d = [...data];
    if (signal !== "ALL") d = d.filter(x => x.signal === signal);
    if (conf   !== "ALL") d = d.filter(x => x.confidence === conf);
    if (search) d = d.filter(x => x.ipo_name.toLowerCase().includes(search.toLowerCase()));
    d.sort((a, b) => {
      if (sort === "score_desc")    return b.final_score - a.final_score;
      if (sort === "score_asc")     return a.final_score - b.final_score;
      if (sort === "articles_desc") return b.article_count - a.article_count;
      if (sort === "gmp_desc")      return (b.gmp ?? -9999) - (a.gmp ?? -9999);
      if (sort === "name_asc")      return a.ipo_name.localeCompare(b.ipo_name);
      return 0;
    });
    return d;
  }, [data, signal, conf, sort, search]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const slice      = filtered.slice((page-1)*PAGE_SIZE, page*PAGE_SIZE);

  const btnStyle = (active, color="#00e6a1") => ({
    padding: "8px 16px", borderRadius: "8px", fontSize: "13px",
    fontWeight: 700, cursor: "pointer",
    border:  active ? `1px solid ${color}40` : "1px solid #1f2937",
    background: active ? `${color}15` : "#0d1117",
    color:   active ? color : "#64748b",
    transition: "all 0.15s",
  });

  const selStyle = {
    background: "#0d1117", border: "1px solid #1f2937",
    borderRadius: "8px", padding: "8px 12px",
    color: "#94a3b8", fontSize: "13px", outline: "none", cursor: "pointer",
  };

  const thStyle = {
    padding: "14px 16px", textAlign: "left", fontSize: "10px",
    fontWeight: 800, letterSpacing: "1.5px", textTransform: "uppercase",
    color: "#475569", fontFamily: "'JetBrains Mono', monospace", whiteSpace: "nowrap",
  };

  return (
    <div>
      {/* Controls */}
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:"16px", flexWrap:"wrap", gap:"10px" }}>
        <div style={{ display:"flex", gap:"8px", flexWrap:"wrap" }}>
          {["ALL","APPLY","NEUTRAL","AVOID"].map(s => (
            <button key={s} onClick={() => { setSignal(s); setPage(1); }}
              style={btnStyle(signal===s, s==="APPLY"?"#00e6a1":s==="AVOID"?"#ef4444":s==="NEUTRAL"?"#4a9eff":"#e2e8f0")}>
              {s==="ALL" ? "All Signals" : s[0]+s.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
        <div style={{ display:"flex", gap:"8px", alignItems:"center", flexWrap:"wrap" }}>
          <div style={{ position:"relative" }}>
            <span style={{ position:"absolute", left:"10px", top:"50%", transform:"translateY(-50%)", color:"#475569" }}>⌕</span>
            <input type="text" placeholder="Search IPO..." value={search}
              onChange={e => { setSearch(e.target.value); setPage(1); }}
              style={{ ...selStyle, paddingLeft:"30px", width:"170px" }}/>
          </div>
          <select value={conf} onChange={e => { setConf(e.target.value); setPage(1); }} style={selStyle}>
            <option value="ALL">All Confidence</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
          <select value={sort} onChange={e => setSort(e.target.value)} style={selStyle}>
            <option value="score_desc">Score ↓</option>
            <option value="score_asc">Score ↑</option>
            <option value="articles_desc">Articles ↓</option>
            <option value="gmp_desc">GMP ↓</option>
            <option value="name_asc">Name A–Z</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div style={{ background:"#0d1117", border:"1px solid #1f2937", borderRadius:"12px", overflow:"hidden" }}>
        <table style={{ width:"100%", borderCollapse:"collapse" }}>
          <thead>
            <tr style={{ background:"rgba(15,23,42,0.6)", borderBottom:"1px solid #1f2937" }}>
              <th style={thStyle}>#</th>
              <th style={thStyle}>IPO Name</th>
              <th style={thStyle}>Signal</th>
              <th style={thStyle}>Confidence</th>
              <th style={{ ...thStyle, cursor:"pointer" }} onClick={() => setSort("score_desc")}>Score ↕</th>
              <th style={{ ...thStyle, cursor:"pointer" }} onClick={() => setSort("gmp_desc")}>
                GMP ↕
                <span style={{ marginLeft:"4px", fontSize:"8px", color:"#a855f7", letterSpacing:"0.5px" }}>LIVE</span>
              </th>
              <th style={{ ...thStyle, cursor:"pointer" }} onClick={() => setSort("articles_desc")}>Articles ↕</th>
              <th style={thStyle}>Sentiment</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} style={{ padding:"60px", textAlign:"center", color:"#374151" }}>Loading...</td></tr>
            ) : !slice.length ? (
              <tr><td colSpan={8} style={{ padding:"60px", textAlign:"center", color:"#374151" }}>No IPOs match your filters</td></tr>
            ) : slice.map((d, i) => {
              const rank     = (page-1)*PAGE_SIZE + i + 1;
              const initials = d.ipo_name.split(" ").slice(0,2).map(w=>w[0]).join("");
              const sentPct  = (d.avg_sentiment_score * 100).toFixed(1);
              const sign     = d.avg_sentiment_score >= 0 ? "+" : "";
              const hasGMP   = d.gmp !== null && d.gmp !== undefined;
              const gmpSign  = hasGMP && d.gmp > 0 ? "+" : "";

              return (
                <tr key={d.ipo_name}
                  onClick={() => navigate(`/ipo/${encodeURIComponent(d.ipo_name)}`)}
                  style={{ borderBottom:"1px solid #1f2937", cursor:"pointer", transition:"background 0.12s" }}
                  onMouseEnter={e => e.currentTarget.style.background="rgba(255,255,255,0.02)"}
                  onMouseLeave={e => e.currentTarget.style.background="transparent"}
                >
                  <td style={{ padding:"12px 16px", color:"#374151", fontSize:"11px", fontFamily:"'JetBrains Mono',monospace" }}>
                    {String(rank).padStart(2,"0")}
                  </td>
                  <td style={{ padding:"12px 16px" }}>
                    <div style={{ display:"flex", alignItems:"center", gap:"10px" }}>
                      <div style={{
                        width:"34px", height:"34px", borderRadius:"8px", flexShrink:0,
                        display:"flex", alignItems:"center", justifyContent:"center",
                        fontSize:"11px", fontWeight:800,
                        background:`rgba(${d.signal==="APPLY"?"0,230,161":d.signal==="AVOID"?"239,68,68":"74,158,255"},0.1)`,
                        color: sigColor(d.signal),
                      }}>{initials}</div>
                      <div>
                        <p style={{ color:"#f1f5f9", fontWeight:700, fontSize:"13px", fontFamily:"Manrope,sans-serif" }}>{d.ipo_name}</p>
                        <p style={{ color:"#374151", fontSize:"10px", textTransform:"uppercase", letterSpacing:"0.8px" }}>{d.article_count} articles</p>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding:"12px 16px" }}>
                    <SignalBadge signal={d.signal} />
                  </td>
                  <td style={{ padding:"12px 16px" }}>
                    <span style={{
                      padding:"3px 8px", borderRadius:"4px", fontSize:"10px",
                      fontWeight:800, letterSpacing:"0.5px", textTransform:"uppercase",
                      fontFamily:"'JetBrains Mono',monospace",
                      background: confBg(d.confidence), color: confColor(d.confidence),
                      border: `1px solid ${confColor(d.confidence)}40`,
                    }}>{d.confidence}</span>
                  </td>
                  <td style={{ padding:"12px 16px" }}>
                    <div style={{ display:"flex", alignItems:"center", gap:"8px" }}>
                      <div style={{ width:"70px", height:"4px", background:"#1f2937", borderRadius:"2px", overflow:"hidden" }}>
                        <div style={{ height:"100%", borderRadius:"2px", width:`${d.final_score*100}%`, background:sigColor(d.signal) }}/>
                      </div>
                      <span style={{ color:"#f1f5f9", fontSize:"12px", fontWeight:700, fontFamily:"'JetBrains Mono',monospace" }}>
                        {d.final_score.toFixed(3)}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding:"12px 16px" }}>
                    {hasGMP ? (
                      <div style={{ display:"flex", alignItems:"center", gap:"6px" }}>
                        <span style={{
                          color: gmpColor(d.gmp), fontSize:"13px", fontWeight:700,
                          fontFamily:"'JetBrains Mono',monospace",
                        }}>
                          {gmpSign}₹{d.gmp}
                        </span>
                        {d.gmp_percent != null && (
                          <span style={{
                            fontSize:"10px", color: gmpColor(d.gmp),
                            background: `${gmpColor(d.gmp)}15`,
                            padding:"1px 5px", borderRadius:"4px",
                            fontFamily:"'JetBrains Mono',monospace",
                          }}>
                            {d.gmp > 0 ? "+" : ""}{Number(d.gmp_percent).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    ) : (
                      <span style={{ color:"#374151", fontSize:"12px", fontFamily:"'JetBrains Mono',monospace" }}>—</span>
                    )}
                  </td>
                  <td style={{ padding:"12px 16px", color:"#64748b", fontSize:"13px", fontFamily:"'JetBrains Mono',monospace" }}>
                    {d.article_count}
                  </td>
                  <td style={{ padding:"12px 16px" }}>
                    <span style={{ color:sentColor(d.avg_sentiment_score), fontSize:"13px", fontWeight:700, fontFamily:"'JetBrains Mono',monospace" }}>
                      {sign}{sentPct}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {/* Pagination */}
        <div style={{ padding:"10px 16px", background:"rgba(15,23,42,0.4)", borderTop:"1px solid #1f2937", display:"flex", alignItems:"center", justifyContent:"space-between" }}>
          <span style={{ color:"#374151", fontSize:"11px", fontFamily:"'JetBrains Mono',monospace" }}>
            {filtered.length} IPOs · Page {page} of {totalPages}
          </span>
          <div style={{ display:"flex", gap:"6px" }}>
            <button onClick={() => setPage(p => Math.max(1,p-1))} disabled={page===1}
              style={{ padding:"4px 10px", borderRadius:"6px", background:"#1f2937", border:"none", color:page===1?"#374151":"#94a3b8", fontSize:"11px", cursor:page===1?"default":"pointer" }}>
              ← Prev
            </button>
            <button onClick={() => setPage(p => Math.min(totalPages,p+1))} disabled={page===totalPages}
              style={{ padding:"4px 10px", borderRadius:"6px", background:"#1f2937", border:"none", color:page===totalPages?"#374151":"#94a3b8", fontSize:"11px", cursor:page===totalPages?"default":"pointer" }}>
              Next →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}