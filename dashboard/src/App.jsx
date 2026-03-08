import { useState, useEffect, useRef, useCallback } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, LineChart, Line, Legend } from "recharts";

// ── GFOS Rail Data ─────────────────────────────────────────────
const RAIL_DATA = {
  banking: [
    { name: "SWIFT", volume: 21, fee: 89, speed: 15, congestion: 72, trend: -11, signal: "Congestion detected — AF→EU corridor under pressure" },
    { name: "SEPA", volume: 67, fee: 12, speed: 95, congestion: 18, trend: 4, signal: "Stable — deep EUR liquidity" },
    { name: "ACH", volume: 54, fee: 8, speed: 40, congestion: 22, trend: 2, signal: "End-of-month volume surge" },
    { name: "Fedwire", volume: 38, fee: 31, speed: 92, congestion: 15, trend: 8, signal: "Large corporates active" },
    { name: "CIPS", volume: 44, fee: 28, speed: 71, congestion: 20, trend: 61, signal: "Trade finance expansion — CN→AF +61% YTD" },
    { name: "CHAPS", volume: 29, fee: 35, speed: 88, congestion: 12, trend: 1, signal: "Stable — GBP high-value flows normal" },
  ],
  remittance: [
    { name: "Wise", volume: 34, fee: 31, speed: 88, congestion: 14, trend: 22, signal: "GBP/KES corridor surging" },
    { name: "Western Union", volume: 17, fee: 72, speed: 65, congestion: 18, trend: -14, signal: "Losing share to mobile money" },
    { name: "Remitly", volume: 28, fee: 38, speed: 82, congestion: 11, trend: 18, signal: "Post-payday US→LATAM spike" },
    { name: "WorldRemit", volume: 22, fee: 42, speed: 79, congestion: 9, trend: 31, signal: "UK→Africa harvest season inflows" },
    { name: "Sendwave", volume: 19, fee: 24, speed: 86, congestion: 8, trend: 27, signal: "Mobile-first corridor growth" },
  ],
  mobile_money: [
    { name: "M-Pesa", volume: 62, fee: 8, speed: 98, congestion: 6, trend: 34, signal: "Harvest season — KE/TZ surging" },
    { name: "MTN MoMo", volume: 48, fee: 11, speed: 96, congestion: 9, trend: 18, signal: "West Africa post-harvest inflows" },
    { name: "Wave", volume: 31, fee: 4, speed: 99, congestion: 4, trend: 47, signal: "Fastest-growing rail globally" },
    { name: "Airtel Money", volume: 27, fee: 9, speed: 97, congestion: 7, trend: 11, signal: "East Africa stable" },
    { name: "Orange Money", volume: 19, fee: 10, speed: 95, congestion: 8, trend: 6, signal: "Francophone West Africa steady" },
  ],
  crypto: [
    { name: "USDC/Solana", volume: 58, fee: 3, speed: 99, congestion: 5, trend: 41, signal: "FX arbitrage pressure — surging" },
    { name: "USDT/TRON", volume: 71, fee: 2, speed: 99, congestion: 8, trend: 29, signal: "Remittance substitution signal" },
    { name: "Stellar XLM", volume: 24, fee: 1, speed: 99, congestion: 3, trend: 15, signal: "Institutional corridors active" },
    { name: "Bitcoin", volume: 14, fee: 22, speed: 72, congestion: 31, trend: -2, signal: "Low remittance usage — store of value" },
    { name: "Ethereum", volume: 19, fee: 68, speed: 81, congestion: 61, trend: -8, signal: "High gas — congestion event" },
  ]
};

