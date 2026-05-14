import React, { useState } from "react"; // import는 소문자로
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Area, AreaChart, BarChart, Bar, Cell
} from "recharts";

// --- Mock 데이터 ---
const MOCK_DATA = [
  { date: "05-06", individual: 18200, foreign: -12300, institution: -5900 },
  { date: "05-07", individual: 22100, foreign: -19800, institution: -2300 },
  { date: "05-08", individual: 11500, foreign: -23100, institution: 11600 },
  { date: "05-09", individual: 28700, foreign: -8400,  institution: -20300 },
  { date: "05-12", individual: 9800,  foreign: -31200, institution: 21400 },
  { date: "05-13", individual: 16400, foreign: -17600, institution: 1200  },
  { date: "05-14", individual: 13200, foreign: -22800, institution: 9600  },
];

function calcFatigue(individual, foreign) {
  let score = 100;
  // 개인 매수세가 15000억 미만일 때 감점
  const indivPenalty = individual < 15000 ? Math.min(40, (15000 - individual) / 300) : 0;
  // 외국인 매도세가 15000억 이상일 때 감점
  const foreignPenalty = foreign < -15000 ? Math.min(40, (-15000 - foreign) / 400) : 0;
  const bothWeakBonus = individual > 25000 ? 5 : 0;
  score = score - indivPenalty - foreignPenalty + bothWeakBonus;
  return Math.round(Math.max(0, Math.min(100, score)));
}

const enriched = MOCK_DATA.map(d => ({
  ...d,
  fatigue: calcFatigue(d.individual, d.foreign),
}));

function statusFromScore(score) {
  if (score < 60) return { label: "위험", color: "#ef4444", bg: "#2a0d0d", border: "#fca5a5" };
  if (score < 78) return { label: "주의", color: "#f59e0b", bg: "#2a1f0d", border: "#fcd34d" };
  return { label: "안전", color: "#10b981", bg: "#0d2a1a", border: "#6ee7b7" };
}

const fmt = (n) => (n >= 0 ? "+" : "") + (n / 100).toFixed(0) + "억";

// 툴팁 컴포넌트
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  const st = statusFromScore(d.fatigue);
  return (
    <div style={{
      background: "#0f172a", border: "1px solid #1e293b",
      borderRadius: 8, padding: "10px 14px", fontSize: 12, color: "#e2e8f0"
    }}>
      <div style={{ fontWeight: 700, marginBottom: 6, color: "#94a3b8" }}>{label}</div>
      <div>피로지수: <span style={{ color: st.color, fontWeight: 700 }}>{d.fatigue}점</span></div>
      <div style={{ marginTop: 4, color: "#64748b" }}>
        개인 {fmt(d.individual)} / 외국인 {fmt(d.foreign)}
      </div>
    </div>
  );
};

export default function FatigueDashboard() {
  const [activeTab, setActiveTab] = useState("fatigue");
  
  if (enriched.length === 0) return <div>No Data</div>;

  const latest = enriched[enriched.length - 1];
  const prev = enriched[enriched.length - 2] || latest;
  const status = statusFromScore(latest.fatigue);
  const delta = latest.fatigue - prev.fatigue;

  return (
    <div style={{
      minHeight: "100vh", background: "#080f1a",
      fontFamily: "sans-serif", color: "#e2e8f0", padding: "28px 24px"
    }}>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
          <div style={{
            width: 8, height: 8, borderRadius: "50%", background: status.color,
            boxShadow: `0 0 8px ${status.color}`
          }} />
          <span style={{ fontSize: 11, color: "#64748b", letterSpacing: "0.12em", textTransform: "uppercase" }}>
            KOSPI 투자자 동향 분석
          </span>
        </div>
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, color: "#f1f5f9" }}>
          개인 방어 피로지수
        </h1>
      </div>

      {/* KPI Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 24 }}>
        <div style={{ background: "#0d1929", border: `1px solid ${status.border}`, borderRadius: 10, padding: "16px 18px" }}>
          <div style={{ fontSize: 10, color: "#64748b", marginBottom: 8 }}>피로지수 ({latest.date})</div>
          <div style={{ fontSize: 36, fontWeight: 700, color: status.color }}>{latest.fatigue}</div>
          <div style={{ fontSize: 11, marginTop: 6, color: "#94a3b8" }}>
            전일比 <span style={{ color: delta >= 0 ? "#10b981" : "#ef4444" }}>{delta >= 0 ? "+" : ""}{delta}점</span>
          </div>
        </div>

        <div style={{ background: "#0d1929", border: "1px solid #1e293b", borderRadius: 10, padding: "16px 18px" }}>
          <div style={{ fontSize: 10, color: "#64748b", marginBottom: 8 }}>개인 순매수</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: latest.individual >= 0 ? "#38bdf8" : "#f87171" }}>{fmt(latest.individual)}</div>
        </div>

        <div style={{ background: "#0d1929", border: "1px solid #1e293b", borderRadius: 10, padding: "16px 18px" }}>
          <div style={{ fontSize: 10, color: "#64748b", marginBottom: 8 }}>외국인 순매수</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: latest.foreign >= 0 ? "#a78bfa" : "#fb923c" }}>{fmt(latest.foreign)}</div>
        </div>
      </div>

      {/* Status Banner */}
      <div style={{
        background: status.bg, border: `1px solid ${status.border}`,
        borderRadius: 8, padding: "12px 16px", marginBottom: 24,
        display: "flex", alignItems: "center", gap: 10
      }}>
        <div style={{ width: 6, height: 6, borderRadius: "50%", background: status.color }} />
        <span style={{ fontSize: 12, color: status.color, fontWeight: 600 }}>
          {status.label === "위험" && `피로 누적 강함 (${latest.fatigue}점) — 곱버스 포지션 재검토 신호`}
          {status.label === "주의" && `주의 단계 (${latest.fatigue}점) — 신용잔고 및 외국인 동향 모니터링`}
          {status.label === "안전" && `안전 구간 (${latest.fatigue}점) — 현재 방어 수요 유지 중`}
        </span>
      </div>

      {/* Tab Nav */}
      <div style={{ display: "flex", gap: 4, marginBottom: 16 }}>
        {["fatigue", "flow"].map(id => (
          <button key={id} onClick={() => setActiveTab(id)} style={{
            padding: "6px 14px", fontSize: 11, borderRadius: 6, cursor: "pointer",
            background: activeTab === id ? "#1e3a5f" : "transparent",
            color: activeTab === id ? "#38bdf8" : "#64748b",
            border: activeTab === id ? "1px solid #38bdf8" : "1px solid #1e293b",
          }}>
            {id === "fatigue" ? "피로지수 추이" : "투자자 수급"}
          </button>
        ))}
      </div>

      {/* Chart Box */}
      <div style={{ background: "#0d1929", border: "1px solid #1e293b", borderRadius: 10, padding: "20px 16px" }}>
        <ResponsiveContainer width="100%" height={250}>
          {activeTab === "fatigue" ? (
            <AreaChart data={enriched}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="fatigue" stroke="#38bdf8" fillOpacity={0.1} fill="#38bdf8" />
            </AreaChart>
          ) : (
            <BarChart data={enriched}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 10 }} />
              <YAxis tickFormatter={v => (v/100).toFixed(0)} tick={{ fill: "#64748b", fontSize: 10 }} />
              <Tooltip formatter={(v) => fmt(v)} />
              <Bar dataKey="individual" fill="#38bdf8" />
              <Bar dataKey="foreign" fill="#fb923c" />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
