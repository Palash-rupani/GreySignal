import { useParams, useNavigate } from "react-router-dom";
import { useIPODetail } from "../hooks/useIPOData";
import SignalBadge from "../components/SignalBadge";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

function sigColor(s) { return s==="APPLY"?"#00e6a1":s==="AVOID"?"#ef4444":"#4a9eff"; }
function confColor(c){ return c==="HIGH"?"#eab308":c==="MEDIUM"?"#a855f7":"#475569"; }
function sentColor(v){ return v>0.05?"#00e6a1":v<-0.05?"#ef4444":"#64748b"; }
function gmpColor(v) { return v>0?"#00e6a1":v<0?"#ef4444":"#64748b"; }

const label = {
  fontSize:"10px", fontWeight:800, letterSpacing:"1.5px",
  textTransform:"uppercase", fontFamily:"'JetBrains Mono',monospace",
  color:"#475569", marginBottom:"8px",
};

function Gauge({ score, signal }) {
  const pct   = Math.min(Math.max(score, 0), 1);
  const angle = pct * 180 - 90;
  const rad   = angle * Math.PI / 180;
  const cx=200, cy=110, r=80;
  const nx = cx + r * Math.sin(rad);
  const ny = cy - r * Math.cos(rad);
  return (
    <svg viewBox="0 0 400 140" style={{ width:"100%", maxWidth:"400px" }}>
      <defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
      <path d={`M ${cx-r} ${cy} A ${r} ${r} 0 0 1 ${cx+r} ${cy}`} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="14" strokeLinecap="round"/>
      <path d={`M ${cx-r} ${cy} A ${r} ${r} 0 0 1 ${cx-r*0.5} ${cy-r*0.866}`} fill="none" stroke="#ef4444" strokeWidth="14" strokeLinecap="round" opacity="0.5"/>
      <path d={`M ${cx-r*0.5} ${cy-r*0.866} A ${r} ${r} 0 0 1 ${cx+r*0.5} ${cy-r*0.866}`} fill="none" stroke="#4a9eff" strokeWidth="14" opacity="0.5"/>
      <path d={`M ${cx+r*0.5} ${cy-r*0.866} A ${r} ${r} 0 0 1 ${cx+r} ${cy}`} fill="none" stroke="#00e6a1" strokeWidth="14" strokeLinecap="round" opacity="0.5"/>
      <line x1={cx} y1={cy} x2={nx} y2={ny} stroke={sigColor(signal)} strokeWidth="3" strokeLinecap="round"/>
      <circle cx={cx} cy={cy} r={6} fill={sigColor(signal)} filter="url(#glow)"/>
      <text x="50"  y="135" fill="#ef4444" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle" fontWeight="700">AVOID</text>
      <text x="200" y="22"  fill="#4a9eff" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle" fontWeight="700">NEUTRAL</text>
      <text x="350" y="135" fill="#00e6a1" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle" fontWeight="700">APPLY</text>
      <text x={cx} y={cy+30} fill="white" fontSize="22" fontFamily="Manrope" textAnchor="middle" fontWeight="800">{score.toFixed(3)}</text>
    </svg>
  );
}

function Bar({ label: lbl, value, color }) {
  return (
    <div style={{ background:"#131920", border:"1px solid #1f2937", borderRadius:"10px", padding:"16px" }}>
      <p style={label}>{lbl}</p>
      <div style={{ display:"flex", alignItems:"center", gap:"10px" }}>
        <div style={{ flex:1, height:"6px", background:"#1f2937", borderRadius:"3px", overflow:"hidden" }}>
          <div style={{ height:"100%", width:`${value*100}%`, background:color, borderRadius:"3px" }}/>
        </div>
        <span style={{ color:"#f1f5f9", fontSize:"13px", fontWeight:700, fontFamily:"'JetBrains Mono',monospace", minWidth:"36px", textAlign:"right" }}>
          {value.toFixed(2)}
        </span>
      </div>
    </div>
  );
}

