import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, Area, AreaChart } from "recharts";

const reviewData = [
  { day: "6/17", count: 24 }, { day: "6/18", count: 31 }, { day: "6/19", count: 18 },
  { day: "6/20", count: 42 }, { day: "6/21", count: 35 }, { day: "6/22", count: 28 }, { day: "6/23", count: 12 },
];

const retentionData = [
  { day: "6/17", rate: 82 }, { day: "6/18", rate: 78 }, { day: "6/19", rate: 85 },
  { day: "6/20", rate: 91 }, { day: "6/21", rate: 88 }, { day: "6/22", rate: 93 }, { day: "6/23", rate: 90 },
];

const cards = [
  { id: 1, front: "Python 中 list 和 tuple 的区别？", back: "list 是可变的有序序列，支持增删改；tuple 是不可变的有序序列，创建后不能修改，但可以作为字典的 key。tuple 性能略优于 list。", tag: "Python", type: "flashcard", stage: 3, mastery: 65 },
  { id: 2, front: "什么是闭包（Closure）？", back: "闭包是指一个函数能够记住并访问其词法作用域中的变量，即使该函数在其词法作用域之外执行。Python 中通过嵌套函数实现闭包。", tag: "编程基础", type: "knowledge", stage: 5, mastery: 85 },
  { id: 3, front: "「生活不是等待暴风雨过去，而是学会在雨中跳舞。」", back: "—— 维维安·格林\n\n核心：适应力与积极心态。不要等待完美的条件，而是在当下找到行动的力量。", tag: "语录", type: "quote", stage: 2, mastery: 40 },
  { id: 4, front: "HTTP 状态码 301 和 302 的区别？", back: "301 是永久重定向，搜索引擎会更新索引；302 是临时重定向，搜索引擎保留原 URL。301 有利于 SEO 迁移。", tag: "网络", type: "flashcard", stage: 4, mastery: 75 },
];

const decks = [
  { name: "Python", count: 48, due: 8, color: "#5B8C7A" },
  { name: "编程基础", count: 35, due: 5, color: "#7BAFD4" },
  { name: "网络协议", count: 22, due: 3, color: "#D4A574" },
  { name: "语录收藏", count: 15, due: 4, color: "#C48B9F" },
];

