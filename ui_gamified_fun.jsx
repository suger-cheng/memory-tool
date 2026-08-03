import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar, PolarAngleAxis } from "recharts";

const weekData = [
  { day: "一", count: 24, xp: 120 }, { day: "二", count: 31, xp: 155 }, { day: "三", count: 18, xp: 90 },
  { day: "四", count: 42, xp: 210 }, { day: "五", count: 35, xp: 175 }, { day: "六", count: 28, xp: 140 }, { day: "日", count: 12, xp: 60 },
];

const cards = [
  { id: 1, front: "什么是递归？用生活中的例子解释。", back: "递归就像俄罗斯套娃：打开一个，里面还有一个更小的，直到最小的那个（基线条件）。\n\n编程中：函数调用自身，每次处理更小的子问题，直到满足终止条件。\n\n例子：查字典 → 遇到不认识的词 → 再查 → 直到都认识。", tag: "编程基础", type: "flashcard", stage: 3, mastery: 55, xp: 30 },
  { id: 2, front: "「千里之行，始于足下。」", back: "—— 老子《道德经》\n\n任何伟大的成就都从第一步开始。不要因为目标遥远而畏惧，重要的是迈出第一步并持续前进。", tag: "语录", type: "quote", stage: 4, mastery: 70, xp: 40 },
  { id: 3, front: "Git rebase 和 merge 的区别？", back: "merge 创建合并提交，保留完整的分支历史（非线性）；\nrebase 将提交移到目标分支顶部，产生线性历史（更干净）。\n\n建议：公共分支用 merge 保留历史，个人分支用 rebase 保持整洁。", tag: "工具", type: "knowledge", stage: 5, mastery: 82, xp: 50 },
  { id: 4, front: "什么是 SOLID 原则？", back: "S - 单一职责：一个类只做一件事\nO - 开闭原则：对扩展开放，对修改关闭\nL - 里氏替换：子类可替换父类\nI - 接口隔离：多个专用接口优于一个大接口\nD - 依赖倒置：依赖抽象而非具体实现", tag: "设计模式", type: "knowledge", stage: 2, mastery: 35, xp: 20 },
];

const badges = [
  { icon: "🔥", name: "连续7天", desc: "连续学习7天", unlocked: true },
  { icon: "⚡", name: "速记大师", desc: "单日复习50+张", unlocked: true },
  { icon: "🏆", name: "百卡达人", desc: "掌握100张卡片", unlocked: false },
  { icon: "💎", name: "完美一天", desc: "全部「记住了」", unlocked: false },
];