export default function IPODetail() {
  const { name }   = useParams();
  const navigate   = useNavigate();
  const ipoName    = decodeURIComponent(name);
  const { data: d, loading, error } = useIPODetail(ipoName);

  const card = {
    background:"#131920", border:"1px solid #1f2937", borderRadius:"12px", padding:"20px",
  };

  if (loading) return <div style={{ padding:"80px", textAlign:"center", color:"#475569" }}>Loading...</div>;
  if (error || !d || d.error) return <div style={{ padding:"80px", textAlign:"center", color:"#ef4444" }}>IPO not found.</div>;

  const hasGMP = d.gmp !== null && d.gmp !== undefined;

  const breakdown = [
    { label:"Sentiment",   value: d.score_sentiment   || 0, color:"#00e6a1" },
    { label:"Consistency", value: d.score_consistency  || 0, color:"#a855f7" },
    { label:"Buzz",        value: d.score_buzz          || 0, color:"#eab308" },
    { label:"Trend",       value: d.score_trend         || 0, color:"#4a9eff" },
  ];

  return (
    <div style={{ padding:"40px 60px", maxWidth:"1100px", margin:"0 auto", display:"flex", flexDirection:"column", gap:"24px" }}>

      {/* Back */}
      <button onClick={() => navigate("/")} style={{
        display:"inline-flex", alignItems:"center", gap:"6px",
        background:"none", border:"none", color:"#475569", cursor:"pointer",
        fontSize:"12px", fontFamily:"'JetBrains Mono',monospace", padding:0,
      }}>← Back to Dashboard</button>

      {/* Header */}
      <div style={{ borderBottom:"1px solid #1f2937", paddingBottom:"24px" }}>
        <p style={label}>IPO Analysis</p>
        <h1 style={{ fontSize:"30px", fontWeight:800, fontFamily:"Manrope,sans-serif", color:"#f1f5f9", marginBottom:"14px" }}>
          {d.ipo_name}
        </h1>
        <div style={{ display:"flex", gap:"10px", alignItems:"center" }}>
          <SignalBadge signal={d.signal} size="lg" />
          <span style={{
            padding:"4px 10px", borderRadius:"4px", fontSize:"10px", fontWeight:800,
            letterSpacing:"1px", textTransform:"uppercase", fontFamily:"'JetBrains Mono',monospace",
            background: confColor(d.confidence)+"20", color: confColor(d.confidence),
            border: `1px solid ${confColor(d.confidence)}40`,
          }}>{d.confidence} CONFIDENCE</span>
          {hasGMP && (
            <span style={{
              padding:"4px 12px", borderRadius:"4px", fontSize:"11px", fontWeight:800,
              fontFamily:"'JetBrains Mono',monospace",
              background: gmpColor(d.gmp)+"15", color: gmpColor(d.gmp),
              border: `1px solid ${gmpColor(d.gmp)}30`,
            }}>
              GMP {d.gmp > 0 ? "+" : ""}₹{d.gmp}
              {d.gmp_percent != null && ` (${d.gmp > 0?"+":""}${Number(d.gmp_percent).toFixed(1)}%)`}
            </span>
          )}
        </div>
      </div>

      {/* Stats — 4 cards if GMP, 3 if not */}
      <div style={{ display:"grid", gridTemplateColumns: hasGMP ? "repeat(4,1fr)" : "repeat(3,1fr)", gap:"16px" }}>
        <div style={card}>
          <p style={label}>Final Score</p>
          <p style={{ fontSize:"30px", fontWeight:800, fontFamily:"Manrope,sans-serif", color:sigColor(d.signal) }}>{d.final_score?.toFixed(4)}</p>
        </div>
        <div style={card}>
          <p style={label}>Articles</p>
          <p style={{ fontSize:"30px", fontWeight:800, fontFamily:"Manrope,sans-serif", color:"#eab308" }}>{d.article_count}</p>
        </div>
        <div style={card}>
          <p style={label}>Avg Sentiment</p>
          <p style={{ fontSize:"30px", fontWeight:800, fontFamily:"Manrope,sans-serif", color:sentColor(d.avg_sentiment_score) }}>
            {d.avg_sentiment_score>=0?"+":""}{(d.avg_sentiment_score*100).toFixed(1)}%
          </p>
        </div>
        {hasGMP && (
          <div style={{ ...card, borderColor: gmpColor(d.gmp)+"40", borderTop:`2px solid ${gmpColor(d.gmp)}` }}>
            <p style={label}>Grey Market Premium</p>
            <p style={{ fontSize:"30px", fontWeight:800, fontFamily:"Manrope,sans-serif", color:gmpColor(d.gmp) }}>
              {d.gmp>0?"+":""}₹{d.gmp}
            </p>
            {d.gmp_percent != null && (
              <p style={{ color:gmpColor(d.gmp), fontSize:"12px", fontFamily:"'JetBrains Mono',monospace", marginTop:"4px" }}>
                {d.gmp>0?"+":""}{Number(d.gmp_percent).toFixed(1)}% expected listing gain
              </p>
            )}
          </div>
        )}
      </div>

      {/* Gauge */}
      <div style={card}>
        <p style={label}>Signal Gauge</p>
        <div style={{ display:"flex", justifyContent:"center" }}>
          <Gauge score={d.final_score||0} signal={d.signal} />
        </div>
      </div>

      {/* Breakdown */}
      <div>
        <p style={{ ...label, marginBottom:"12px" }}>Score Breakdown</p>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"12px" }}>
          {breakdown.map(b => <Bar key={b.label} label={b.label} value={b.value} color={b.color} />)}
        </div>
      </div>

      {/* Trend chart */}
      {d.trend && d.trend.length > 1 && (
        <div style={card}>
          <p style={label}>Sentiment Trend</p>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={d.trend}>
              <XAxis dataKey="week" tick={{ fill:"#475569", fontSize:10 }} axisLine={false} tickLine={false}/>
              <YAxis tick={{ fill:"#475569", fontSize:10 }} axisLine={false} tickLine={false}/>
              <Tooltip contentStyle={{ background:"#0d1117", border:"1px solid #1f2937", borderRadius:"8px", fontSize:"12px" }}
                labelStyle={{ color:"#94a3b8" }} itemStyle={{ color:sigColor(d.signal) }}/>
              <ReferenceLine y={0} stroke="#1f2937"/>
              <Line type="monotone" dataKey="avg_sentiment" stroke={sigColor(d.signal)} strokeWidth={2} dot={false}/>
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Coming soon */}
      <div style={{ ...card, background:"#0d1117" }}>
        <p style={{ ...label, marginBottom:"12px" }}>
          Coming Soon
          <span style={{ marginLeft:"8px", padding:"2px 8px", borderRadius:"4px", background:"rgba(234,179,8,0.1)", color:"#eab308", border:"1px solid rgba(234,179,8,0.2)", fontSize:"9px" }}>ROADMAP</span>
        </p>
        <div style={{ display:"flex", flexWrap:"wrap", gap:"12px" }}>
          {["📋 Promoter Holdings","🔄 Subscription Status","💰 OFS Details","📈 Price Band & Lot Size","🏛️ Anchor Investors","📊 Historical Backtesting"].map(item => (
            <span key={item} style={{ color:"#374151", fontSize:"13px" }}>{item}</span>
          ))}
        </div>
      </div>

    </div>
  );
}