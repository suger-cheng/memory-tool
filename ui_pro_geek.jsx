import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, AreaChart, Area } from "recharts";

const reviewData = [
  { day: "Mon", count: 24, forgot: 4, fuzzy: 6, ok: 14 },
  { day: "Tue", count: 31, forgot: 5, fuzzy: 8, ok: 18 },
  { day: "Wed", count: 18, forgot: 2, fuzzy: 4, ok: 12 },
  { day: "Thu", count: 42, forgot: 6, fuzzy: 10, ok: 26 },
  { day: "Fri", count: 35, forgot: 3, fuzzy: 7, ok: 25 },
  { day: "Sat", count: 28, forgot: 4, fuzzy: 5, ok: 19 },
  { day: "Sun", count: 12, forgot: 1, fuzzy: 2, ok: 9 },
];

const radarData = [
  { subject: "Python", A: 85 }, { subject: "网络", A: 72 }, { subject: "算法", A: 65 },
  { subject: "数据库", A: 78 }, { subject: "系统", A: 58 }, { subject: "语录", A: 92 },
];

const heatmapData = Array.from({ length: 28 }, (_, i) => ({
  day: i, value: Math.floor(Math.random() * 50) + 5,
}));

const cards = [
  { id: 1, front: "Python GIL 的作用与限制？", back: "GIL（全局解释器锁）确保同一时刻只有一个线程执行 Python 字节码。保证了线程安全但限制了 CPU 密集型任务的多线程并行能力。解决方案：multiprocessing、C扩展、或使用 asyncio。", tag: "Python", type: "flashcard", stage: 4, mastery: 72, ease: 2.3, interval: "4d" },
  { id: 2, front: "TCP 三次握手过程", back: "SYN → SYN-ACK → ACK\n客户端发起连接请求(SYN)，服务器回应(SYN-ACK)，客户端确认(ACK)。确保双方都具备收发能力。", tag: "网络", type: "knowledge", stage: 6, mastery: 88, ease: 2.6, interval: "15d" },
  { id: 3, front: "「先完成，再完美。」", back: "—— Reid Hoffman (LinkedIn 创始人)\n\nDone is better than perfect. 避免完美主义导致的分析瘫痪，迭代式改进往往更高效。", tag: "语录", type: "quote", stage: 2, mastery: 35, ease: 1.8, interval: "12h" },
  { id: 4, front: "时间复杂度 O(n log n) 的排序算法有哪些？", back: "归并排序(Merge Sort)、快速排序(Quick Sort, 平均)、堆排序(Heap Sort)。其中快排常数因子最小，实践中最快。", tag: "算法", type: "flashcard", stage: 5, mastery: 80, ease: 2.4, interval: "7d" },
];