const CORRIDORS = [
  { from: "KE", to: "DE", fromName: "Kenya", toName: "Germany", dominant: "M-Pesa→USDC→SEPA", volume: 88, trend: 34 },
  { from: "US", to: "MX", fromName: "USA", toName: "Mexico", dominant: "ACH→Remitly", volume: 94, trend: 18 },
  { from: "UK", to: "NG", fromName: "UK", toName: "Nigeria", dominant: "WorldRemit→MTN", volume: 76, trend: 31 },
  { from: "CN", to: "AF", fromName: "China", toName: "Africa", dominant: "CIPS→Mobile", volume: 82, trend: 61 },
  { from: "US", to: "IN", fromName: "USA", toName: "India", dominant: "Wise→UPI", volume: 91, trend: 12 },
  { from: "EU", to: "PH", fromName: "Europe", toName: "Philippines", dominant: "SEPA→GCash", volume: 67, trend: 22 },
  { from: "GH", to: "UK", fromName: "Ghana", toName: "UK", dominant: "MTN→Sendwave", volume: 58, trend: 27 },
  { from: "SN", to: "FR", fromName: "Senegal", toName: "France", dominant: "Wave→SEPA", volume: 49, trend: 47 },
];

const CATEGORY_COLORS = {
  banking: "#f59e0b",
  remittance: "#06b6d4",
  mobile_money: "#10b981",
  crypto: "#8b5cf6",
  fx: "#f43f5e",
};

const TABS = [
  { id: "flow", label: "Rail Flow", icon: "⟳" },
  { id: "architecture", label: "Architecture", icon: "⬡" },
  { id: "comparison", label: "Rail Compare", icon: "≡" },
  { id: "heatmap", label: "Corridor Heatmap", icon: "◉" },
];

// ── Claude API call ─────────────────────────────────────────────
async function analyzeWithClaude(prompt, context) {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: `You are the GFOS Intelligence Engine — the AI analysis layer of the Global Financial Operating System. 
You analyse real-time payment rail data across banking, remittance apps, mobile money, and crypto networks.
You provide sharp, concise financial intelligence — like a Bloomberg analyst who also understands emerging market mobile money and crypto rails.
Keep responses under 200 words. Use specific numbers. Be direct. No fluff. Format with short paragraphs or bullet points.`,
      messages: [{ role: "user", content: `${prompt}\n\nData: ${JSON.stringify(context, null, 2)}` }],
    }),
  });
  const data = await response.json();
  return data.content?.[0]?.text || "Analysis unavailable.";
}

