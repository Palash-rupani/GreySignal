import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import Dashboard  from "./pages/Dashboard";
import IPODetail  from "./pages/IPODetail";

function Header() {
  const navigate = useNavigate();

  return (
    <header style={{
      position:       "sticky", top:0, zIndex:100,
      borderBottom:   "1px solid #1f2937",
      background:     "rgba(8,12,16,0.90)",
      backdropFilter: "blur(16px)",
    }}>
      <div style={{
        display:        "flex",
        alignItems:     "center",
        justifyContent: "space-between",
        padding:        "0 40px",
        height:         "64px",
        width:          "100%",
      }}>
        {/* Logo */}
        <div style={{ display:"flex", alignItems:"center", gap:"32px" }}>
          <div onClick={() => navigate("/")} style={{ display:"flex", alignItems:"center", gap:"10px", cursor:"pointer" }}>
            <div style={{ position:"relative", width:"24px", height:"24px" }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L4 7v10l8 5 8-5V7L12 2z" stroke="#00e6a1" strokeWidth="1.5" fill="none"/>
                <path d="M12 7L8 9.5v5L12 17l4-2.5v-5L12 7z" fill="#00e6a1" fillOpacity="0.3"/>
              </svg>
              <span style={{
                position:"absolute", top:"-2px", right:"-2px",
                width:"7px", height:"7px", borderRadius:"50%",
                background:"#00e6a1",
                boxShadow:"0 0 8px #00e6a1",
                animation:"pulse 2s infinite",
              }}/>
            </div>
            <span style={{ fontSize:"20px", fontWeight:800, fontFamily:"Manrope,sans-serif", color:"#f1f5f9", letterSpacing:"-0.5px" }}>
              GreySignal
            </span>
          </div>

          <nav style={{ display:"flex", gap:"24px" }}>
            <a onClick={() => navigate("/")} style={{ color:"#00e6a1", fontSize:"13px", fontWeight:600, cursor:"pointer", textDecoration:"none" }}>Dashboard</a>
            <a style={{ color:"#475569", fontSize:"13px", fontWeight:500, cursor:"pointer", textDecoration:"none" }}>Market</a>
            <a style={{ color:"#475569", fontSize:"13px", fontWeight:500, cursor:"pointer", textDecoration:"none" }}>Sentiment</a>
            <a style={{ color:"#475569", fontSize:"13px", fontWeight:500, cursor:"pointer", textDecoration:"none" }}>Reports</a>
          </nav>
        </div>

        {/* Right */}
        <div style={{ display:"flex", alignItems:"center", gap:"16px" }}>
          <span style={{
            color:"#374151", fontSize:"11px",
            fontFamily:"'JetBrains Mono',monospace",
          }}>
            {new Date().toLocaleDateString("en-IN",{day:"numeric",month:"short",year:"numeric"})}
          </span>
          <div style={{
            display:"flex", alignItems:"center", gap:"6px",
            padding:"4px 12px", borderRadius:"999px",
            background:"rgba(0,230,161,0.08)",
            border:"1px solid rgba(0,230,161,0.2)",
          }}>
            <span style={{ width:"6px", height:"6px", borderRadius:"50%", background:"#00e6a1", animation:"pulse 1.5s infinite" }}/>
            <span style={{ color:"#00e6a1", fontSize:"10px", fontWeight:800, letterSpacing:"1.5px", fontFamily:"'JetBrains Mono',monospace" }}>LIVE</span>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%,100% { opacity:1; box-shadow:0 0 8px #00e6a1; }
          50%      { opacity:0.5; box-shadow:0 0 3px #00e6a1; }
        }
      `}</style>
    </header>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div style={{
        minHeight:       "100vh",
        background:      "#080c10",
        backgroundImage: "linear-gradient(rgba(31,41,55,0.12) 1px,transparent 1px),linear-gradient(90deg,rgba(31,41,55,0.12) 1px,transparent 1px)",
        backgroundSize:  "40px 40px",
        color:           "#f1f5f9",
        fontFamily:      "Manrope, sans-serif",
      }}>
        <Header />
        <Routes>
          <Route path="/"          element={<Dashboard />} />
          <Route path="/ipo/:name" element={<IPODetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}