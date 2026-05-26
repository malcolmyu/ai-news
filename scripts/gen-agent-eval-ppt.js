const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// ── Icons ────────────────────────────────────────────────────────────────
const { FaRobot, FaBalanceScale, FaCode, FaUserCheck, FaUserSecret, FaDocker,
  FaLightbulb, FaChartBar, FaSearch, FaShieldAlt, FaFlask, FaGlobe,
  FaCheckCircle, FaTimesCircle, FaStar, FaArrowRight, FaGithub,
  FaBookOpen, FaBullseye } = require("react-icons/fa");

function renderIconSvg(Icon, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(Icon, { color, size: String(size) })
  );
}

async function iconToBase64Png(Icon, color, size = 256) {
  const svg = renderIconSvg(Icon, color, size);
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

// ── Preset ───────────────────────────────────────────────────────────────
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "AI News Research";
pres.title = "Agent 评测平台深度对比";

// ── Colors ───────────────────────────────────────────────────────────────
const C = {
  bg:       "0F0F1A",
  card:     "1A1A2E",
  cardAlt:  "222244",
  accent:   "5E6AD2",
  accentL:  "7C83FF",
  white:    "FFFFFF",
  gray:     "8B8FA3",
  grayL:    "B0B3C5",
  green:    "34D399",
  orange:   "F59E0B",
  red:      "EF4444",
  teal:     "14B8A6",
  pink:     "EC4899",
};

const FONT_TITLE = "Arial Black";
const FONT_BODY = "Arial";

// ── Helpers ──────────────────────────────────────────────────────────────
function titleSlide(title, subtitle, iconData) {
  const s = pres.addSlide();
  s.background = { color: C.bg };

  // Top accent bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent }
  });

  // Icon circle
  if (iconData) {
    s.addShape(pres.shapes.OVAL, {
      x: 4.4, y: 1.2, w: 1.2, h: 1.2,
      fill: { color: C.accent, transparency: 15 }
    });
    s.addImage({ data: iconData, x: 4.55, y: 1.35, w: 0.9, h: 0.9 });
  }

  // Title
  s.addText(title, {
    x: 1, y: 2.7, w: 8, h: 1,
    fontSize: 36, fontFace: FONT_TITLE, color: C.white,
    align: "center", bold: true, margin: 0
  });

  // Subtitle
  if (subtitle) {
    s.addText(subtitle, {
      x: 1.5, y: 3.6, w: 7, h: 0.6,
      fontSize: 15, fontFace: FONT_BODY, color: C.grayL,
      align: "center", margin: 0
    });
  }

  // Bottom accent bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.565, w: 10, h: 0.06, fill: { color: C.accent }
  });
  return s;
}

function sectionSlide(title, subtitle, iconData) {
  const s = pres.addSlide();
  s.background = { color: C.bg };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent }
  });

  if (iconData) {
    s.addShape(pres.shapes.OVAL, {
      x: 4.4, y: 1.6, w: 1.0, h: 1.0,
      fill: { color: C.accent, transparency: 15 }
    });
    s.addImage({ data: iconData, x: 4.55, y: 1.75, w: 0.7, h: 0.7 });
  }

  s.addText(title, {
    x: 1, y: 2.9, w: 8, h: 0.8,
    fontSize: 32, fontFace: FONT_TITLE, color: C.white,
    align: "center", bold: true, margin: 0
  });

  if (subtitle) {
    s.addText(subtitle, {
      x: 1.5, y: 3.7, w: 7, h: 0.5,
      fontSize: 14, fontFace: FONT_BODY, color: C.grayL,
      align: "center", margin: 0
    });
  }
  return s;
}

function addStatCard(slide, x, y, num, label, color) {
  slide.addText(num, {
    x, y, w: 2.2, h: 0.7,
    fontSize: 36, fontFace: FONT_TITLE, color: color || C.accent,
    align: "center", bold: true, margin: 0
  });
  slide.addText(label, {
    x, y: y + 0.7, w: 2.2, h: 0.4,
    fontSize: 11, fontFace: FONT_BODY, color: C.gray,
    align: "center", margin: 0
  });
}

function addParadigmCard(slide, x, y, emoji, title, desc, platforms, color) {
  const c = color || C.accent;
  // Card bg
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 4.5, h: 1.6,
    fill: { color: C.card }
  });
  // Left accent
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.06, h: 1.6, fill: { color: c }
  });
  // Emoji
  slide.addText(emoji, {
    x: x + 0.2, y: y + 0.1, w: 0.5, h: 0.5,
    fontSize: 22, align: "center", margin: 0
  });
  // Title
  slide.addText(title, {
    x: x + 0.75, y: y + 0.1, w: 3.5, h: 0.4,
    fontSize: 13, fontFace: FONT_TITLE, color: c, bold: true, margin: 0
  });
  // Description
  slide.addText(desc, {
    x: x + 0.2, y: y + 0.55, w: 4.1, h: 0.6,
    fontSize: 10, fontFace: FONT_BODY, color: C.grayL, margin: 0
  });
  // Platforms
  slide.addText(platforms, {
    x: x + 0.2, y: y + 1.15, w: 4.1, h: 0.35,
    fontSize: 9, fontFace: FONT_BODY, color: C.gray, italic: true, margin: 0
  });
}