export default function ModernMinimalist() {
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
      setFlipped(false);
      setFeedback(null);
      setReviewed(reviewed + 1);
      if (cardIdx < cards.length - 1) setCardIdx(cardIdx + 1);
      else setCardIdx(0);
    }, 400);
  };

  const navItems = [
    { id: "dashboard", label: "今日概览", icon: "◉" },
    { id: "review", label: "开始复习", icon: "↻" },
    { id: "manage", label: "卡片管理", icon: "☰" },
    { id: "stats", label: "学习统计", icon: "◈" },
  ];

  return (
    <div style={{ display: "flex", width: 960, height: 620, fontFamily: "'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif", background: "#F7F6F3", borderRadius: 12, overflow: "hidden", boxShadow: "0 4px 24px rgba(0,0,0,0.08)" }}>
      {/* Sidebar */}
      <div style={{ width: 200, background: "#FFFFFF", borderRight: "1px solid #EDEDEB", display: "flex", flexDirection: "column", padding: "28px 0" }}>
        <div style={{ padding: "0 24px", marginBottom: 36 }}>
          <div style={{ fontSize: 20, fontWeight: 600, color: "#2D3436", letterSpacing: 1 }}>忆 · Recall</div>
          <div style={{ fontSize: 11, color: "#B2BEC3", marginTop: 4 }}>Ebbinghaus Review</div>
        </div>
        {navItems.map(item => (
          <div key={item.id}
            onClick={() => { setView(item.id); setFlipped(false); setCardIdx(0); setReviewed(0); }}
            style={{
              padding: "10px 24px", cursor: "pointer", display: "flex", alignItems: "center", gap: 10,
              fontSize: 14, color: view === item.id ? "#5B8C7A" : "#636E72", fontWeight: view === item.id ? 600 : 400,
              background: view === item.id ? "#F0F5F2" : "transparent",
              borderLeft: view === item.id ? "3px solid #5B8C7A" : "3px solid transparent",
              transition: "all 0.2s"
            }}>
            <span style={{ fontSize: 16 }}>{item.icon}</span>
            {item.label}
          </div>
        ))}
        <div style={{ flex: 1 }} />
        <div style={{ padding: "0 24px", fontSize: 11, color: "#B2BEC3" }}>
          <div style={{ padding: "12px 16px", background: "#F9F9F7", borderRadius: 10 }}>
            <div style={{ fontWeight: 600, color: "#5B8C7A", marginBottom: 4 }}>连续学习 12 天</div>
            <div style={{ width: "100%", height: 4, background: "#E8E8E4", borderRadius: 2 }}>
              <div style={{ width: "72%", height: "100%", background: "#5B8C7A", borderRadius: 2 }} />
            </div>
            <div style={{ marginTop: 4, fontSize: 10 }}>距下一个里程碑: 3 天</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, padding: "28px 32px", overflowY: "auto" }}>
        {/* Dashboard View */}
        {view === "dashboard" && (
          <div>
            <div style={{ marginBottom: 28 }}>
              <div style={{ fontSize: 22, fontWeight: 600, color: "#2D3436" }}>早上好 ☀️</div>
              <div style={{ fontSize: 13, color: "#B2BEC3", marginTop: 4 }}>今天有 20 张卡片等待复习</div>
            </div>

            {/* Stats Row */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 14, marginBottom: 28 }}>
              {[
                { label: "今日待复习", value: "20", sub: "已完成 12", accent: "#5B8C7A" },
                { label: "记忆留存率", value: "90%", sub: "↑ 2% vs 昨日", accent: "#7BAFD4" },
                { label: "总卡片数", value: "120", sub: "已掌握 68", accent: "#D4A574" },
                { label: "连续天数", value: "12", sub: "最长 18 天", accent: "#C48B9F" },
              ].map((s, i) => (
                <div key={i} style={{ background: "#FFF", borderRadius: 12, padding: "18px 20px", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
                  <div style={{ fontSize: 11, color: "#B2BEC3", marginBottom: 8 }}>{s.label}</div>
                  <div style={{ fontSize: 28, fontWeight: 700, color: s.accent }}>{s.value}</div>
                  <div style={{ fontSize: 11, color: "#636E72", marginTop: 4 }}>{s.sub}</div>
                </div>
              ))}
            </div>

            {/* Due Cards + Decks */}
            <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 16 }}>
              <div style={{ background: "#FFF", borderRadius: 12, padding: "20px 24px", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: "#2D3436", marginBottom: 16 }}>即将复习</div>
                {cards.slice(0, 3).map((c, i) => (
                  <div key={i} style={{ padding: "12px 0", borderBottom: i < 2 ? "1px solid #F0F0ED" : "none", display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: c.mastery < 50 ? "#E17055" : c.mastery < 80 ? "#FDCB6E" : "#5B8C7A" }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13, color: "#2D3436", lineHeight: 1.4 }}>{c.front.length > 30 ? c.front.slice(0, 30) + "..." : c.front}</div>
                      <div style={{ fontSize: 11, color: "#B2BEC3", marginTop: 2 }}>{c.tag} · 第{c.stage}阶段</div>
                    </div>
                    <div style={{ fontSize: 11, color: "#B2BEC3" }}>熟练度 {c.mastery}%</div>
                  </div>
                ))}
              </div>
              <div style={{ background: "#FFF", borderRadius: 12, padding: "20px 24px", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: "#2D3436", marginBottom: 16 }}>卡组概览</div>
                {decks.map((d, i) => (
                  <div key={i} style={{ padding: "10px 0", borderBottom: i < decks.length - 1 ? "1px solid #F0F0ED" : "none", display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: d.color + "18", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, color: d.color, fontWeight: 600 }}>{d.count}</div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13, color: "#2D3436" }}>{d.name}</div>
                      <div style={{ fontSize: 11, color: "#B2BEC3" }}>{d.due} 张待复习</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Review View */}
        {view === "review" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", height: "100%" }}>
            <div style={{ display: "flex", justifyContent: "space-between", width: "100%", marginBottom: 20 }}>
              <div style={{ fontSize: 13, color: "#B2BEC3" }}>第 {reviewed + 1} / {cards.length} 张</div>
              <div style={{ fontSize: 13, color: "#5B8C7A", fontWeight: 600 }}>{currentCard.tag}</div>
            </div>

            {/* Progress bar */}
            <div style={{ width: "100%", height: 3, background: "#E8E8E4", borderRadius: 2, marginBottom: 28 }}>
              <div style={{ width: `${(reviewed / cards.length) * 100}%`, height: "100%", background: "#5B8C7A", borderRadius: 2, transition: "width 0.3s" }} />
            </div>

            {/* Card */}
            <div onClick={handleFlip}
              style={{
                width: "100%", maxWidth: 520, minHeight: 260, background: "#FFF", borderRadius: 16, padding: "36px 32px",
                boxShadow: flipped ? "0 8px 32px rgba(91,140,122,0.12)" : "0 2px 12px rgba(0,0,0,0.06)",
                cursor: "pointer", transition: "all 0.3s", display: "flex", flexDirection: "column", justifyContent: "center",
                transform: flipped ? "scale(1.01)" : "scale(1)",
                opacity: feedback ? 0.5 : 1,
              }}>
              {!flipped ? (
                <div>
                  <div style={{ fontSize: 11, color: "#B2BEC3", marginBottom: 12, textTransform: "uppercase", letterSpacing: 1 }}>
                    {currentCard.type === "quote" ? "语录" : currentCard.type === "knowledge" ? "知识点" : "记忆卡片"} · 点击翻转
                  </div>
                  <div style={{ fontSize: 18, color: "#2D3436", lineHeight: 1.7, fontWeight: 500 }}>{currentCard.front}</div>
                </div>
              ) : (
                <div>
                  <div style={{ fontSize: 11, color: "#5B8C7A", marginBottom: 12, textTransform: "uppercase", letterSpacing: 1 }}>答案</div>
                  <div style={{ fontSize: 15, color: "#636E72", lineHeight: 1.8, whiteSpace: "pre-line" }}>{currentCard.back}</div>
                </div>
              )}
            </div>

            {/* Feedback Buttons */}
            {flipped && (
              <div style={{ display: "flex", gap: 16, marginTop: 28 }}>
                {[
                  { label: "忘了", sub: "重头来过", color: "#E17055", bg: "#FFF5F3", type: "forgot" },
                  { label: "模糊", sub: "再来一次", color: "#FDCB6E", bg: "#FFFBF0", type: "fuzzy" },
                  { label: "记住了", sub: "下次间隔更长", color: "#5B8C7A", bg: "#F0F5F2", type: "remembered" },
                ].map(btn => (
                  <div key={btn.type} onClick={() => handleFeedback(btn.type)}
                    style={{
                      padding: "14px 28px", borderRadius: 12, background: btn.bg, cursor: "pointer",
                      border: `1.5px solid ${btn.color}30`, textAlign: "center", transition: "all 0.2s",
                      minWidth: 120
                    }}>
                    <div style={{ fontSize: 15, fontWeight: 600, color: btn.color }}>{btn.label}</div>
                    <div style={{ fontSize: 11, color: "#B2BEC3", marginTop: 2 }}>{btn.sub}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Mastery indicator */}
            <div style={{ marginTop: 24, display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ fontSize: 11, color: "#B2BEC3" }}>当前熟练度</div>
              <div style={{ width: 120, height: 4, background: "#E8E8E4", borderRadius: 2 }}>
                <div style={{ width: `${currentCard.mastery}%`, height: "100%", background: currentCard.mastery < 50 ? "#E17055" : currentCard.mastery < 80 ? "#FDCB6E" : "#5B8C7A", borderRadius: 2 }} />
              </div>
              <div style={{ fontSize: 11, color: "#636E72" }}>{currentCard.mastery}%</div>
            </div>
          </div>
        )}

        {/* Manage View */}
        {view === "manage" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
              <div style={{ fontSize: 18, fontWeight: 600, color: "#2D3436" }}>卡片管理</div>
              <div style={{ padding: "8px 20px", background: "#5B8C7A", color: "#FFF", borderRadius: 8, fontSize: 13, cursor: "pointer", fontWeight: 500 }}>+ 新建卡片</div>
            </div>

            {/* Filter tabs */}
            <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
              {["全部", "记忆卡片", "知识点", "语录"].map((t, i) => (
                <div key={i} style={{
                  padding: "6px 16px", borderRadius: 20, fontSize: 12, cursor: "pointer",
                  background: i === 0 ? "#5B8C7A" : "#FFF", color: i === 0 ? "#FFF" : "#636E72",
                  border: i === 0 ? "none" : "1px solid #EDEDEB"
                }}>{t}</div>
              ))}
            </div>

            {/* Search bar */}
            <div style={{ padding: "10px 16px", background: "#FFF", borderRadius: 10, border: "1px solid #EDEDEB", marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ color: "#B2BEC3", fontSize: 14 }}>⌕</span>
              <div style={{ fontSize: 13, color: "#B2BEC3" }}>搜索卡片内容、标签...</div>
            </div>

            {/* Card list */}
            {cards.map((c, i) => (
              <div key={i} style={{
                background: "#FFF", borderRadius: 12, padding: "18px 22px", marginBottom: 10,
                boxShadow: "0 1px 4px rgba(0,0,0,0.03)", display: "flex", alignItems: "flex-start", gap: 16
              }}>
                <div style={{
                  padding: "3px 10px", borderRadius: 6, fontSize: 10, fontWeight: 600,
                  background: c.type === "quote" ? "#FFF0F3" : c.type === "knowledge" ? "#F0F5FF" : "#F0F5F2",
                  color: c.type === "quote" ? "#C48B9F" : c.type === "knowledge" ? "#7BAFD4" : "#5B8C7A",
                  whiteSpace: "nowrap"
                }}>
                  {c.type === "quote" ? "语录" : c.type === "knowledge" ? "知识点" : "卡片"}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, color: "#2D3436", lineHeight: 1.5 }}>{c.front}</div>
                  <div style={{ fontSize: 12, color: "#B2BEC3", marginTop: 6 }}>{c.tag} · 阶段{c.stage} · 熟练度 {c.mastery}%</div>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <div style={{ width: 60, height: 4, background: "#E8E8E4", borderRadius: 2 }}>
                    <div style={{ width: `${c.mastery}%`, height: "100%", background: c.mastery < 50 ? "#E17055" : c.mastery < 80 ? "#FDCB6E" : "#5B8C7A", borderRadius: 2 }} />
                  </div>
                  <span style={{ fontSize: 16, color: "#B2BEC3", cursor: "pointer" }}>⋯</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Stats View */}
        {view === "stats" && (
          <div>
            <div style={{ fontSize: 18, fontWeight: 600, color: "#2D3436", marginBottom: 24 }}>学习统计</div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
              <div style={{ background: "#FFF", borderRadius: 12, padding: "20px 24px", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#2D3436", marginBottom: 16 }}>每日复习量</div>
                <ResponsiveContainer width="100%" height={140}>
                  <BarChart data={reviewData}>
                    <XAxis dataKey="day" tick={{ fontSize: 10, fill: "#B2BEC3" }} axisLine={false} tickLine={false} />
                    <YAxis hide />
                    <Tooltip contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 2px 8px rgba(0,0,0,0.1)", fontSize: 12 }} />
                    <Bar dataKey="count" fill="#5B8C7A" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div style={{ background: "#FFF", borderRadius: 12, padding: "20px 24px", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#2D3436", marginBottom: 16 }}>记忆留存率趋势</div>
                <ResponsiveContainer width="100%" height={140}>
                  <AreaChart data={retentionData}>
                    <defs>
                      <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#7BAFD4" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#7BAFD4" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="day" tick={{ fontSize: 10, fill: "#B2BEC3" }} axisLine={false} tickLine={false} />
                    <YAxis hide domain={[70, 100]} />
                    <Tooltip contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 2px 8px rgba(0,0,0,0.1)", fontSize: 12 }} />
                    <Area type="monotone" dataKey="rate" stroke="#7BAFD4" fill="url(#colorRate)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Memory stages overview */}
            <div style={{ background: "#FFF", borderRadius: 12, padding: "20px 24px", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "#2D3436", marginBottom: 16 }}>记忆阶段分布</div>
              <div style={{ display: "flex", gap: 8, alignItems: "flex-end", height: 80 }}>
                {["5分钟", "30分钟", "12小时", "1天", "2天", "4天", "7天", "15天", "30天", "长期"].map((label, i) => {
                  const heights = [12, 18, 25, 35, 28, 42, 55, 38, 20, 65];
                  return (
                    <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                      <div style={{ fontSize: 10, color: "#5B8C7A", fontWeight: 600 }}>{heights[i]}</div>
                      <div style={{ width: "100%", height: heights[i], background: `rgba(91,140,122,${0.2 + i * 0.08})`, borderRadius: 4 }} />
                      <div style={{ fontSize: 8, color: "#B2BEC3", whiteSpace: "nowrap" }}>{label}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}