// ── Rail Flow Diagram ───────────────────────────────────────────
function RailFlowDiagram({ onAnalyze }) {
  const canvasRef = useRef(null);
  const [selected, setSelected] = useState(null);
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);

  const nodes = [
    { id: "banking", x: 160, y: 200, label: "BANKING", sub: "SWIFT·SEPA·ACH", color: CATEGORY_COLORS.banking, volume: 75 },
    { id: "remittance", x: 160, y: 380, label: "REMITTANCE", sub: "Wise·WU·Remitly", color: CATEGORY_COLORS.remittance, volume: 55 },
    { id: "mobile", x: 430, y: 120, label: "MOBILE MONEY", sub: "M-Pesa·MTN·Wave", color: CATEGORY_COLORS.mobile_money, volume: 90 },
    { id: "crypto", x: 430, y: 400, label: "CRYPTO", sub: "USDT·USDC·XLM", color: CATEGORY_COLORS.crypto, volume: 68 },
    { id: "fx", x: 700, y: 260, label: "FX MARKETS", sub: "170+ pairs", color: CATEGORY_COLORS.fx, volume: 82 },
  ];

  const flows = [
    { from: 0, to: 2, width: 3, label: "SWIFT→Mobile" },
    { from: 1, to: 2, width: 5, label: "Remit→Mobile" },
    { from: 1, to: 3, width: 4, label: "Remit→Crypto" },
    { from: 2, to: 3, width: 6, label: "Mobile→Crypto" },
    { from: 2, to: 4, width: 4, label: "Mobile→FX" },
    { from: 3, to: 4, width: 7, label: "Crypto→FX" },
    { from: 0, to: 4, width: 3, label: "Bank→FX" },
  ];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    // Background grid
    ctx.strokeStyle = "rgba(245,158,11,0.06)";
    ctx.lineWidth = 1;
    for (let x = 0; x < W; x += 40) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = 0; y < H; y += 40) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    // Animated flow lines
    const t = Date.now() / 1000;
    flows.forEach((flow) => {
      const n1 = nodes[flow.from], n2 = nodes[flow.to];
      const grad = ctx.createLinearGradient(n1.x, n1.y, n2.x, n2.y);
      grad.addColorStop(0, n1.color + "80");
      grad.addColorStop(0.5, n2.color + "cc");
      grad.addColorStop(1, n2.color + "40");
      ctx.beginPath();
      ctx.moveTo(n1.x, n1.y);
      const cx = (n1.x + n2.x) / 2 + Math.sin(t + flow.from) * 20;
      const cy = (n1.y + n2.y) / 2 + Math.cos(t + flow.to) * 20;
      ctx.quadraticCurveTo(cx, cy, n2.x, n2.y);
      ctx.strokeStyle = grad;
      ctx.lineWidth = flow.width;
      ctx.stroke();

      // Animated particle
      const p = (t * 0.3 + flow.from * 0.2) % 1;
      const bx = (1-p)*(1-p)*n1.x + 2*(1-p)*p*cx + p*p*n2.x;
      const by = (1-p)*(1-p)*n1.y + 2*(1-p)*p*cy + p*p*n2.y;
      ctx.beginPath();
      ctx.arc(bx, by, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#fff";
      ctx.fill();
    });

    // Nodes
    nodes.forEach((node) => {
      const isSelected = selected === node.id;
      const glow = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, 55);
      glow.addColorStop(0, node.color + (isSelected ? "50" : "20"));
      glow.addColorStop(1, "transparent");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(node.x, node.y, 55, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.arc(node.x, node.y, 32, 0, Math.PI * 2);
      ctx.fillStyle = "#0a0a0f";
      ctx.fill();
      ctx.strokeStyle = node.color;
      ctx.lineWidth = isSelected ? 3 : 1.5;
      ctx.stroke();

      // Volume ring
      ctx.beginPath();
      ctx.arc(node.x, node.y, 32, -Math.PI / 2, -Math.PI / 2 + (node.volume / 100) * Math.PI * 2);
      ctx.strokeStyle = node.color;
      ctx.lineWidth = 4;
      ctx.stroke();

      ctx.fillStyle = node.color;
      ctx.font = "bold 9px monospace";
      ctx.textAlign = "center";
      ctx.fillText(node.label, node.x, node.y - 4);
      ctx.fillStyle = "rgba(255,255,255,0.5)";
      ctx.font = "8px monospace";
      ctx.fillText(node.sub, node.x, node.y + 8);
    });
  }, [selected]);

  useEffect(() => {
    const interval = setInterval(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      // re-trigger draw
    }, 50);
    return () => clearInterval(interval);
  }, [selected]);

  const handleAnalyze = async () => {
    setLoading(true);
    const text = await analyzeWithClaude(
      "Analyse the current rail flow patterns across all categories. Which rails are gaining share? Where are the critical flow concentrations? What does this signal for the next 30 days?",
      { flows: RAIL_DATA, corridors: CORRIDORS }
    );
    setAnalysis(text);
    setLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, height: "100%" }}>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <div key={cat} style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 10px", border: `1px solid ${color}40`, borderRadius: 4, fontSize: 11, color, fontFamily: "monospace", textTransform: "uppercase" }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: color }} />
            {cat.replace("_", " ")}
          </div>
        ))}
      </div>
      <canvas ref={canvasRef} width={880} height={480} style={{ width: "100%", height: "auto", border: "1px solid rgba(245,158,11,0.15)", borderRadius: 8, background: "#0a0a0f", cursor: "crosshair" }} />
      <AIPanel analysis={analysis} loading={loading} onAnalyze={handleAnalyze} label="Analyse Rail Flows" />
    </div>
  );
}