function addGapCard(slide, x, y, num, title, desc, market, difficulty) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 8.6, h: 0.88,
    fill: { color: C.card }
  });
  // Number
  slide.addText(num, {
    x: x + 0.15, y: y + 0.1, w: 0.4, h: 0.4,
    fontSize: 22, fontFace: FONT_TITLE, color: C.accent, bold: true,
    align: "center", margin: 0
  });
  // Title
  slide.addText(title, {
    x: x + 0.65, y: y + 0.08, w: 5, h: 0.35,
    fontSize: 12, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });
  // Description
  slide.addText(desc, {
    x: x + 0.65, y: y + 0.42, w: 5, h: 0.4,
    fontSize: 9.5, fontFace: FONT_BODY, color: C.grayL, margin: 0
  });
  // Market badges
  const mColor = market === "高" ? C.red : market === "中" ? C.orange : C.green;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x + 6.7, y: y + 0.15, w: 0.8, h: 0.25,
    fill: { color: mColor, transparency: 70 }
  });
  slide.addText("潜力" + market, {
    x: x + 6.7, y: y + 0.15, w: 0.8, h: 0.25,
    fontSize: 8, fontFace: FONT_BODY, color: mColor, align: "center", margin: 0
  });
  const dColor = difficulty === "高" ? C.red : difficulty === "中" ? C.orange : C.green;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x + 7.6, y: y + 0.15, w: 0.8, h: 0.25,
    fill: { color: dColor, transparency: 70 }
  });
  slide.addText("难度" + difficulty, {
    x: x + 7.6, y: y + 0.15, w: 0.8, h: 0.25,
    fontSize: 8, fontFace: FONT_BODY, color: dColor, align: "center", margin: 0
  });
}

// ────────────────────────────────────────────────────────────────────────
// MAIN
// ────────────────────────────────────────────────────────────────────────

