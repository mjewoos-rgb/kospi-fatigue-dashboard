import { useState, useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Area, AreaChart, BarChart, Bar, Cell
} from "recharts";

// --- Mock data simulating pykrx output ---
// Replace with real API call if running locally with pykrx
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
  // Base score 100
  // Individual net buy < 15000억 → defensive demand weakening
  // Foreign net sell > 15000억 → selling pressure
  // Combined signal
  let score = 100;
  const indivPenalty = individual < 15000 ? Math.min(40, (15000 - individual) / 300) : 0;
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
  if (score < 60) return { label: "위험", color: "#ef4444", bg: "#fef2f2", border: "#fca5a5" };
  if (score < 78) return { label: "주의", color: "#f59e0b", bg: "#fffbeb", border: "#fcd34d" };
  return { label: "안전", color: "#10b981", bg: "#f0fdf4", border: "#6ee7b7" };
}

const fmt = (n) => (n >= 0 ? "+" : "") + (n / 100).toFixed(0) + "억";

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
  const latest = enriched[enriched.length - 1];
  const prev = enriched[enriched.length - 2];
  const status = statusFromScore(latest.fatigue);
  const delta = latest.fatigue - prev.fatigue;

  const barColors = enriched.map(d => {
    const s = statusFromScore(d.fatigue);
    return s.color;
  });

  return (
    <div style={{
      minHeight: "100vh", background: "#080f1a",
      fontFamily: "'IBM Plex Mono', 'Courier New', monospace",
      color: "#e2e8f0", padding: "28px 24px"
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
        <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, color: "#f1f5f9", letterSpacing: "-0.02em" }}>
          개인 방어 피로지수
        </h1>
        <div style={{ fontSize: 11, color: "#475569", marginTop: 4 }}>
          최근 거래일 기준 · pykrx 연동 · 데이터 단위: 억원
        </div>
      </div>

      {/* KPI Row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 24 }}>
        {/* Fatigue Score */}
        <div style={{
          background: "#0d1929", border: `1px solid ${status.border}`,
          borderRadius: 10, padding: "16px 18px"
        }}>
          <div style={{ fontSize: 10, color: "#64748b", letterSpacing: "0.1em", marginBottom: 8 }}>
            피로지수 ({latest.date})
          </div>
          <div style={{ fontSize: 36, fontWeight: 700, color: status.color, lineHeight: 1 }}>
            {latest.fatigue}
          </div>
          <div style={{ fontSize: 11, marginTop: 6, color: "#94a3b8" }}>
            전일比 <span style={{ color: delta >= 0 ? "#10b981" : "#ef4444" }}>
              {delta >= 0 ? "+" : ""}{delta}점
            </span>
          </div>
          {/* Progress bar */}
          <div style={{ marginTop: 10, background: "#1e293b", borderRadius: 4, height: 4 }}>
            <div style={{
              width: `${latest.fatigue}%`, height: "100%",
              background: status.color, borderRadius: 4,
              transition: "width 0.8s ease"
            }} />
          </div>
        </div>

        {/* Individual */}
        <div style={{
          background: "#0d1929", border: "1px solid #1e293b",
          borderRadius: 10, padding: "16px 18px"
        }}>
          <div style={{ fontSize: 10, color: "#64748b", letterSpacing: "0.1em", marginBottom: 8 }}>
            개인 순매수
          </div>
          <div style={{ fontSize: 28, fontWeight: 700, color: latest.individual >= 0 ? "#38bdf8" : "#f87171", lineHeight: 1 }}>
            {fmt(latest.individual)}
          </div>
          <div style={{ fontSize: 11, marginTop: 6, color: "#475569" }}>
            {latest.individual >= 15000 ? "방어 수요 충분" : "방어 수요 미약"}
          </div>
        </div>

        {/* Foreign */}
        <div style={{
          background: "#0d1929", border: "1px solid #1e293b",
          borderRadius: 10, padding: "16px 18px"
        }}>
          <div style={{ fontSize: 10, color: "#64748b", letterSpacing: "0.1em", marginBottom: 8 }}>
            외국인 순매수
          </div>
          <div style={{ fontSize: 28, fontWeight: 700, color: latest.foreign >= 0 ? "#a78bfa" : "#fb923c", lineHeight: 1 }}>
            {fmt(latest.foreign)}
          </div>
          <div style={{ fontSize: 11, marginTop: 6, color: "#475569" }}>
            {latest.foreign < -15000 ? "매도 압력 강함" : "매도 압력 보통"}
          </div>
        </div>
      </div>

      {/* Status Banner */}
      <div style={{
        background: status.bg.replace("f0fdf4", "0d2a1a").replace("fef2f2", "2a0d0d").replace("fffbeb", "2a1f0d"),
        border: `1px solid ${status.border}`,
        borderRadius: 8, padding: "12px 16px", marginBottom: 24,
        display: "flex", alignItems: "center", gap: 10
      }}>
        <div style={{ width: 6, height: 6, borderRadius: "50%", background: status.color, flexShrink: 0 }} />
        <span style={{ fontSize: 12, color: status.color, fontWeight: 600 }}>
          {status.label === "위험" && `피로 누적 강함 (${latest.fatigue}점) — 곱버스 포지션 재검토 신호`}
          {status.label === "주의" && `주의 단계 (${latest.fatigue}점) — 신용잔고 및 외국인 동향 모니터링`}
          {status.label === "안전" && `안전 구간 (${latest.fatigue}점) — 현재 방어 수요 유지 중`}
        </span>
      </div>

      {/* Tab Nav */}
      <div style={{ display: "flex", gap: 4, marginBottom: 16 }}>
        {[
          { id: "fatigue", label: "피로지수 추이" },
          { id: "flow",    label: "투자자 수급" },
        ].map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
            padding: "6px 14px", fontSize: 11, letterSpacing: "0.05em",
            borderRadius: 6, cursor: "pointer", transition: "all 0.15s",
            background: activeTab === tab.id ? "#1e3a5f" : "transparent",
            color: activeTab === tab.id ? "#38bdf8" : "#64748b",
            border: activeTab === tab.id ? "1px solid #38bdf8" : "1px solid #1e293b",
          }}>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Charts */}
      <div style={{
        background: "#0d1929", border: "1px solid #1e293b",
        borderRadius: 10, padding: "20px 16px", marginBottom: 24
      }}>
        {activeTab === "fatigue" && (
          <>
            <div style={{ fontSize: 11, color: "#64748b", marginBottom: 16 }}>
              피로지수 일별 추이 (0~100점)
            </div>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={enriched} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="fatigueGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine y={78} stroke="#f59e0b" strokeDasharray="4 3" strokeOpacity={0.5}
                  label={{ value: "주의", fill: "#f59e0b", fontSize: 9, position: "right" }} />
                <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="4 3" strokeOpacity={0.5}
                  label={{ value: "위험", fill: "#ef4444", fontSize: 9, position: "right" }} />
                <Area type="monotone" dataKey="fatigue" stroke="#38bdf8" strokeWidth={2}
                  fill="url(#fatigueGrad)" dot={{ r: 3, fill: "#38bdf8" }}
                  activeDot={{ r: 5, fill: "#38bdf8" }} />
              </AreaChart>
            </ResponsiveContainer>
          </>
        )}

        {activeTab === "flow" && (
          <>
            <div style={{ fontSize: 11, color: "#64748b", marginBottom: 16 }}>
              개인·외국인 순매수 (억원)
            </div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={enriched} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}
                barGap={2} barCategoryGap="30%">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 10 }} axisLine={false} tickLine={false} />
                <YAxis tickFormatter={v => (v / 100).toFixed(0) + "억"} tick={{ fill: "#64748b", fontSize: 9 }} axisLine={false} tickLine={false} />
                <Tooltip
                  formatter={(v, name) => [(v / 100).toFixed(0) + "억", name === "individual" ? "개인" : "외국인"]}
                  labelStyle={{ color: "#94a3b8", fontSize: 11 }}
                  contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 6 }}
                />
                <ReferenceLine y={0} stroke="#334155" />
                <Bar dataKey="individual" name="individual" fill="#38bdf8" radius={[3, 3, 0, 0]} opacity={0.85} />
                <Bar dataKey="foreign" name="foreign" fill="#fb923c" radius={[3, 3, 0, 0]} opacity={0.85} />
              </BarChart>
            </ResponsiveContainer>
            <div style={{ display: "flex", gap: 16, marginTop: 10 }}>
              {[{ color: "#38bdf8", label: "개인" }, { color: "#fb923c", label: "외국인" }].map(l => (
                <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                  <div style={{ width: 8, height: 8, borderRadius: 2, background: l.color }} />
                  <span style={{ fontSize: 10, color: "#64748b" }}>{l.label}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Data Table */}
      <div style={{
        background: "#0d1929", border: "1px solid #1e293b",
        borderRadius: 10, overflow: "hidden", marginBottom: 24
      }}>
        <div style={{
          padding: "12px 16px", borderBottom: "1px solid #1e293b",
          fontSize: 11, color: "#64748b", letterSpacing: "0.05em"
        }}>
          원본 데이터 (최근 7거래일)
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11 }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #1e293b" }}>
              {["날짜", "개인", "외국인", "기관", "피로지수"].map(h => (
                <th key={h} style={{
                  padding: "8px 12px", textAlign: h === "날짜" ? "left" : "right",
                  color: "#475569", fontWeight: 500, letterSpacing: "0.05em"
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...enriched].reverse().map((row, i) => {
              const s = statusFromScore(row.fatigue);
              return (
                <tr key={row.date} style={{
                  background: i % 2 === 0 ? "transparent" : "#0a1520",
                  borderBottom: "1px solid #0f1f30"
                }}>
                  <td style={{ padding: "8px 12px", color: "#94a3b8" }}>{row.date}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right", color: row.individual >= 0 ? "#38bdf8" : "#f87171" }}>
                    {fmt(row.individual)}
                  </td>
                  <td style={{ padding: "8px 12px", textAlign: "right", color: row.foreign >= 0 ? "#a78bfa" : "#fb923c" }}>
                    {fmt(row.foreign)}
                  </td>
                  <td style={{ padding: "8px 12px", textAlign: "right", color: row.institution >= 0 ? "#6ee7b7" : "#fca5a5" }}>
                    {fmt(row.institution)}
                  </td>
                  <td style={{ padding: "8px 12px", textAlign: "right" }}>
                    <span style={{
                      color: s.color, background: `${s.color}22`,
                      padding: "2px 8px", borderRadius: 4, fontWeight: 700
                    }}>
                      {row.fatigue}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div style={{ fontSize: 10, color: "#334155", lineHeight: 1.6 }}>
        <div>피로지수 산출: 개인 순매수 + 외국인 순매수 기반 가중 감점 모델 (0~100점)</div>
        <div>실제 운용 시: pykrx <code style={{ color: "#475569" }}>get_market_net_purchases_of_equities</code> 로 교체 필요</div>
        <div style={{ marginTop: 4, color: "#1e293b" }}>
          임계값 (78 / 60점) 및 가중치는 백테스트 기반으로 조정 권장
        </div>
      </div>
    </div>
  );
}