// ── Architecture Diagram ────────────────────────────────────────
function ArchitectureDiagram() {
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeLayer, setActiveLayer] = useState(null);

  const layers = [
    { id: "sources", label: "DATA SOURCES", color: "#f59e0b", items: ["Banking APIs", "Mobile Money APIs", "Crypto RPCs", "Remittance APIs", "FX Feeds", "Community Reports"], y: 0 },
    { id: "collectors", label: "DATA COLLECTORS", color: "#06b6d4", items: ["Banking Observer", "Mobile Observer", "Crypto Observer", "Remittance Observer", "FX Collector"], y: 1 },
    { id: "streaming", label: "STREAMING LAYER", color: "#8b5cf6", items: ["Apache Kafka", "Redis Streams", "Pattern Triggers", "Cross-Rail Alerts"], y: 2 },
    { id: "database", label: "DATABASE LAYER", color: "#10b981", items: ["PostgreSQL", "Neo4j Rail Graph", "Time-Series Metrics", "Flow History"], y: 3 },
    { id: "intelligence", label: "INTELLIGENCE LAYER", color: "#f43f5e", items: ["Flow Analyser", "Congestion Detector", "Liquidity Modeller", "AI Pattern Engine", "Cross-Rail Comparator"], y: 4 },
    { id: "api", label: "API LAYER", color: "#f59e0b", items: ["FastAPI REST", "WebSocket Stream", "Read-Only Endpoints", "SDK Gateway"], y: 5 },
    { id: "dashboard", label: "UNIFIED DASHBOARD", color: "#06b6d4", items: ["Global Flow Map", "Rail Comparison", "Corridor Heatmap", "AI Analysis Panel"], y: 6 },
  ];

  const handleAnalyze = async () => {
    setLoading(true);
    const text = await analyzeWithClaude(
      "Analyse this system architecture for the GFOS platform. What are the strongest architectural decisions? What are potential bottlenecks or risks? What should be built first to validate the architecture?",
      { layers: layers.map(l => ({ layer: l.label, components: l.items })) }
    );
    setAnalysis(text);
    setLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
        {layers.map((layer, i) => (
          <div key={layer.id} onClick={() => setActiveLayer(activeLayer === layer.id ? null : layer.id)}
            style={{ display: "flex", alignItems: "stretch", cursor: "pointer", transition: "all 0.2s" }}>
            {/* Arrow connector */}
            {i > 0 && (
              <div style={{ position: "absolute", left: "50%", marginTop: -10, fontSize: 14, color: layers[i-1].color, fontFamily: "monospace", zIndex: 1 }} />
            )}
            <div style={{ width: 180, padding: "10px 14px", background: activeLayer === layer.id ? layer.color + "25" : layer.color + "12", border: `1px solid ${layer.color}${activeLayer === layer.id ? "80" : "35"}`, borderRight: "none", borderRadius: "6px 0 0 6px", display: "flex", alignItems: "center" }}>
              <span style={{ fontSize: 10, fontFamily: "monospace", fontWeight: "bold", color: layer.color, letterSpacing: 1 }}>{layer.label}</span>
            </div>
            <div style={{ flex: 1, padding: "10px 14px", background: activeLayer === layer.id ? layer.color + "10" : "rgba(255,255,255,0.02)", border: `1px solid ${layer.color}${activeLayer === layer.id ? "40" : "20"}`, borderLeft: "none", borderRadius: "0 6px 6px 0", display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
              {layer.items.map(item => (
                <span key={item} style={{ fontSize: 10, fontFamily: "monospace", color: "rgba(255,255,255,0.6)", padding: "2px 8px", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 3, background: "rgba(255,255,255,0.04)" }}>{item}</span>
              ))}
            </div>
          </div>
        ))}

        {/* Flow arrows between layers */}
        <div style={{ display: "flex", justifyContent: "center", padding: "4px 0" }}>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
            {layers.slice(0, -1).map((_, i) => (
              <div key={i} style={{ width: 1, height: 8, background: `linear-gradient(${layers[i].color}, ${layers[i+1].color})`, opacity: 0.4 }} />
            ))}
          </div>
        </div>
      </div>
      <AIPanel analysis={analysis} loading={loading} onAnalyze={handleAnalyze} label="Analyse Architecture" />
    </div>
  );
}

// ── Rail Comparison Chart ───────────────────────────────────────
function RailComparison() {
  const [category, setCategory] = useState("all");
  const [metric, setMetric] = useState("volume");
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);

  const allRails = [
    ...RAIL_DATA.banking.map(r => ({ ...r, category: "banking" })),
    ...RAIL_DATA.remittance.map(r => ({ ...r, category: "remittance" })),
    ...RAIL_DATA.mobile_money.map(r => ({ ...r, category: "mobile_money" })),
    ...RAIL_DATA.crypto.map(r => ({ ...r, category: "crypto" })),
  ];

  const filtered = category === "all" ? allRails : allRails.filter(r => r.category === category);
  const sorted = [...filtered].sort((a, b) => b[metric] - a[metric]);

  const radarData = ["SWIFT", "Wise", "M-Pesa", "USDT/TRON"].map(name => {
    const rail = allRails.find(r => r.name === name) || {};
    return { name, Volume: rail.volume || 0, Speed: rail.speed || 0, "Low Fee": 100 - (rail.fee || 0), Reliability: 100 - (rail.congestion || 0) };
  });

  const trendData = filtered.map(r => ({ name: r.name, trend: r.trend, fill: r.trend > 0 ? CATEGORY_COLORS[r.category] : "#ef4444" }));

  const handleAnalyze = async () => {
    setLoading(true);
    const text = await analyzeWithClaude(
      `Compare these payment rails across categories. Which rails are winning on ${metric}? What does the trend data reveal about where volume is shifting? Which legacy rails are under threat?`,
      { rails: sorted.slice(0, 10), metric }
    );
    setAnalysis(text);
    setLoading(false);
  };

  const METRICS = ["volume", "fee", "speed", "congestion", "trend"];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Controls */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {["all", "banking", "remittance", "mobile_money", "crypto"].map(cat => (
          <button key={cat} onClick={() => setCategory(cat)} style={{ padding: "5px 12px", fontSize: 10, fontFamily: "monospace", textTransform: "uppercase", letterSpacing: 1, border: `1px solid ${category === cat ? (CATEGORY_COLORS[cat] || "#f59e0b") : "rgba(255,255,255,0.15)"}`, borderRadius: 4, background: category === cat ? (CATEGORY_COLORS[cat] || "#f59e0b") + "20" : "transparent", color: category === cat ? (CATEGORY_COLORS[cat] || "#f59e0b") : "rgba(255,255,255,0.5)", cursor: "pointer" }}>
            {cat.replace("_", " ")}
          </button>
        ))}
        <div style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
          {METRICS.map(m => (
            <button key={m} onClick={() => setMetric(m)} style={{ padding: "5px 10px", fontSize: 10, fontFamily: "monospace", textTransform: "uppercase", border: `1px solid ${metric === m ? "#f59e0b" : "rgba(255,255,255,0.1)"}`, borderRadius: 4, background: metric === m ? "#f59e0b20" : "transparent", color: metric === m ? "#f59e0b" : "rgba(255,255,255,0.4)", cursor: "pointer" }}>
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Bar chart */}
      <div style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(245,158,11,0.12)", borderRadius: 8, padding: 16 }}>
        <div style={{ fontSize: 10, fontFamily: "monospace", color: "rgba(255,255,255,0.4)", marginBottom: 12, textTransform: "uppercase", letterSpacing: 2 }}>{metric} Index — all rail categories</div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={sorted} margin={{ top: 0, right: 0, bottom: 40, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="name" tick={{ fontSize: 9, fontFamily: "monospace", fill: "rgba(255,255,255,0.5)" }} angle={-35} textAnchor="end" />
            <YAxis tick={{ fontSize: 9, fontFamily: "monospace", fill: "rgba(255,255,255,0.4)" }} />
            <Tooltip contentStyle={{ background: "#0a0a0f", border: "1px solid rgba(245,158,11,0.3)", borderRadius: 6, fontSize: 11, fontFamily: "monospace" }} />
            <Bar dataKey={metric} radius={[3, 3, 0, 0]}
              fill="#f59e0b"
              label={false}
              cell={sorted.map((entry, i) => (
                <rect key={i} fill={CATEGORY_COLORS[entry.category] || "#f59e0b"} />
              ))}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Radar + Trend row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(245,158,11,0.12)", borderRadius: 8, padding: 16 }}>
          <div style={{ fontSize: 10, fontFamily: "monospace", color: "rgba(255,255,255,0.4)", marginBottom: 8, textTransform: "uppercase", letterSpacing: 2 }}>Cross-Rail Radar</div>
          <ResponsiveContainer width="100%" height={180}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.08)" />
              <PolarAngleAxis dataKey="name" tick={{ fontSize: 9, fontFamily: "monospace", fill: "rgba(255,255,255,0.5)" }} />
              <Radar name="SWIFT" dataKey="Volume" stroke={CATEGORY_COLORS.banking} fill={CATEGORY_COLORS.banking} fillOpacity={0.15} />
              <Radar name="M-Pesa" dataKey="Speed" stroke={CATEGORY_COLORS.mobile_money} fill={CATEGORY_COLORS.mobile_money} fillOpacity={0.15} />
              <Radar name="USDT" dataKey="Low Fee" stroke={CATEGORY_COLORS.crypto} fill={CATEGORY_COLORS.crypto} fillOpacity={0.15} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ background: "rgba(255,255,255,0.02)", border: "1px solid rgba(245,158,11,0.12)", borderRadius: 8, padding: 16 }}>
          <div style={{ fontSize: 10, fontFamily: "monospace", color: "rgba(255,255,255,0.4)", marginBottom: 8, textTransform: "uppercase", letterSpacing: 2 }}>WoW Trend %</div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={trendData.slice(0, 8)} margin={{ top: 0, right: 0, bottom: 30, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 8, fontFamily: "monospace", fill: "rgba(255,255,255,0.5)" }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 8, fontFamily: "monospace", fill: "rgba(255,255,255,0.4)" }} />
              <Tooltip contentStyle={{ background: "#0a0a0f", border: "1px solid rgba(245,158,11,0.3)", borderRadius: 6, fontSize: 11, fontFamily: "monospace" }} />
              <Bar dataKey="trend" radius={[3, 3, 0, 0]}>
                {trendData.slice(0, 8).map((entry, i) => (
                  <rect key={i} fill={entry.trend > 0 ? "#10b981" : "#ef4444"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <AIPanel analysis={analysis} loading={loading} onAnalyze={handleAnalyze} label="Analyse Rail Comparison" />
    </div>
  );
}

// ── Corridor Heatmap ────────────────────────────────────────────
function CorridorHeatmap() {
  const [selected, setSelected] = useState(null);
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("all");

  const getColor = (volume, trend) => {
    if (trend > 40) return "#10b981";
    if (trend > 20) return "#06b6d4";
    if (trend > 5)  return "#f59e0b";
    if (trend > 0)  return "#f59e0b90";
    return "#ef4444";
  };

  const handleAnalyze = async () => {
    setLoading(true);
    const text = await analyzeWithClaude(
      "Analyse these global payment corridors. Which corridors are experiencing the most significant flow shifts? Which are declining? What macro factors are driving the top-growth corridors? What does this mean for capital allocation in emerging markets?",
      { corridors: CORRIDORS, selected }
    );
    setAnalysis(text);
    setLoading(false);
  };

  const allRails = [...RAIL_DATA.banking, ...RAIL_DATA.remittance, ...RAIL_DATA.mobile_money, ...RAIL_DATA.crypto];
  const topSurging = [...allRails].sort((a, b) => b.trend - a.trend).slice(0, 6);
  const topCongested = [...allRails].sort((a, b) => b.congestion - a.congestion).slice(0, 4);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Corridor grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8 }}>
        {CORRIDORS.map((corridor) => (
          <div key={`${corridor.from}-${corridor.to}`} onClick={() => setSelected(selected?.from === corridor.from ? null : corridor)}
            style={{ padding: 14, border: `1px solid ${selected?.from === corridor.from ? getColor(corridor.volume, corridor.trend) : getColor(corridor.volume, corridor.trend) + "50"}`, borderRadius: 8, background: selected?.from === corridor.from ? getColor(corridor.volume, corridor.trend) + "15" : "rgba(255,255,255,0.02)", cursor: "pointer", transition: "all 0.2s" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
              <span style={{ fontSize: 10, fontFamily: "monospace", fontWeight: "bold", color: "rgba(255,255,255,0.9)" }}>{corridor.fromName}</span>
              <span style={{ fontSize: 16, color: "rgba(255,255,255,0.2)" }}>→</span>
              <span style={{ fontSize: 10, fontFamily: "monospace", fontWeight: "bold", color: "rgba(255,255,255,0.9)" }}>{corridor.toName}</span>
            </div>
            <div style={{ fontSize: 9, fontFamily: "monospace", color: getColor(corridor.volume, corridor.trend), marginBottom: 6 }}>{corridor.dominant}</div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ height: 3, flex: 1, borderRadius: 2, background: "rgba(255,255,255,0.1)", marginRight: 8 }}>
                <div style={{ height: "100%", width: `${corridor.volume}%`, borderRadius: 2, background: getColor(corridor.volume, corridor.trend), transition: "width 0.5s" }} />
              </div>
              <span style={{ fontSize: 10, fontFamily: "monospace", fontWeight: "bold", color: corridor.trend > 0 ? "#10b981" : "#ef4444" }}>
                {corridor.trend > 0 ? "+" : ""}{corridor.trend}%
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Signal strips */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div style={{ background: "rgba(16,185,129,0.05)", border: "1px solid rgba(16,185,129,0.2)", borderRadius: 8, padding: 14 }}>
          <div style={{ fontSize: 10, fontFamily: "monospace", color: "#10b981", marginBottom: 10, letterSpacing: 2 }}>⬆ SURGING RAILS</div>
          {topSurging.map(rail => (
            <div key={rail.name} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "5px 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <span style={{ fontSize: 10, fontFamily: "monospace", color: "rgba(255,255,255,0.7)" }}>{rail.name}</span>
              <span style={{ fontSize: 10, fontFamily: "monospace", color: "#10b981", fontWeight: "bold" }}>+{rail.trend}%</span>
            </div>
          ))}
        </div>
        <div style={{ background: "rgba(239,68,68,0.05)", border: "1px solid rgba(239,68,68,0.2)", borderRadius: 8, padding: 14 }}>
          <div style={{ fontSize: 10, fontFamily: "monospace", color: "#ef4444", marginBottom: 10, letterSpacing: 2 }}>⚠ CONGESTION ALERTS</div>
          {topCongested.map(rail => (
            <div key={rail.name} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "5px 0", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
              <span style={{ fontSize: 10, fontFamily: "monospace", color: "rgba(255,255,255,0.7)" }}>{rail.name}</span>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ width: 50, height: 4, borderRadius: 2, background: "rgba(255,255,255,0.1)" }}>
                  <div style={{ width: `${rail.congestion}%`, height: "100%", borderRadius: 2, background: "#ef4444" }} />
                </div>
                <span style={{ fontSize: 10, fontFamily: "monospace", color: "#ef4444" }}>{rail.congestion}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <AIPanel analysis={analysis} loading={loading} onAnalyze={handleAnalyze} label="Analyse Corridors" />
    </div>
  );
}

// ── AI Analysis Panel ───────────────────────────────────────────
function AIPanel({ analysis, loading, onAnalyze, label }) {
  return (
    <div style={{ border: "1px solid rgba(245,158,11,0.25)", borderRadius: 8, overflow: "hidden" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 14px", background: "rgba(245,158,11,0.06)", borderBottom: "1px solid rgba(245,158,11,0.15)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: loading ? "#f59e0b" : analysis ? "#10b981" : "rgba(255,255,255,0.3)", boxShadow: loading ? "0 0 8px #f59e0b" : "none", animation: loading ? "pulse 1s infinite" : "none" }} />
          <span style={{ fontSize: 10, fontFamily: "monospace", color: "#f59e0b", letterSpacing: 2 }}>CLAUDE INTELLIGENCE ENGINE</span>
        </div>
        <button onClick={onAnalyze} disabled={loading} style={{ padding: "5px 14px", fontSize: 10, fontFamily: "monospace", fontWeight: "bold", letterSpacing: 1, border: "1px solid #f59e0b", borderRadius: 4, background: loading ? "rgba(245,158,11,0.1)" : "rgba(245,158,11,0.15)", color: "#f59e0b", cursor: loading ? "not-allowed" : "pointer" }}>
          {loading ? "ANALYSING..." : `▶  ${label}`}
        </button>
      </div>
      <div style={{ padding: 14, minHeight: 80, fontSize: 12, fontFamily: "monospace", lineHeight: 1.7, color: analysis ? "rgba(255,255,255,0.8)" : "rgba(255,255,255,0.25)" }}>
        {loading ? (
          <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
            {[0,1,2].map(i => <div key={i} style={{ width: 6, height: 6, borderRadius: "50%", background: "#f59e0b", animation: `bounce 1s ${i*0.15}s infinite` }} />)}
            <span style={{ marginLeft: 8, color: "rgba(255,255,255,0.4)" }}>Processing rail data...</span>
          </div>
        ) : analysis || "Press the button above to run Claude AI analysis on this data."}
      </div>
    </div>
  );
}

// ── Main App ────────────────────────────────────────────────────
export default function GFOSDashboard() {
  const [activeTab, setActiveTab] = useState("flow");
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setTick(t => t + 1), 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#07070d", color: "#fff", fontFamily: "monospace" }}>
      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
        @keyframes scan { 0%{transform:translateY(-100%)} 100%{transform:translateY(100vh)} }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px } 
        ::-webkit-scrollbar-track { background: #0a0a0f }
        ::-webkit-scrollbar-thumb { background: rgba(245,158,11,0.3); border-radius: 2px }
      `}</style>

      {/* Scan line */}
      <div style={{ position: "fixed", top: 0, left: 0, right: 0, height: 1, background: "rgba(245,158,11,0.06)", zIndex: 0, animation: "scan 8s linear infinite", pointerEvents: "none" }} />

      {/* Header */}
      <div style={{ padding: "12px 24px", borderBottom: "1px solid rgba(245,158,11,0.15)", display: "flex", alignItems: "center", justifyContent: "space-between", background: "rgba(0,0,0,0.4)", backdropFilter: "blur(10px)", position: "sticky", top: 0, zIndex: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: "bold", letterSpacing: 3, color: "#f59e0b" }}>GFOS</div>
            <div style={{ fontSize: 8, color: "rgba(255,255,255,0.4)", letterSpacing: 2 }}>GLOBAL FINANCIAL OPERATING SYSTEM</div>
          </div>
          <div style={{ width: 1, height: 32, background: "rgba(245,158,11,0.2)" }} />
          <div style={{ display: "flex", gap: 12 }}>
            {[
              { label: "RAILS LIVE", value: "47", color: "#10b981" },
              { label: "SURGING", value: "12", color: "#f59e0b" },
              { label: "ALERTS", value: "3", color: "#ef4444" },
            ].map(stat => (
              <div key={stat.label} style={{ textAlign: "center" }}>
                <div style={{ fontSize: 16, fontWeight: "bold", color: stat.color }}>{stat.value}</div>
                <div style={{ fontSize: 8, color: "rgba(255,255,255,0.35)", letterSpacing: 1 }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981", boxShadow: "0 0 8px #10b981", animation: "pulse 2s infinite" }} />
          <span style={{ fontSize: 10, color: "rgba(255,255,255,0.5)" }}>LIVE  |  {new Date().toUTCString().slice(17, 25)} UTC</span>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 0, borderBottom: "1px solid rgba(245,158,11,0.1)", padding: "0 24px", background: "rgba(0,0,0,0.2)" }}>
        {TABS.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{ padding: "12px 20px", fontSize: 10, fontFamily: "monospace", letterSpacing: 2, fontWeight: "bold", border: "none", borderBottom: `2px solid ${activeTab === tab.id ? "#f59e0b" : "transparent"}`, background: "transparent", color: activeTab === tab.id ? "#f59e0b" : "rgba(255,255,255,0.35)", cursor: "pointer", transition: "all 0.2s", display: "flex", alignItems: "center", gap: 6 }}>
            <span>{tab.icon}</span> {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
        {activeTab === "flow" && <RailFlowDiagram />}
        {activeTab === "architecture" && <ArchitectureDiagram />}
        {activeTab === "comparison" && <RailComparison />}
        {activeTab === "heatmap" && <CorridorHeatmap />}
      </div>
    </div>
  );
}