(async () => {

// Pre-render icons
const icons = {
  robot: await iconToBase64Png(FaRobot, "#FFFFFF"),
  brain: await iconToBase64Png(FaLightbulb, "#FFFFFF"),
  chart: await iconToBase64Png(FaChartBar, "#FFFFFF"),
  search: await iconToBase64Png(FaSearch, "#FFFFFF"),
  shield: await iconToBase64Png(FaShieldAlt, "#FFFFFF"),
  flask: await iconToBase64Png(FaFlask, "#FFFFFF"),
  bullseye: await iconToBase64Png(FaBullseye, "#FFFFFF"),
  check: await iconToBase64Png(FaCheckCircle, "#34D399"),
  cross: await iconToBase64Png(FaTimesCircle, "#EF4444"),
  star: await iconToBase64Png(FaStar, "#F59E0B"),
  book: await iconToBase64Png(FaBookOpen, "#FFFFFF"),
};

// ════════════════════════════════════════════════════════════════════════
// SLIDE 1 — Cover
// ════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.565, w: 10, h: 0.06, fill: { color: C.accent } });

  // Decorative circle
  s.addShape(pres.shapes.OVAL, {
    x: 3.9, y: 1.0, w: 2.2, h: 2.2,
    fill: { color: C.accent, transparency: 10 }
  });
  s.addImage({ data: icons.robot, x: 4.25, y: 1.35, w: 1.5, h: 1.5 });

  s.addText("Agent 评测平台深度对比", {
    x: 0.5, y: 3.5, w: 9, h: 0.9,
    fontSize: 34, fontFace: FONT_TITLE, color: C.white, bold: true,
    align: "center", margin: 0
  });

  s.addText("9 平台 × 5 范式 · 横向对比、场景选型、空白地带与市场格局", {
    x: 1, y: 4.3, w: 8, h: 0.5,
    fontSize: 14, fontFace: FONT_BODY, color: C.grayL, align: "center", margin: 0
  });

  s.addText("AI News Research · 2026/05/22", {
    x: 1, y: 4.8, w: 8, h: 0.4,
    fontSize: 11, fontFace: FONT_BODY, color: C.gray, align: "center", margin: 0
  });
}

// ════════════════════════════════════════════════════════════════════════
// SLIDE 2 — Overview Stats
// ════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  s.addText("全景概览", {
    x: 0.5, y: 0.3, w: 9, h: 0.6,
    fontSize: 26, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });

  // Stats
  addStatCard(s, 0.5, 1.3, "9", "活跃评测平台", C.accent);
  addStatCard(s, 2.9, 1.3, "5", "评测范式分类", C.teal);
  addStatCard(s, 5.3, 1.3, "5", "关键空白地带", C.orange);
  addStatCard(s, 7.7, 1.3, "9", "场景选型推荐", C.pink);

  // Tag cloud
  const tags = [
    "LLM-as-Judge", "Code-based Eval", "Human Eval",
    "Agent-as-Judge", "Sandbox Eval", "OTel 可观测",
    "CI/CD 集成", "幻觉检测", "仿真测试"
  ];
  let tx = 0.5, ty = 2.6;
  const makeTagBg = () => ({ color: C.card });
  tags.forEach((tag, i) => {
    const w = tag.length * 0.15 + 0.3;
    if (tx + w > 9.5) { tx = 0.5; ty += 0.5; }
    s.addShape(pres.shapes.RECTANGLE, {
      x: tx, y: ty, w, h: 0.35,
      fill: makeTagBg()
    });
    s.addText(tag, {
      x: tx, y: ty, w, h: 0.35,
      fontSize: 10, fontFace: FONT_BODY, color: C.grayL,
      align: "center", margin: 0
    });
    tx += w + 0.15;
  });

  // Coverage stat
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.8, w: 9, h: 1.3,
    fill: { color: C.card }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.8, w: 0.06, h: 1.3, fill: { color: C.accent }
  });

  s.addText("覆盖率", {
    x: 0.8, y: 3.95, w: 2, h: 0.35,
    fontSize: 13, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });

  // Progress bars
  const bars = [
    { label: "LLM-as-Judge", pct: 100, color: C.green },
    { label: "Code-based", pct: 89, color: C.teal },
    { label: "Human Eval", pct: 100, color: C.accent },
    { label: "Agent-as-Judge", pct: 33, color: C.orange },
    { label: "Sandbox", pct: 11, color: C.red },
  ];
  bars.forEach((b, i) => {
    const by = 4.35 + i * 0.16;
    s.addText(b.label, {
      x: 0.8, y: by, w: 1.8, h: 0.15,
      fontSize: 9, fontFace: FONT_BODY, color: C.grayL, margin: 0
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 2.65, y: by + 0.02, w: 5.5, h: 0.1,
      fill: { color: C.cardAlt }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 2.65, y: by + 0.02, w: 5.5 * b.pct / 100, h: 0.1,
      fill: { color: b.color }
    });
    s.addText(b.pct + "%", {
      x: 8.3, y: by, w: 0.8, h: 0.15,
      fontSize: 9, fontFace: FONT_BODY, color: b.color, bold: true, margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════════════
// SLIDE 3 — Five Paradigms
// ════════════════════════════════════════════════════════════════════════
{
  const s = sectionSlide("五大评测范式", "评判主体与自动化程度", icons.brain);

  const paradigms = [
    {
      emoji: "🤖", title: "LLM-as-Judge",
      desc: "用另一个 LLM 对输出打分。核心问题：偏见（Position/Verbosity/Self-enhancement）和推理成本。",
      platforms: "DeepEval G-Eval · Galileo Luna-2 · Braintrust Loop AI · LangSmith Polly AI",
      color: C.accent
    },
    {
      emoji: "⚙️", title: "Code-based / Deterministic",
      desc: "通过代码规则（正则匹配、JSON Schema、DAG 流程）进行确定性评判。零随机性、零 API 成本。",
      platforms: "DeepEval DAG · Braintrust Scorer · LangSmith 自定义",
      color: C.teal
    },
    {
      emoji: "👤", title: "Human Eval（人工评测）",
      desc: "人类专家判定。精度最高但成本最高、扩展性最差。所有平台都支持，但深度差异大。",
      platforms: "Braintrust 人工队列 · Galileo Enterprise · Langfuse 标注队列",
      color: C.green
    },
    {
      emoji: "🕵️", title: "Agent-as-Judge（最大空白）",
      desc: "专用 Agent 评估全链路行为（规划、工具调用、中间决策）。6/9 平台完全缺失。",
      platforms: "Braintrust Loop AI（唯一完整）· DeepEval（部分）",
      color: C.orange
    },
    {
      emoji: "🔒", title: "Sandbox Eval（LangSmith 护城河）",
      desc: "在隔离环境中执行 Agent 操作并评估结果。LangSmith 唯一提供完整 Docker 沙箱。",
      platforms: "LangSmith Sandbox（唯一）· Maxim 仿真引擎（近似）",
      color: C.pink
    },
  ];

  // 5 cards in a 3+2 layout: top row 3, bottom row 2
  const top3 = paradigms.slice(0, 3);
  const bot2 = paradigms.slice(3, 5);

  top3.forEach((p, i) => {
    addParadigmCard(s, 0.3 + i * 3.2, 0.9, p.emoji, p.title, p.desc, p.platforms, p.color);
  });

  bot2.forEach((p, i) => {
    addParadigmCard(s, 1.7 + i * 3.2, 2.7, p.emoji, p.title, p.desc, p.platforms, p.color);
  });

  // Key finding banner
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.3, y: 4.55, w: 9.4, h: 0.7,
    fill: { color: C.card }
  });
  s.addText("🔍 关键发现：无平台覆盖全部 5 范式。Braintrust 和 DeepEval 最完整（4/5），均缺 Sandbox。Agent-as-Judge 是最大空白（67% 平台缺失）。", {
    x: 0.5, y: 4.6, w: 9, h: 0.55,
    fontSize: 10.5, fontFace: FONT_BODY, color: C.orange, margin: 0
  });
}

// ════════════════════════════════════════════════════════════════════════
// SLIDE 4 — Paradigm Coverage Matrix (Table)
// ════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  s.addText("范式覆盖矩阵——9 平台 × 5 范式", {
    x: 0.3, y: 0.2, w: 9.4, h: 0.5,
    fontSize: 18, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });

  const hdrOpts = { fill: { color: C.cardAlt }, color: C.white, bold: true, fontSize: 9, fontFace: FONT_BODY, align: "center", valign: "middle" };
  const cellOpts = (color) => ({ fill: { color: C.card }, color: color, fontSize: 8.5, fontFace: FONT_BODY, align: "center", valign: "middle" });
  const starOpts = { fill: { color: C.card }, color: C.orange, fontSize: 8.5, fontFace: FONT_BODY, align: "center", valign: "middle", bold: true };

  const rows = [
    [
      { text: "平台", options: hdrOpts },
      { text: "LLM-as-Judge", options: hdrOpts },
      { text: "Code-based", options: hdrOpts },
      { text: "Human Eval", options: hdrOpts },
      { text: "Agent-as-Judge", options: hdrOpts },
      { text: "Sandbox", options: hdrOpts },
      { text: "覆盖", options: hdrOpts },
    ],
    [
      { text: "W&B Weave", options: cellOpts(C.grayL) },
      { text: "⭐ 基础", options: cellOpts(C.grayL) },
      { text: "⭐ 基础", options: cellOpts(C.grayL) },
      { text: "⭐ 基础", options: cellOpts(C.grayL) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "3/5", options: cellOpts(C.grayL) },
    ],
    [
      { text: "Braintrust", options: cellOpts(C.accentL) },
      { text: "⭐⭐⭐ Loop AI", options: cellOpts(C.green) },
      { text: "⭐⭐ 自定义", options: cellOpts(C.teal) },
      { text: "⭐⭐ 队列", options: cellOpts(C.green) },
      { text: "⭐⭐⭐ 闭环", options: cellOpts(C.green) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "4/5 ★", options: starOpts },
    ],
    [
      { text: "Arize Phoenix", options: cellOpts(C.grayL) },
      { text: "⭐⭐ 多维", options: cellOpts(C.grayL) },
      { text: "⭐ 自定义", options: cellOpts(C.grayL) },
      { text: "⭐ 标注", options: cellOpts(C.grayL) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "3/5", options: cellOpts(C.grayL) },
    ],
    [
      { text: "LangSmith", options: cellOpts(C.accentL) },
      { text: "⭐⭐ Polly AI", options: cellOpts(C.grayL) },
      { text: "⭐⭐ 自定义", options: cellOpts(C.teal) },
      { text: "⭐⭐ 标注", options: cellOpts(C.green) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "⭐⭐⭐ 唯一沙箱", options: cellOpts(C.pink) },
      { text: "4/5 ★", options: starOpts },
    ],
    [
      { text: "Comet Opik", options: cellOpts(C.grayL) },
      { text: "⭐⭐ Judge", options: cellOpts(C.grayL) },
      { text: "⭐⭐ ROUGE/BLEU", options: cellOpts(C.teal) },
      { text: "⭐ UI 标注", options: cellOpts(C.grayL) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "3/5", options: cellOpts(C.grayL) },
    ],
    [
      { text: "DeepEval", options: cellOpts(C.accentL) },
      { text: "⭐⭐⭐ 40+ 指标", options: cellOpts(C.green) },
      { text: "⭐⭐⭐ DAG 管道", options: cellOpts(C.green) },
      { text: "⭐ CA 平台", options: cellOpts(C.grayL) },
      { text: "⭐⭐ TaskComp", options: cellOpts(C.orange) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "4/5 ★", options: starOpts },
    ],
    [
      { text: "Maxim AI", options: cellOpts(C.grayL) },
      { text: "⭐⭐ 预构建", options: cellOpts(C.grayL) },
      { text: "⭐ 自定义", options: cellOpts(C.grayL) },
      { text: "⭐⭐ 队列", options: cellOpts(C.green) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "3/5", options: cellOpts(C.grayL) },
    ],
    [
      { text: "Langfuse", options: cellOpts(C.grayL) },
      { text: "⭐⭐ 内置", options: cellOpts(C.grayL) },
      { text: "⭐⭐ Python", options: cellOpts(C.teal) },
      { text: "⭐⭐ UI 队列", options: cellOpts(C.green) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "3/5", options: cellOpts(C.grayL) },
    ],
    [
      { text: "Galileo", options: cellOpts(C.accentL) },
      { text: "⭐⭐⭐ Luna-2", options: cellOpts(C.green) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "⭐ Enterprise", options: cellOpts(C.grayL) },
      { text: "⭐⭐ Insights", options: cellOpts(C.orange) },
      { text: "✗", options: cellOpts(C.red) },
      { text: "3/5", options: cellOpts(C.grayL) },
    ],
  ];

  s.addTable(rows, {
    x: 0.3, y: 0.85, w: 9.4,
    colW: [1.5, 1.5, 1.3, 1.2, 1.5, 1.5, 0.9],
    rowH: [0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35, 0.35],
    border: { pt: 0.5, color: "2A2A4A" },
  });

  // Legend
  s.addText("⭐ 深入  ⭐⭐ 标准  ⭐ 基础  ✗ 不支持  ★ 最完整平台", {
    x: 0.3, y: 4.65, w: 9.4, h: 0.3,
    fontSize: 9, fontFace: FONT_BODY, color: C.gray, align: "center", margin: 0
  });

  // 5 key findings below
  const findings = [
    "① 无平台覆盖全部 5 范式",
    "② Agent-as-Judge 6/9 缺失",
    "③ Sandbox 是 LangSmith 独有护城河",
    "④ Galileo 走专有模型差异化路线",
    "⑤ 开源阵营：通用可观测 vs 评估专精"
  ];
  findings.forEach((f, i) => {
    s.addText(f, {
      x: 0.3 + (i % 3) * 3.15, y: 5.05 + Math.floor(i/3) * 0.28, w: 3, h: 0.25,
      fontSize: 9, fontFace: FONT_BODY, color: C.orange, margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════════════
// SLIDE 5 — Data Comparison Table
// ════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  s.addText("平台横向对比——开源·定价·核心差异化", {
    x: 0.3, y: 0.2, w: 9.4, h: 0.5,
    fontSize: 18, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });

  const hdrOpts = { fill: { color: C.cardAlt }, color: C.white, bold: true, fontSize: 8.5, fontFace: FONT_BODY, align: "center", valign: "middle" };
  const cellOpts = (color) => ({ fill: { color: C.card }, color: color || C.grayL, fontSize: 8, fontFace: FONT_BODY, align: "center", valign: "middle" });

  const rows = [
    [
      { text: "平台", options: hdrOpts },
      { text: "开源", options: hdrOpts },
      { text: "许可", options: hdrOpts },
      { text: "自托管", options: hdrOpts },
      { text: "免费层", options: hdrOpts },
      { text: "SaaS 起价", options: hdrOpts },
      { text: "核心差异化", options: hdrOpts },
    ],
    [
      { text: "W&B Weave", options: cellOpts() },
      { text: "❌", options: cellOpts(C.red) },
      { text: "闭源", options: cellOpts() },
      { text: "Enterprise", options: cellOpts() },
      { text: "100GB 免费", options: cellOpts(C.green) },
      { text: "~$50/用户/月", options: cellOpts() },
      { text: "传统 ML → LLM 延伸", options: cellOpts() },
    ],
    [
      { text: "Braintrust", options: cellOpts(C.accentL) },
      { text: "❌", options: cellOpts(C.red) },
      { text: "闭源", options: cellOpts() },
      { text: "Enterprise", options: cellOpts() },
      { text: "1GB + 10k scores", options: cellOpts() },
      { text: "$249/月", options: cellOpts(C.orange) },
      { text: "★★★★ 唯一完整 Agent-as-Judge", options: cellOpts(C.green) },
    ],
    [
      { text: "Arize Phoenix", options: cellOpts(C.accentL) },
      { text: "✅", options: cellOpts(C.green) },
      { text: "Apache 2.0", options: cellOpts(C.green) },
      { text: "✅ Phoenix 免费", options: cellOpts(C.green) },
      { text: "完全免费", options: cellOpts(C.green) },
      { text: "AX 按量计", options: cellOpts() },
      { text: "OTel 可观测 + Drift/Embedding", options: cellOpts() },
    ],
    [
      { text: "LangSmith", options: cellOpts(C.accentL) },
      { text: "❌", options: cellOpts(C.red) },
      { text: "闭源", options: cellOpts() },
      { text: "Enterprise", options: cellOpts() },
      { text: "开发者免费", options: cellOpts(C.green) },
      { text: "~$99/月", options: cellOpts() },
      { text: "★★★★ 唯一 Docker 沙箱", options: cellOpts(C.pink) },
    ],
    [
      { text: "Comet Opik", options: cellOpts(C.accentL) },
      { text: "✅", options: cellOpts(C.green) },
      { text: "Apache 2.0", options: cellOpts(C.green) },
      { text: "✅ Docker/K8s", options: cellOpts(C.green) },
      { text: "10M traces/月", options: cellOpts(C.green) },
      { text: "~$999/月", options: cellOpts(C.red) },
      { text: "开源高吞吐 (40M trace/day)", options: cellOpts() },
    ],
    [
      { text: "DeepEval", options: cellOpts(C.accentL) },
      { text: "✅", options: cellOpts(C.green) },
      { text: "Apache 2.0", options: cellOpts(C.green) },
      { text: "✅ DE 免费", options: cellOpts(C.green) },
      { text: "DE 免费", options: cellOpts(C.green) },
      { text: "~$299/月 (CA)", options: cellOpts(C.orange) },
      { text: "★★★★ 评估即代码 40+ 指标", options: cellOpts(C.green) },
    ],
    [
      { text: "Maxim AI", options: cellOpts(C.accentL) },
      { text: "❌", options: cellOpts(C.red) },
      { text: "闭源", options: cellOpts() },
      { text: "In-VPC", options: cellOpts() },
      { text: "免费入门", options: cellOpts(C.green) },
      { text: "按座位/用量", options: cellOpts() },
      { text: "★★★★ 唯一 Simulation 引擎", options: cellOpts(C.green) },
    ],
    [
      { text: "Langfuse", options: cellOpts(C.accentL) },
      { text: "✅", options: cellOpts(C.green) },
      { text: "MIT/EE", options: cellOpts(C.green) },
      { text: "✅ 完全免费", options: cellOpts(C.green) },
      { text: "有限免费", options: cellOpts(C.green) },
      { text: "~$59/月", options: cellOpts(C.green) },
      { text: "极致性价比", options: cellOpts() },
    ],
    [
      { text: "Galileo", options: cellOpts(C.accentL) },
      { text: "❌", options: cellOpts(C.red) },
      { text: "闭源", options: cellOpts() },
      { text: "Enterprise", options: cellOpts() },
      { text: "有限免费", options: cellOpts() },
      { text: "按 token 计费", options: cellOpts() },
      { text: "Luna-2 专有 SLM + Protect", options: cellOpts(C.green) },
    ],
  ];

  s.addTable(rows, {
    x: 0.3, y: 0.85, w: 9.4,
    colW: [1.2, 0.6, 1.1, 1.2, 1.3, 1.3, 2.7],
    rowH: 0.38,
    border: { pt: 0.5, color: "2A2A4A" },
  });

  // Bottom insight
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.3, y: 4.85, w: 9.4, h: 0.55,
    fill: { color: C.card }
  });
  s.addText("开源阵营：Arize Phoenix · Comet Opik · DeepEval · Langfuse（Apache 2.0 / MIT）  |  闭源阵营各有不可替代的独特范式深度", {
    x: 0.5, y: 4.9, w: 9, h: 0.45,
    fontSize: 10, fontFace: FONT_BODY, color: C.grayL, margin: 0
  });
}