export default function GamifiedFun() {
  const [view, setView] = useState("dashboard");
  const [flipped, setFlipped] = useState(false);
  const [cardIdx, setCardIdx] = useState(0);
  const [reviewed, setReviewed] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [showXp, setShowXp] = useState(false);

  const currentCard = cards[cardIdx];
  const level = 7;
  const xpTotal = 1450;
  const xpNeeded = 2000;
  const xpProgress = (xpTotal / xpNeeded) * 100;

  const handleFlip = () => setFlipped(!flipped);
  const handleFeedback = (type) => {
    setFeedback(type);
    if (type === "remembered") setShowXp(true);
    setTimeout(() => {
      setFlipped(false); setFeedback(null); setShowXp(false); setReviewed(reviewed + 1);
      if (cardIdx < cards.length - 1) setCardIdx(cardIdx + 1); else setCardIdx(0);
    }, 600);
  };

  const G = {
    bg: "#FFF8F0", panel: "#FFFFFF", text: "#3D3247", muted: "#A09CB0",
    orange: "#FF8C42", purple: "#9B72CF", green: "#5EC487", pink: "#FF6B8A",
    blue: "#5BA4E0", yellow: "#FFD166", gradStart: "#FF8C42", gradEnd: "#FF6B8A",
  };

  const navItems = [
    { id: "dashboard", label: "我的主页", emoji: "🏠" },
    { id: "review", label: "开始挑战", emoji: "⚔️" },
    { id: "manage", label: "卡片库", emoji: "📚" },
    { id: "stats", label: "成就墙", emoji: "🏅" },
  ];

  return (
    <div style={{ display: "flex", width: 960, height: 620, fontFamily: "'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif", background: G.bg, borderRadius: 20, overflow: "hidden", boxShadow: "0 8px 32px rgba(0,0,0,0.1)" }}>
      {/* Sidebar */}
      <div style={{ width: 190, background: `linear-gradient(180deg, #FFF5EB 0%, #FFF0F5 100%)`, borderRight: "1px solid #F0E8E0", display: "flex", flexDirection: "column", padding: "24px 0" }}>
        {/* Avatar area */}
        <div style={{ padding: "0 20px", marginBottom: 28, textAlign: "center" }}>
          <div style={{
            width: 56, height: 56, borderRadius: "50%", margin: "0 auto 8px",
            background: `linear-gradient(135deg, ${G.orange}, ${G.pink})`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 28, boxShadow: `0 4px 12px ${G.orange}40`,
          }}>🧠</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: G.text }}>记忆小达人</div>
          <div style={{ fontSize: 11, color: G.muted, marginTop: 2 }}>Lv.{level} · 学习中坚</div>
        </div>

        {/* XP Bar */}
        <div style={{ padding: "0 20px", marginBottom: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: G.muted, marginBottom: 4 }}>
            <span>经验值</span><span>{xpTotal}/{xpNeeded} XP</span>
          </div>
          <div style={{ width: "100%", height: 8, background: "#F0E8E0", borderRadius: 4, overflow: "hidden" }}>
            <div style={{ width: `${xpProgress}%`, height: "100%", background: `linear-gradient(90deg, ${G.orange}, ${G.pink})`, borderRadius: 4, transition: "width 0.5s" }} />
          </div>
          <div style={{ fontSize: 9, color: G.muted, marginTop: 3 }}>距 Lv.{level + 1} 还差 {xpNeeded - xpTotal} XP</div>
        </div>

        {navItems.map(item => (
          <div key={item.id} onClick={() => { setView(item.id); setFlipped(false); setCardIdx(0); setReviewed(0); }}
            style={{
              padding: "10px 20px", cursor: "pointer", display: "flex", alignItems: "center", gap: 10,
              fontSize: 13, color: view === item.id ? G.orange : G.muted,
              fontWeight: view === item.id ? 700 : 500,
              background: view === item.id ? G.orange + "12" : "transparent",
              borderRadius: view === item.id ? "0 24px 24px 0" : 0,
              marginRight: view === item.id ? 8 : 0,
            }}>
            <span style={{ fontSize: 18 }}>{item.emoji}</span>
            {item.label}
          </div>
        ))}

        <div style={{ flex: 1 }} />

        {/* Streak */}
        <div style={{ padding: "0 16px" }}>
          <div style={{
            background: `linear-gradient(135deg, ${G.orange}15, ${G.pink}15)`,
            borderRadius: 16, padding: "14px 16px", textAlign: "center"
          }}>
            <div style={{ fontSize: 28 }}>🔥</div>
            <div style={{ fontSize: 22, fontWeight: 800, color: G.orange, marginTop: 2 }}>12 天</div>
            <div style={{ fontSize: 10, color: G.muted }}>连续打卡中</div>
          </div>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, padding: "24px 28px", overflowY: "auto" }}>
        {/* Dashboard */}
        {view === "dashboard" && (
          <div>
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 22, fontWeight: 800, color: G.text }}>Hi，今天也要加油哦 ✨</div>
              <div style={{ fontSize: 13, color: G.muted, marginTop: 4 }}>完成今天的 20 张复习卡，就能获得额外 50 XP 奖励！</div>
            </div>

            {/* Today's mission */}
            <div style={{
              background: `linear-gradient(135deg, ${G.orange}, ${G.pink})`, borderRadius: 16,
              padding: "20px 24px", marginBottom: 20, color: "#FFF",
              boxShadow: `0 4px 16px ${G.orange}30`
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, opacity: 0.9 }}>今日任务</div>
                  <div style={{ fontSize: 26, fontWeight: 800, marginTop: 4 }}>复习 20 张卡片</div>
                  <div style={{ fontSize: 12, opacity: 0.85, marginTop: 4 }}>已完成 12/20 · 奖励 +50 XP</div>
                </div>
                <div style={{
                  width: 72, height: 72, borderRadius: "50%", background: "rgba(255,255,255,0.2)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  <div style={{ width: 56, height: 56, borderRadius: "50%", background: "rgba(255,255,255,0.3)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, fontWeight: 800 }}>
                    60%
                  </div>
                </div>
              </div>
            </div>

            {/* Stats row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
              {[
                { emoji: "📝", label: "已复习", value: "12 张", color: G.blue },
                { emoji: "🎯", label: "正确率", value: "90%", color: G.green },
                { emoji: "⭐", label: "今日 XP", value: "+180", color: G.orange },
              ].map((s, i) => (
                <div key={i} style={{ background: G.panel, borderRadius: 14, padding: "16px", textAlign: "center", boxShadow: "0 2px 8px rgba(0,0,0,0.04)" }}>
                  <div style={{ fontSize: 24, marginBottom: 4 }}>{s.emoji}</div>
                  <div style={{ fontSize: 22, fontWeight: 800, color: s.color }}>{s.value}</div>
                  <div style={{ fontSize: 11, color: G.muted }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* Badges */}
            <div style={{ background: G.panel, borderRadius: 14, padding: "18px 20px", boxShadow: "0 2px 8px rgba(0,0,0,0.04)" }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: G.text, marginBottom: 14 }}>最近成就</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                {badges.map((b, i) => (
                  <div key={i} style={{
                    textAlign: "center", padding: "12px 8px", borderRadius: 12,
                    background: b.unlocked ? G.yellow + "18" : "#F5F0EB",
                    opacity: b.unlocked ? 1 : 0.5,
                  }}>
                    <div style={{ fontSize: 28, filter: b.unlocked ? "none" : "grayscale(1)" }}>{b.icon}</div>
                    <div style={{ fontSize: 11, fontWeight: 700, color: G.text, marginTop: 4 }}>{b.name}</div>
                    <div style={{ fontSize: 9, color: G.muted, marginTop: 2 }}>{b.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Review */}
        {view === "review" && (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", height: "100%", position: "relative" }}>
            {/* XP popup */}
            {showXp && (
              <div style={{
                position: "absolute", top: 20, right: 40, fontSize: 24, fontWeight: 800,
                color: G.orange, animation: "none", zIndex: 10,
              }}>+{currentCard.xp} XP ⭐</div>
            )}

            <div style={{ display: "flex", gap: 16, alignItems: "center", marginBottom: 12 }}>
              <div style={{ fontSize: 13, color: G.muted }}>第 {reviewed + 1} 关 / 共 {cards.length} 关</div>
              <div style={{ padding: "3px 12px", background: G.purple + "18", borderRadius: 12, fontSize: 11, color: G.purple, fontWeight: 600 }}>
                {currentCard.tag}
              </div>
            </div>

            {/* Fun progress */}
            <div style={{ width: "100%", maxWidth: 500, marginBottom: 20, position: "relative" }}>
              <div style={{ height: 12, background: "#F0E8E0", borderRadius: 6, overflow: "hidden" }}>
                <div style={{
                  width: `${(reviewed / cards.length) * 100}%`, height: "100%",
                  background: `linear-gradient(90deg, ${G.green}, ${G.blue})`, borderRadius: 6,
                  transition: "width 0.4s"
                }} />
              </div>
              <div style={{
                position: "absolute", left: `${(reviewed / cards.length) * 100}%`, top: -4,
                transform: "translateX(-50%)", fontSize: 18, transition: "left 0.4s"
              }}>🚀</div>
            </div>

            {/* Card */}
            <div onClick={handleFlip}
              style={{
                width: "100%", maxWidth: 480, minHeight: 230,
                background: flipped
                  ? `linear-gradient(135deg, ${G.panel}, #F8F4FF)`
                  : G.panel,
                borderRadius: 20, padding: "32px 28px",
                boxShadow: flipped
                  ? `0 8px 24px ${G.purple}20`
                  : "0 4px 16px rgba(0,0,0,0.06)",
                cursor: "pointer", transition: "all 0.3s",
                border: `2px solid ${flipped ? G.purple + "30" : "transparent"}`,
                opacity: feedback ? 0.4 : 1,
              }}>
              {!flipped ? (
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 32, marginBottom: 12 }}>🤔</div>
                  <div style={{ fontSize: 10, color: G.muted, letterSpacing: 1, marginBottom: 8 }}>
                    {currentCard.type === "quote" ? "语录记忆" : currentCard.type === "knowledge" ? "知识挑战" : "记忆闯关"} · 点我翻面
                  </div>
                  <div style={{ fontSize: 17, color: G.text, lineHeight: 1.7, fontWeight: 600 }}>{currentCard.front}</div>
                </div>
              ) : (
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 32, marginBottom: 12 }}>💡</div>
                  <div style={{ fontSize: 10, color: G.purple, letterSpacing: 1, marginBottom: 8 }}>答案揭晓</div>
                  <div style={{ fontSize: 14, color: "#6B6580", lineHeight: 1.8, whiteSpace: "pre-line", textAlign: "left" }}>{currentCard.back}</div>
                </div>
              )}
            </div>

            {/* Feedback */}
            {flipped && (
              <div style={{ display: "flex", gap: 14, marginTop: 24 }}>
                {[
                  { label: "不会 😅", desc: "从头再来", color: G.pink, type: "forgot" },
                  { label: "有点印象 🤏", desc: "巩固一下", color: G.yellow, type: "fuzzy" },
                  { label: "记住了！💪", desc: `+${currentCard.xp} XP`, color: G.green, type: "remembered" },
                ].map(btn => (
                  <div key={btn.type} onClick={() => handleFeedback(btn.type)}
                    style={{
                      padding: "14px 22px", borderRadius: 16, cursor: "pointer", textAlign: "center",
                      background: btn.color + "15", border: `2px solid ${btn.color}30`,
                      minWidth: 120, transition: "transform 0.15s",
                    }}>
                    <div style={{ fontSize: 14, fontWeight: 700, color: btn.color }}>{btn.label}</div>
                    <div style={{ fontSize: 10, color: G.muted, marginTop: 3 }}>{btn.desc}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Manage */}
        {view === "manage" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div style={{ fontSize: 18, fontWeight: 800, color: G.text }}>📚 我的卡片库</div>
              <div style={{
                padding: "8px 18px", background: `linear-gradient(135deg, ${G.orange}, ${G.pink})`,
                color: "#FFF", borderRadius: 20, fontSize: 12, cursor: "pointer", fontWeight: 700,
                boxShadow: `0 2px 8px ${G.orange}30`,
              }}>+ 创建新卡片</div>
            </div>

            {/* Filter pills */}
            <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
              {[{ l: "全部", e: "📋" }, { l: "记忆卡", e: "🎴" }, { l: "知识点", e: "📝" }, { l: "语录", e: "💬" }].map((t, i) => (
                <div key={i} style={{
                  padding: "6px 14px", borderRadius: 20, fontSize: 12, cursor: "pointer",
                  background: i === 0 ? G.orange + "18" : G.panel,
                  color: i === 0 ? G.orange : G.muted,
                  border: `1.5px solid ${i === 0 ? G.orange + "40" : "#F0E8E0"}`,
                  fontWeight: i === 0 ? 600 : 400,
                }}>{t.e} {t.l}</div>
              ))}
            </div>

            {cards.map((c, i) => (
              <div key={i} style={{
                background: G.panel, borderRadius: 14, padding: "16px 20px", marginBottom: 10,
                boxShadow: "0 2px 8px rgba(0,0,0,0.03)", display: "flex", alignItems: "center", gap: 14,
                borderLeft: `4px solid ${c.mastery > 70 ? G.green : c.mastery > 40 ? G.yellow : G.pink}`,
              }}>
                <div style={{ fontSize: 24 }}>
                  {c.type === "quote" ? "💬" : c.type === "knowledge" ? "📝" : "🎴"}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, color: G.text, lineHeight: 1.5, fontWeight: 500 }}>{c.front}</div>
                  <div style={{ display: "flex", gap: 8, marginTop: 6, alignItems: "center" }}>
                    <span style={{ padding: "2px 8px", background: G.purple + "15", borderRadius: 8, fontSize: 10, color: G.purple }}>{c.tag}</span>
                    <span style={{ fontSize: 10, color: G.muted }}>阶段 {c.stage}</span>
                    <span style={{ fontSize: 10, color: G.orange }}>+{c.xp} XP</span>
                  </div>
                </div>
                <div style={{ textAlign: "center" }}>
                  <div style={{
                    width: 44, height: 44, borderRadius: "50%",
                    background: `conic-gradient(${c.mastery > 70 ? G.green : c.mastery > 40 ? G.yellow : G.pink} ${c.mastery * 3.6}deg, #F0E8E0 0deg)`,
                    display: "flex", alignItems: "center", justifyContent: "center"
                  }}>
                    <div style={{ width: 34, height: 34, borderRadius: "50%", background: G.panel, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: G.text }}>
                      {c.mastery}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Stats / Achievements */}
        {view === "stats" && (
          <div>
            <div style={{ fontSize: 18, fontWeight: 800, color: G.text, marginBottom: 20 }}>🏅 成就墙</div>

            {/* Level card */}
            <div style={{
              background: `linear-gradient(135deg, ${G.purple}20, ${G.blue}20)`, borderRadius: 16,
              padding: "20px 24px", marginBottom: 18, display: "flex", alignItems: "center", gap: 20
            }}>
              <div style={{
                width: 72, height: 72, borderRadius: "50%",
                background: `linear-gradient(135deg, ${G.orange}, ${G.pink})`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 28, fontWeight: 800, color: "#FFF",
                boxShadow: `0 4px 12px ${G.orange}30`,
              }}>
                {level}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 16, fontWeight: 700, color: G.text }}>学习中坚</div>
                <div style={{ fontSize: 12, color: G.muted, marginTop: 2 }}>累计获得 {xpTotal} 经验值</div>
                <div style={{ width: "100%", height: 8, background: "#E8E0D8", borderRadius: 4, marginTop: 8 }}>
                  <div style={{ width: `${xpProgress}%`, height: "100%", background: `linear-gradient(90deg, ${G.orange}, ${G.pink})`, borderRadius: 4 }} />
                </div>
                <div style={{ fontSize: 10, color: G.muted, marginTop: 3 }}>还需 {xpNeeded - xpTotal} XP 升至 Lv.{level + 1}</div>
              </div>
            </div>

            {/* Weekly chart */}
            <div style={{ background: G.panel, borderRadius: 16, padding: "18px 20px", marginBottom: 16, boxShadow: "0 2px 8px rgba(0,0,0,0.04)" }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: G.text, marginBottom: 14 }}>本周学习能量</div>
              <ResponsiveContainer width="100%" height={130}>
                <BarChart data={weekData}>
                  <XAxis dataKey="day" tick={{ fontSize: 11, fill: G.muted }} axisLine={false} tickLine={false} />
                  <YAxis hide />
                  <Tooltip contentStyle={{ borderRadius: 10, border: "none", boxShadow: "0 2px 8px rgba(0,0,0,0.1)", fontSize: 11 }} />
                  <Bar dataKey="xp" fill={G.orange} radius={[8, 8, 0, 0]} name="XP" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* All badges */}
            <div style={{ background: G.panel, borderRadius: 16, padding: "18px 20px", boxShadow: "0 2px 8px rgba(0,0,0,0.04)" }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: G.text, marginBottom: 14 }}>全部成就</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                {[...badges, { icon: "🌟", name: "初学者", desc: "完成首次复习", unlocked: true },
                  { icon: "📖", name: "博览群书", desc: "创建50张卡片", unlocked: true },
                  { icon: "🎯", name: "神射手", desc: "连续5天正确率>90%", unlocked: false },
                  { icon: "👑", name: "记忆王者", desc: "连续30天打卡", unlocked: false },
                ].map((b, i) => (
                  <div key={i} style={{
                    textAlign: "center", padding: "14px 8px", borderRadius: 14,
                    background: b.unlocked ? `linear-gradient(135deg, ${G.yellow}15, ${G.orange}10)` : "#F8F4F0",
                    opacity: b.unlocked ? 1 : 0.45,
                    border: b.unlocked ? `1.5px solid ${G.yellow}40` : "1.5px solid transparent",
                  }}>
                    <div style={{ fontSize: 30, filter: b.unlocked ? "none" : "grayscale(1)" }}>{b.icon}</div>
                    <div style={{ fontSize: 11, fontWeight: 700, color: G.text, marginTop: 6 }}>{b.name}</div>
                    <div style={{ fontSize: 9, color: G.muted, marginTop: 2 }}>{b.desc}</div>
                    {b.unlocked && <div style={{ fontSize: 9, color: G.green, marginTop: 4, fontWeight: 600 }}>✓ 已解锁</div>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}