export default function ProGeek() {
  const [view, setView] = useState("dashboard");
  const [flipped, setFlipped] = useState(false);
  const [cardIdx, setCardIdx] = useState(0);
  const [reviewed, setReviewed] = useState(0);
  const [feedback, setFeedback] = useState(null);

  const currentCard = cards[cardIdx];

  const handleFlip = () => setFlipped(!flipped);
  const handleFeedback = (type) => {
    setFeedback(type);
    setTimeout(() => {
      setFlipped(false); setFeedback(null); setReviewed(reviewed + 1);
      if (cardIdx < cards.length - 1) setCardIdx(cardIdx + 1); else setCardIdx(0);
    }, 300);
  };

  const S = {
    bg: "#0F0F17", panel: "#1A1A2E", border: "#2A2A42", text: "#E0E0E8", muted: "#6B6B8D",
    accent: "#8B5CF6", accent2: "#06D6A0", accent3: "#3B82F6", danger: "#EF4444", warn: "#F59E0B",
  };

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: "⬡" },
    { id: "review", label: "Review", icon: "⟳" },
    { id: "manage", label: "Cards", icon: "▤" },
    { id: "stats", label: "Analytics", icon: "◫" },
  ];

  return (
    <div style={{ display: "flex", width: 960, height: 620, fontFamily: "'Cascadia Code', 'JetBrains Mono', 'Consolas', monospace", background: S.bg, borderRadius: 8, overflow: "hidden", boxShadow: "0 8px 32px rgba(0,0,0,0.5)" }}>
      {/* Sidebar */}
      <div style={{ width: 180, background: S.panel, borderRight: `1px solid ${S.border}`, display: "flex", flexDirection: "column", padding: "20px 0" }}>
        <div style={{ padding: "0 18px", marginBottom: 32 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 28, height: 28, borderRadius: 6, background: `linear-gradient(135deg, ${S.accent}, ${S.accent2})`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, color: "#FFF" }}>E</div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: S.text, letterSpacing: 1 }}>RECALL</div>
              <div style={{ fontSize: 9, color: S.muted }}>v2.0 · Ebbinghaus</div>
            </div>
          </div>
        </div>

        {navItems.map(item => (
          <div key={item.id} onClick={() => { setView(item.id); setFlipped(false); setCardIdx(0); setReviewed(0); }}
            style={{
              padding: "9px 18px", cursor: "pointer", display: "flex", alignItems: "center", gap: 8,
              fontSize: 12, color: view === item.id ? S.accent : S.muted,
              fontWeight: view === item.id ? 600 : 400,
              background: view === item.id ? S.accent + "12" : "transparent",
              borderLeft: view === item.id ? `2px solid ${S.accent}` : "2px solid transparent",
            }}>
            <span style={{ fontSize: 14 }}>{item.icon}</span>
            {item.label}
          </div>
        ))}

        <div style={{ flex: 1 }} />
        <div style={{ padding: "0 18px" }}>
          <div style={{ padding: "12px", background: S.border + "40", borderRadius: 8, fontSize: 10 }}>
            <div style={{ color: S.accent2, fontWeight: 600, marginBottom: 6 }}>SESSION</div>
            <div style={{ color: S.muted }}>Streak: <span style={{ color: S.accent2 }}>12d</span></div>
            <div style={{ color: S.muted }}>Today: <span style={{ color: S.text }}>12/20</span></div>
            <div style={{ color: S.muted }}>Rate: <span style={{ color: S.accent }}>90%</span></div>
          </div>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, padding: "20px 24px", overflowY: "auto" }}>
        {/* Dashboard */}
        {view === "dashboard" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div>
                <div style={{ fontSize: 18, fontWeight: 700, color: S.text }}>Command Center</div>
                <div style={{ fontSize: 11, color: S.muted, marginTop: 2 }}>20 cards pending · 4 decks active</div>
              </div>
              <div style={{ padding: "7px 16px", background: S.accent, color: "#FFF", borderRadius: 6, fontSize: 11, cursor: "pointer", fontWeight: 600 }}>▶ START REVIEW</div>
            </div>

            {/* Stat cards */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 18 }}>
              {[
                { label: "DUE", value: "20", color: S.accent, icon: "◉" },
                { label: "RETENTION", value: "90%", color: S.accent2, icon: "◈" },
                { label: "MASTERED", value: "68", color: S.accent3, icon: "◆" },
                { label: "STREAK", value: "12d", color: S.warn, icon: "▲" },
              ].map((s, i) => (
                <div key={i} style={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 8, padding: "14px 16px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ fontSize: 9, color: S.muted, letterSpacing: 1 }}>{s.label}</div>
                    <div style={{ fontSize: 12, color: s.color }}>{s.icon}</div>
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: s.color, marginTop: 4 }}>{s.value}</div>
                </div>
              ))}
            </div>

            {/* Charts row */}
            <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 12 }}>
              <div style={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 8, padding: "16px" }}>
                <div style={{ fontSize: 11, color: S.muted, marginBottom: 12, letterSpacing: 1 }}>WEEKLY REVIEW VOLUME</div>
                <ResponsiveContainer width="100%" height={140}>
                  <BarChart data={reviewData}>
                    <XAxis dataKey="day" tick={{ fontSize: 9, fill: S.muted }} axisLine={false} tickLine={false} />
                    <YAxis hide />
                    <Tooltip contentStyle={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 6, fontSize: 10, color: S.text }} />
                    <Bar dataKey="ok" stackId="a" fill={S.accent2} radius={[0,0,0,0]} />
                    <Bar dataKey="fuzzy" stackId="a" fill={S.warn} radius={[0,0,0,0]} />
                    <Bar dataKey="forgot" stackId="a" fill={S.danger} radius={[4,4,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div style={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 8, padding: "16px" }}>
                <div style={{ fontSize: 11, color: S.muted, marginBottom: 12, letterSpacing: 1 }}>SKILL RADAR</div>
                <ResponsiveContainer width="100%" height={140}>
                  <RadarChart data={radarData} cx="50%" cy="50%" outerRadius={55}>
                    <PolarGrid stroke={S.border} />
                    <PolarAngleAxis dataKey="subject" tick={{ fontSize: 9, fill: S.muted }} />
                    <Radar dataKey="A" stroke={S.accent} fill={S.accent} fillOpacity={0.2} strokeWidth={2} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Activity heatmap */}
            <div style={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 8, padding: "14px 16px", marginTop: 12 }}>
              <div style={{ fontSize: 11, color: S.muted, marginBottom: 10, letterSpacing: 1 }}>ACTIVITY HEATMAP · LAST 4 WEEKS</div>
              <div style={{ display: "flex", gap: 3, flexWrap: "wrap" }}>
                {heatmapData.map((d, i) => (
                  <div key={i} style={{
                    width: 18, height: 18, borderRadius: 3,
                    background: d.value < 15 ? S.border : d.value < 30 ? S.accent + "40" : d.value < 40 ? S.accent + "80" : S.accent,
                  }} title={`${d.value} cards`} />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Review */}
        {view === "review" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", height: "100%" }}>
            {/* Header bar */}
            <div style={{ width: "100%", display: "flex", justifyContent: "space-between", marginBottom: 8, fontSize: 10, color: S.muted }}>
              <span>CARD {reviewed + 1}/{cards.length}</span>
              <span style={{ color: S.accent }}>{currentCard.tag}</span>
              <span>EASE: {currentCard.ease}x</span>
            </div>
            {/* Progress */}
            <div style={{ width: "100%", height: 2, background: S.border, borderRadius: 1, marginBottom: 24 }}>
              <div style={{ width: `${(reviewed / cards.length) * 100}%`, height: "100%", background: `linear-gradient(90deg, ${S.accent}, ${S.accent2})`, borderRadius: 1, transition: "width 0.3s" }} />
            </div>

            {/* Card */}
            <div onClick={handleFlip}
              style={{
                width: "100%", maxWidth: 520, minHeight: 240, background: S.panel,
                border: `1px solid ${flipped ? S.accent + "60" : S.border}`, borderRadius: 10, padding: "32px 28px",
                cursor: "pointer", transition: "all 0.25s",
                boxShadow: flipped ? `0 0 24px ${S.accent}15` : "none",
                opacity: feedback ? 0.4 : 1,
              }}>
              {!flipped ? (
                <div>
                  <div style={{ fontSize: 9, color: S.accent, letterSpacing: 2, marginBottom: 16 }}>
                    [{currentCard.type === "quote" ? "QUOTE" : currentCard.type === "knowledge" ? "KNOWLEDGE" : "FLASHCARD"}] · CLICK TO REVEAL
                  </div>
                  <div style={{ fontSize: 16, color: S.text, lineHeight: 1.7, fontWeight: 500 }}>{currentCard.front}</div>
                </div>
              ) : (
                <div>
                  <div style={{ fontSize: 9, color: S.accent2, letterSpacing: 2, marginBottom: 16 }}>[ANSWER]</div>
                  <div style={{ fontSize: 13, color: "#B0B0C0", lineHeight: 1.8, whiteSpace: "pre-line", fontFamily: "'Segoe UI', 'Microsoft YaHei', sans-serif" }}>{currentCard.back}</div>
                </div>
              )}
            </div>

            {/* Feedback */}
            {flipped && (
              <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
                {[
                  { label: "FORGOT", key: "1", color: S.danger, desc: "Reset to 5min" },
                  { label: "FUZZY", key: "2", color: S.warn, desc: "Repeat current" },
                  { label: "REMEMBERED", key: "3", color: S.accent2, desc: `Next: ${currentCard.interval}` },
                ].map(btn => (
                  <div key={btn.key} onClick={() => handleFeedback(btn.key)}
                    style={{
                      padding: "12px 24px", borderRadius: 8, cursor: "pointer", textAlign: "center",
                      background: btn.color + "12", border: `1px solid ${btn.color}40`, minWidth: 130,
                    }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: btn.color, letterSpacing: 1 }}>{btn.label}</div>
                    <div style={{ fontSize: 9, color: S.muted, marginTop: 3 }}>{btn.desc}</div>
                    <div style={{ fontSize: 9, color: S.muted, marginTop: 2 }}>[{btn.key}]</div>
                  </div>
                ))}
              </div>
            )}

            {/* Meta */}
            <div style={{ marginTop: 20, display: "flex", gap: 24, fontSize: 10, color: S.muted }}>
              <span>MASTERY: <span style={{ color: currentCard.mastery > 70 ? S.accent2 : S.warn }}>{currentCard.mastery}%</span></span>
              <span>STAGE: <span style={{ color: S.text }}>{currentCard.stage}/9</span></span>
              <span>EASE: <span style={{ color: S.text }}>{currentCard.ease}x</span></span>
            </div>
          </div>
        )}

        {/* Manage */}
        {view === "manage" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
              <div style={{ fontSize: 16, fontWeight: 700, color: S.text }}>Card Database</div>
              <div style={{ padding: "6px 14px", background: S.accent, color: "#FFF", borderRadius: 6, fontSize: 11, cursor: "pointer" }}>+ NEW CARD</div>
            </div>

            <div style={{ display: "flex", gap: 6, marginBottom: 14 }}>
              {["ALL", "FLASHCARD", "KNOWLEDGE", "QUOTE"].map((t, i) => (
                <div key={i} style={{
                  padding: "5px 12px", borderRadius: 4, fontSize: 10, cursor: "pointer", letterSpacing: 1,
                  background: i === 0 ? S.accent + "20" : "transparent", color: i === 0 ? S.accent : S.muted,
                  border: `1px solid ${i === 0 ? S.accent + "40" : S.border}`,
                }}>{t}</div>
              ))}
            </div>

            {cards.map((c, i) => (
              <div key={i} style={{
                background: S.panel, border: `1px solid ${S.border}`, borderRadius: 8, padding: "14px 18px", marginBottom: 8,
                display: "flex", alignItems: "center", gap: 14,
              }}>
                <div style={{
                  padding: "2px 8px", borderRadius: 4, fontSize: 9, fontWeight: 600, letterSpacing: 1,
                  background: c.type === "quote" ? S.warn + "20" : c.type === "knowledge" ? S.accent3 + "20" : S.accent + "20",
                  color: c.type === "quote" ? S.warn : c.type === "knowledge" ? S.accent3 : S.accent,
                }}>
                  {c.type === "quote" ? "QUOTE" : c.type === "knowledge" ? "KNOW" : "CARD"}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, color: S.text, lineHeight: 1.5, fontFamily: "'Segoe UI', 'Microsoft YaHei', sans-serif" }}>{c.front}</div>
                  <div style={{ fontSize: 10, color: S.muted, marginTop: 4 }}>{c.tag} · S{c.stage} · Ease {c.ease}x</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: c.mastery > 70 ? S.accent2 : c.mastery > 40 ? S.warn : S.danger }}>{c.mastery}%</div>
                  <div style={{ fontSize: 9, color: S.muted }}>mastery</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Stats */}
        {view === "stats" && (
          <div>
            <div style={{ fontSize: 16, fontWeight: 700, color: S.text, marginBottom: 18 }}>Analytics Dashboard</div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 }}>
              <div style={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 8, padding: "16px" }}>
                <div style={{ fontSize: 10, color: S.muted, letterSpacing: 1, marginBottom: 12 }}>RETENTION RATE TREND</div>
                <ResponsiveContainer width="100%" height={130}>
                  <AreaChart data={reviewData.map(d => ({ day: d.day, rate: Math.round((d.ok / d.count) * 100) }))}>
                    <defs>
                      <linearGradient id="grdAcc" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={S.accent} stopOpacity={0.3}/>
                        <stop offset="95%" stopColor={S.accent} stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="day" tick={{ fontSize: 9, fill: S.muted }} axisLine={false} tickLine={false} />
                    <YAxis hide domain={[50, 100]} />
                    <Tooltip contentStyle={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 6, fontSize: 10, color: S.text }} />
                    <Area type="monotone" dataKey="rate" stroke={S.accent} fill="url(#grdAcc)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div style={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 8, padding: "16px" }}>
                <div style={{ fontSize: 10, color: S.muted, letterSpacing: 1, marginBottom: 12 }}>KNOWLEDGE RADAR</div>
                <ResponsiveContainer width="100%" height={130}>
                  <RadarChart data={radarData} cx="50%" cy="50%" outerRadius={50}>
                    <PolarGrid stroke={S.border} />
                    <PolarAngleAxis dataKey="subject" tick={{ fontSize: 9, fill: S.muted }} />
                    <Radar dataKey="A" stroke={S.accent2} fill={S.accent2} fillOpacity={0.15} strokeWidth={2} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Forgetting curve */}
            <div style={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 8, padding: "16px" }}>
              <div style={{ fontSize: 10, color: S.muted, letterSpacing: 1, marginBottom: 12 }}>FORGETTING CURVE · THEORY vs ACTUAL</div>
              <ResponsiveContainer width="100%" height={120}>
                <LineChart data={[
                  { t: "0h", theory: 100, actual: 100 }, { t: "20m", theory: 58, actual: 65 },
                  { t: "1h", theory: 44, actual: 52 }, { t: "9h", theory: 36, actual: 45 },
                  { t: "1d", theory: 33, actual: 42 }, { t: "2d", theory: 28, actual: 38 },
                  { t: "6d", theory: 25, actual: 35 }, { t: "31d", theory: 21, actual: 32 },
                ]}>
                  <CartesianGrid stroke={S.border} strokeDasharray="3 3" />
                  <XAxis dataKey="t" tick={{ fontSize: 9, fill: S.muted }} axisLine={false} />
                  <YAxis tick={{ fontSize: 9, fill: S.muted }} axisLine={false} domain={[0, 100]} />
                  <Tooltip contentStyle={{ background: S.panel, border: `1px solid ${S.border}`, borderRadius: 6, fontSize: 10, color: S.text }} />
                  <Line type="monotone" dataKey="theory" stroke={S.danger} strokeDasharray="5 5" strokeWidth={1.5} dot={false} name="Theoretical" />
                  <Line type="monotone" dataKey="actual" stroke={S.accent2} strokeWidth={2} dot={{ fill: S.accent2, r: 3 }} name="Your Performance" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}