// ════════════════════════════════════════════════════════════════════════
// SLIDE 6 — Scenario Recommendations (Part 1)
// ════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  s.addText("场景选型推荐（1/2）", {
    x: 0.3, y: 0.2, w: 9.4, h: 0.5,
    fontSize: 18, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });

  const scenarios = [
    {
      emoji: "🐍", title: "Python CI/CD + 大量指标",
      pick: "DeepEval", alt: "Braintrust",
      reason: "40+ 预构建指标 + DAG 管道 + Pytest 风格天然适配 CI/CD。Apache 2.0 开源零成本集成。"
    },
    {
      emoji: "🔗", title: "LangChain 重度用户",
      pick: "LangSmith", alt: "Braintrust",
      reason: "原生 LangChain/LangGraph 集成 + 步骤级评分 + 唯一 Docker 沙箱。Agent-as-Judge 需 Braintrust 补充。"
    },
    {
      emoji: "🏠", title: "自托管 + 数据主权 + 免费",
      pick: "Langfuse", alt: "Comet Opik",
      reason: "MIT 开源，自托管完全免费，SaaS 仅 $59/月。OTel 原生 + Trace/评估/成本追踪四合一。"
    },
    {
      emoji: "🔄", title: "CI/CD 闭环 + 高产出团队",
      pick: "Braintrust", alt: "—",
      reason: "唯一完整 Agent-as-Judge（Loop AI）。自动从生产 trace 生成测试集→评估→分析→修复闭环。$249/月。"
    },
  ];

  scenarios.forEach((sc, i) => {
    const y = 0.85 + i * 1.15;
    // Card bg
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.3, y, w: 9.4, h: 1.0,
      fill: { color: C.card }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.3, y, w: 0.06, h: 1.0, fill: { color: C.accent }
    });

    s.addText(sc.emoji, {
      x: 0.55, y: y + 0.1, w: 0.4, h: 0.4,
      fontSize: 18, margin: 0
    });
    s.addText(sc.title, {
      x: 1.0, y: y + 0.12, w: 2.5, h: 0.35,
      fontSize: 12, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
    });

    // Pick badge
    s.addShape(pres.shapes.RECTANGLE, {
      x: 3.6, y: y + 0.15, w: 1.2, h: 0.3,
      fill: { color: C.accent, transparency: 60 }
    });
    s.addText("首选 " + sc.pick, {
      x: 3.6, y: y + 0.15, w: 1.2, h: 0.3,
      fontSize: 9, fontFace: FONT_BODY, color: C.white, align: "center", margin: 0
    });

    if (sc.alt !== "—") {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 4.95, y: y + 0.15, w: 1.0, h: 0.3,
        fill: { color: C.cardAlt }
      });
      s.addText("备选 " + sc.alt, {
        x: 4.95, y: y + 0.15, w: 1.0, h: 0.3,
        fontSize: 9, fontFace: FONT_BODY, color: C.grayL, align: "center", margin: 0
      });
    }

    s.addText(sc.reason, {
      x: 0.55, y: y + 0.55, w: 8.9, h: 0.4,
      fontSize: 9.5, fontFace: FONT_BODY, color: C.grayL, margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════════════
// SLIDE 7 — Scenario Recommendations (Part 2)
// ════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  s.addText("场景选型推荐（2/2）", {
    x: 0.3, y: 0.2, w: 9.4, h: 0.5,
    fontSize: 18, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });

  const scenarios = [
    {
      emoji: "🛡️", title: "幻觉检测 + 生产安全",
      pick: "Galileo", alt: "—",
      reason: "Luna-2 蒸馏 SLM（$0.02/1M tokens, 152ms 延迟）+ Galileo Protect 运行时拦截。Code-based 空白。"
    },
    {
      emoji: "🎭", title: "AI Agent 仿真测试",
      pick: "Maxim AI", alt: "—",
      reason: "唯一 Simulation 引擎，在安全环境模拟 Agent 行为后再投产。In-VPC 部署满足数据敏感场景。"
    },
    {
      emoji: "📊", title: "已有 W&B 基础设施",
      pick: "W&B Weave", alt: "—",
      reason: "传统 ML + LLM 统一管理。基础三范式覆盖。适合「够用就好」，迁移成本最低。"
    },
    {
      emoji: "📈", title: "OTel 生态 + Embedding/Drift",
      pick: "Arize Phoenix", alt: "—",
      reason: "OTel 原生 ML 可观测。Embedding 分析 + Drift 检测全市场最强。Phoenix 开源免费。"
    },
    {
      emoji: "💰", title: "预算敏感 + 完整方案",
      pick: "Langfuse 自托管", alt: "DeepEval",
      reason: "自托管 $0 / SaaS $59/月。Trace + LLM-Judge + Human 标注 + 成本追踪四合一。DeepEval 完全免费备选。"
    },
  ];

  scenarios.forEach((sc, i) => {
    const y = 0.85 + i * 0.88;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.3, y, w: 9.4, h: 0.75,
      fill: { color: C.card }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.3, y, w: 0.06, h: 0.75, fill: { color: C.accent }
    });

    s.addText(sc.emoji, {
      x: 0.55, y: y + 0.1, w: 0.4, h: 0.4,
      fontSize: 18, margin: 0
    });
    s.addText(sc.title, {
      x: 1.0, y: y + 0.1, w: 2.3, h: 0.35,
      fontSize: 11, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
    });

    s.addShape(pres.shapes.RECTANGLE, {
      x: 3.4, y: y + 0.12, w: 1.1, h: 0.28,
      fill: { color: C.accent, transparency: 60 }
    });
    s.addText("首选 " + sc.pick, {
      x: 3.4, y: y + 0.12, w: 1.1, h: 0.28,
      fontSize: 8.5, fontFace: FONT_BODY, color: C.white, align: "center", margin: 0
    });

    if (sc.alt !== "—") {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 4.65, y: y + 0.12, w: 1.0, h: 0.28,
        fill: { color: C.cardAlt }
      });
      s.addText("备选 " + sc.alt, {
        x: 4.65, y: y + 0.12, w: 1.0, h: 0.28,
        fontSize: 8.5, fontFace: FONT_BODY, color: C.grayL, align: "center", margin: 0
      });
    }

    s.addText(sc.reason, {
      x: 0.55, y: y + 0.45, w: 8.9, h: 0.28,
      fontSize: 9, fontFace: FONT_BODY, color: C.grayL, margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════════════
// SLIDE 8 — Five Key Gaps
// ════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  s.addText("五大关键空白——市场潜力与填补难度", {
    x: 0.3, y: 0.2, w: 9.4, h: 0.5,
    fontSize: 18, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });

  const gaps = [
    {
      num: "①", title: "Agent-as-Judge × 通用平台",
      desc: "6/9 平台（67%）完全空白。仅 Braintrust 有完整闭环。预期 1-2 年填补。",
      market: "高", difficulty: "中"
    },
    {
      num: "②", title: "Sandbox × 大众平台（垄断空白）",
      desc: "仅 LangSmith 提供 Docker 沙箱。类比早期 CI 在裸机运行测试→后来容器化成为标配。预期 2-3 年。",
      market: "高", difficulty: "高"
    },
    {
      num: "③", title: "Code-based 缺失（Galileo 专有路线）",
      desc: "Galileo 唯一不支持 Code-based 的平台。Luna-2 低成本弥补，但精确匹配等场景仍有缺陷。",
      market: "低", difficulty: "低"
    },
    {
      num: "④", title: "Simulation + Sandbox 组合（交汇空白）",
      desc: "Maxim 有 Simulation 无沙箱，LangSmith 有沙箱无 Simulation。黄金组合：隔离沙箱中运行仿真测试。",
      market: "中", difficulty: "高"
    },
    {
      num: "⑤", title: "Agent-as-Judge + OTel 原生集成",
      desc: "OTel 原生平台（Arize/Opik/Langfuse）均无 Agent-as-Judge。理想方案：Agent trace→OTel→Agent-Judge 评估 span tree。",
      market: "中", difficulty: "中"
    },
  ];

  gaps.forEach((g, i) => {
    addGapCard(s, 0.5, 0.9 + i * 0.92, g.num, g.title, g.desc, g.market, g.difficulty);
  });

  // Insight
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.15, w: 9, h: 0.45,
    fill: { color: C.card }
  });
  s.addText("格局洞察：开源阵营分化为「通用可观测」和「评估专精」两条路线。闭源专精玩家各有不可替代性。", {
    x: 0.7, y: 5.17, w: 8.6, h: 0.4,
    fontSize: 10, fontFace: FONT_BODY, color: C.grayL, margin: 0
  });
}

