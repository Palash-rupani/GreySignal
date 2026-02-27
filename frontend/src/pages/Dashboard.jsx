import StatsRow from "../components/StatsRow";
import IPOTable from "../components/IPOTable";
import { useSignals } from "../hooks/useIPOData";

export default function Dashboard() {
  const { data, loading, error } = useSignals();

  return (
    <div style={{ padding:"40px", margin:"0 auto", display:"flex", flexDirection:"column", gap:"24px" }}>
      <div>
        <h1 style={{ fontSize:"28px", fontWeight:800, fontFamily:"Manrope,sans-serif", color:"#f1f5f9", marginBottom:"6px" }}>
          IPO Intelligence
        </h1>
        <p style={{ color:"#475569", fontSize:"14px" }}>
          Real-time sentiment signals powered by FinBERT · {data.length} IPOs tracked
        </p>
      </div>

      <StatsRow />

      {error ? (
        <div style={{ background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.2)", borderRadius:"12px", padding:"20px", color:"#ef4444" }}>
          ⚠ Could not connect to backend. Make sure FastAPI is running:<br/>
          <code style={{ fontFamily:"'JetBrains Mono',monospace", fontSize:"13px", marginTop:"8px", display:"block" }}>
            cd backend && uvicorn main:app --reload
          </code>
        </div>
      ) : (
        <IPOTable data={data} loading={loading} />
      )}
    </div>
  );
}