// ════════════════════════════════════════════════════════════════════════
// SLIDE 9 — Why This Matters
// ════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  s.addText("Why This Matters", {
    x: 0.3, y: 0.2, w: 9.4, h: 0.5,
    fontSize: 22, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });
  s.addText("为什么每个 AI 团队都该关注 Agent 评测", {
    x: 0.3, y: 0.65, w: 9.4, h: 0.4,
    fontSize: 13, fontFace: FONT_BODY, color: C.grayL, margin: 0
  });

  // Main statement
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.2, w: 9, h: 1.0,
    fill: { color: C.card }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.2, w: 0.06, h: 1.0, fill: { color: C.accent }
  });
  s.addText("Agent 正在从「对话机器人」进化为「自主执行者」。当 Agent 开始操作数据库、发 HTTP 请求、写文件、调用内部 API，评估就不能再只看最终输出——你需要全过程验证。", {
    x: 0.8, y: 1.3, w: 8.4, h: 0.55,
    fontSize: 11.5, fontFace: FONT_BODY, color: C.white, margin: 0
  });
  s.addText("评测不再是「跑个 benchmark」的事，而是生产基础设施。就像 CI/CD 测试从可选变成标配，Agent 评测也将成为每个 AI 工程团队的基本能力。", {
    x: 0.8, y: 1.78, w: 8.4, h: 0.35,
    fontSize: 9.5, fontFace: FONT_BODY, color: C.grayL, italic: true, margin: 0
  });

  // China-specific
  s.addText("对中国 AI 团队尤其关键", {
    x: 0.5, y: 2.5, w: 9, h: 0.35,
    fontSize: 14, fontFace: FONT_TITLE, color: C.accent, bold: true, margin: 0
  });

  const cnPoints = [
    "国内 Agent 生态缺少 LangSmith 级别的沙箱平台——这是基础设施级空缺",
    "开源方案（Langfuse/DeepEval）可零成本自托管，规避数据出境的合规风险",
    "Agent-as-Judge 空白意味着巨大创新空间——比做第 10 个 LLM 更有价值",
    "选对平台不只看范式数量，更要看「独特范式深度」——沙箱、Agent-Judge、专有评估模型"
  ];
  cnPoints.forEach((p, i) => {
    s.addText("•  " + p, {
      x: 0.8, y: 2.95 + i * 0.32, w: 8.4, h: 0.3,
      fontSize: 10, fontFace: FONT_BODY, color: C.grayL, margin: 0
    });
  });

  // Core judgment
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.35, w: 9, h: 1.0,
    fill: { color: C.cardAlt }
  });
  s.addText("核心判断", {
    x: 0.7, y: 4.4, w: 2, h: 0.3,
    fontSize: 12, fontFace: FONT_TITLE, color: C.accent, bold: true, margin: 0
  });
  s.addText("无平台覆盖全部 5 范式，意味着当前市场仍处于早期。未来 1-2 年最可能发生的变化：(1) 可观测平台收购评估专精团队；(2) Sandbox 从 LangSmith 的护城河变成全行业标配；(3) Agent-as-Judge 从稀缺能力变成必备功能。", {
    x: 0.7, y: 4.72, w: 8.6, h: 0.55,
    fontSize: 10.5, fontFace: FONT_BODY, color: C.grayL, margin: 0
  });
}

// ════════════════════════════════════════════════════════════════════════
// SLIDE 10 — References
// ════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.bg };

  s.addText("参考文献", {
    x: 0.3, y: 0.2, w: 9.4, h: 0.5,
    fontSize: 22, fontFace: FONT_TITLE, color: C.white, bold: true, margin: 0
  });

  // Research docs
  s.addText("调研产出", {
    x: 0.5, y: 0.9, w: 3, h: 0.3,
    fontSize: 13, fontFace: FONT_TITLE, color: C.accent, bold: true, margin: 0
  });

  const docs = [
    ["T1 范式分类", "paradigms.md — 5 范式定义、偏见问题、平台映射"],
    ["T1 维度矩阵", "dimensions.md — 4 维度（单步/多步、结果/轨迹、功能/安全/效率/成本、离线/在线）"],
    ["T1 沙箱分析", "sandbox.md — 3 层级隔离机制、LangSmith/Anthropic/OSWorld 方案"],
    ["T1 平台-范式映射", "platforms-paradigm-mapping.md — 9 平台 × 5 范式映射 + 差距分析"],
    ["T2 对比总表", "comparison-table.md — 10 平台横向对比全维度"],
    ["T2 平台详析", "platforms/ — 10 平台每平台详细分析"],
    ["T3 综合对比分析", "comprehensive-analysis.md — 本报告完整数据源"],
  ];

  docs.forEach((d, i) => {
    s.addText(d[0], {
      x: 0.5, y: 1.3 + i * 0.3, w: 1.8, h: 0.25,
      fontSize: 9, fontFace: FONT_TITLE, color: C.grayL, bold: true, margin: 0
    });
    s.addText(d[1], {
      x: 2.4, y: 1.3 + i * 0.3, w: 7, h: 0.25,
      fontSize: 9, fontFace: FONT_BODY, color: C.gray, margin: 0
    });
  });

  // Key papers
  s.addText("关键论文", {
    x: 0.5, y: 3.6, w: 3, h: 0.3,
    fontSize: 13, fontFace: FONT_TITLE, color: C.accent, bold: true, margin: 0
  });

  const papers = [
    "Zheng et al., \"Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena\", NeurIPS 2023",
    "Liu et al., \"G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment\", EMNLP 2023",
    "AgentBench: Evaluating LLMs as Agents, ICLR 2024",
    "GAIA: A General AI Assistant Benchmark",
    "WebArena: A Realistic Web Environment for Building Autonomous Agents"
  ];

  papers.forEach((p, i) => {
    s.addText("📚  " + p, {
      x: 0.5, y: 4.0 + i * 0.28, w: 9, h: 0.25,
      fontSize: 9, fontFace: FONT_BODY, color: C.gray, margin: 0
    });
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.565, w: 10, h: 0.06, fill: { color: C.accent }
  });
  s.addText("⚠️ 所有数据基于 T1-T3 调研产出（截至 2026-05-22）。定价可能随各平台政策变化。", {
    x: 0.5, y: 5.15, w: 9, h: 0.3,
    fontSize: 8.5, fontFace: FONT_BODY, color: C.gray, margin: 0
  });
}

// ════════════════════════════════════════════════════════════════════════
// WRITE
// ════════════════════════════════════════════════════════════════════════
const outPath = "/Users/yuminghao/Work/ai-news/output/Agent评测平台深度对比.pptx";
await pres.writeFile({ fileName: outPath });
console.log("✅ Written: " + outPath);

})();
