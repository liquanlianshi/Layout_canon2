# -*- coding: utf-8 -*-
"""生成「关键亮点说明」PDF 交付文档。

流程：站点风格 HTML（封面 / 项目概览 / 关键亮点 / 数据来源）→
      用系统 Edge（无头）打印为 A4 PDF。

产物：
  docs/亮点说明.html   可在浏览器直接打开、样式与站点一致
  docs/亮点说明.pdf    正式交付用文档

用法：python tools/make_report.py
依赖：playwright（复用 tools/check_pages.py 的浏览器启动逻辑，用系统 Edge 无头打印）
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
PALETTE_CSS = ROOT / "assets" / "css" / "palette.css"
OUT_HTML = ROOT / "docs" / "亮点说明.html"
OUT_PDF = ROOT / "docs" / "亮点说明.pdf"

# 页面：标题 + 核心内容（用于项目概览表）
PAGES = [
    ("总览", "概念坐标 · 四项关键数据 · AI 重构生产力三要素 · 价值传导链路"),
    ("产业规模", "核心产业规模与 2030 目标 · 生成式 AI 专利格局 · 东数西算 8 大枢纽地图 · 算力结构"),
    ("行业渗透", "行业×环节渗透热力图 · 价值传导桑基图 · 实证效率研究 · 行业成熟度雷达 · 场景热度词云"),
    ("劳动力变革", "岗位创造与替代瀑布图 · 技能重构 · 2030 核心技能 TOP8 · 新职业时间轴 · 人机分工"),
    ("未来展望", "政策时间轴 · 2030 目标完成度仪表盘 · 技术扩散 S 曲线 · 成熟度采纳象限 · 治理与风险"),
    ("社会影响", "就业与收入 · 日常生活 · 区域协调 · 绿色低碳 —— 11 组数据图形"),
]

SOURCES = [
    ("核心产业规模、企业数量、算力规模、5G 基站、智能制造示范工厂", "工业和信息化部"),
    ("生成式 AI 用户规模与普及率（2.3 → 2.49 → 5.15 亿）", "CNNIC《中国互联网络发展状况统计报告》第 54/55/56 次"),
    ("生成式 AI 专利（中国 3.8 万件，约占全球七成）", "WIPO《Generative AI: Patent Landscape》2024"),
    ("全球 AI 支出（1540 / 2350 / 3070 / 6320 亿美元）", "IDC Worldwide AI Spending Guide"),
    ("全球 AI 私人投资 1091 亿美元", "Stanford AI Index 2025"),
    ("岗位创造 1.7 亿 / 替代 9200 万 / 技能重构 39% / 59% 需再培训", "WEF《Future of Jobs Report 2025》"),
    ("编码任务提速 55.8%", "GitHub & 微软对照实验（2022，95 名开发者）"),
    ("知识工作提速 25.1%、质量提升 40%", "BCG & 哈佛大学实验（2023，758 名顾问）"),
    ("客服生产率提升 14%", "麦肯锡（2023）"),
    ("东数西算 8 枢纽 10 集群", "国家发展改革委等四部门实施方案（2021）"),
    ("新职业（人工智能工程技术人员 / 训练师 / 生成式 AI 系统应用员等）", "人力资源和社会保障部历次新发布"),
    ("政策时间轴（2017 规划 → 2023 暂行办法 → 2024「人工智能+」）", "国务院、科技部、全国网络安全标准化技术委员会"),
]

HIGHLIGHTS = [
    ("内容亮点", "一条完整的论证链", [
        "从概念到证据：先用「生产力三要素」框架解释 AI 为什么属于新质生产力，再用产业规模（宏观）、行业渗透（中观）、劳动力变革（微观）三层证据支撑，最后落到政策与治理边界。",
        "数据分层标注：严格区分「官方统计 / 第三方研究 / 示意性相对评估」三类，示意类图表均在图上注明，避免误读。",
        "用可视化讲抽象概念：桑基图解释「技术如何变成收益」，瀑布图解释「岗位净增 7800 万怎么来的」，S 曲线解释「为什么现在是加速期」。",
    ]),
    ("可视化亮点", "全站 10+ 种图表类型，每一种都服务于内容", [
        "折线/面积、柱状、瀑布、横向条形、热力图、桑基图、雷达图、环形图、仪表盘、象限散点、地图涟漪散点（含十段线的中国地图）、词云，另有 markArea / markLine 标注。",
        "统一主题：一处 registerTheme 定义全站图表的字体、坐标轴、提示框与图例样式；图表进入视口才渲染（懒初始化），长页面滚动依然流畅。",
        "细节动效：数字滚动计数、阅读进度条、卡片上浮、滚动渐显、涟漪扩散；并尊重 prefers-reduced-motion（系统开启减弱动效时自动关闭动画）。",
    ]),
    ("设计亮点", "多彩低饱和度，且「可验证」", [
        "实现方式：统一饱和度与明度、只变化色相 —— 8 个色相环均匀分布，主色统一 HSL(52%, 63%)。",
        "不是拍脑袋选色：调色板由脚本生成，并有自动化断言守护（饱和度超过 60%、色相跨度不足、明度越界或重新引入高饱和色都会导致测试失败）。",
        "浅色柔光基调：白卡片 + 大圆角 + 柔和投影 + 细描边；图表与强调元素承担色彩，大面积留白保证可读性。",
    ]),
    ("工程亮点", "零构建交付 + 自动化验收", [
        "零构建、零 CDN 依赖：ECharts、词云插件、中国地图 GeoJSON 全部本地化，断网可运行；vendor/SOURCES.json 记录来源与 sha256，可联网核对与上游字节级一致。",
        "自动化校验：结构 / 资源引用 / 图表绑定 / 插件加载 / 路径白名单 / zip-slip 防护 / 色彩断言，共数十项断言，在源码目录与解压副本中均全绿。",
        "交付自检：解压包逐个文件与源码做 sha256 比对，并复用打包白名单双向核对文件集合，确保「包内内容 = 源码内容」。",
    ]),
]

CSS = """
@page { size: A4; margin: 15mm 14mm 13mm; }
* { box-sizing: border-box; }
body { margin: 0; color: #323A4D; background: #fff;
  font-family: "PingFang SC","HarmonyOS Sans SC","Microsoft YaHei","Noto Sans SC",sans-serif;
  font-size: 10.5pt; line-height: 1.72; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
h1,h2,h3 { margin: 0; line-height: 1.3; }
p { margin: 0 0 8px; }
a { color: #38519F; text-decoration: none; }

/* ---- 封面 ---- */
.cover { position: relative; height: 262mm; display: flex; flex-direction: column; justify-content: center;
  page-break-after: always; padding-left: 6mm; }
.cover .halo { position: absolute; inset: -12mm -6mm auto -6mm; height: 116mm; opacity: .30;
  background:
    radial-gradient(38% 46% at 18% 30%, $c1 0%, transparent 58%),
    radial-gradient(34% 42% at 74% 12%, $c5 0%, transparent 58%),
    radial-gradient(42% 48% at 82% 78%, $c4 0%, transparent 58%),
    radial-gradient(34% 42% at 26% 88%, $c3 0%, transparent 58%); }
.cover > *:not(.halo) { position: relative; z-index: 1; }
.cover .kicker { font-size: 10pt; letter-spacing: .34em; color: #6B7280; text-transform: uppercase; }
.cover h1 { font-size: 34pt; margin: 8mm 0 3mm; letter-spacing: .01em; }
.cover h1 .grad { background: linear-gradient(96deg, $c6d, $c7d 45%, $c1d 90%);
  -webkit-background-clip: text; background-clip: text; color: transparent; }
.cover .sub { font-size: 13pt; color: #6B7280; margin-bottom: 12mm; }
.cover .metrics { display: flex; gap: 5mm; flex-wrap: wrap; margin-bottom: 12mm; }
.cover .metric { background: #fff; border: 1px solid #E8EAF0; border-radius: 4mm; padding: 4mm 5mm; min-width: 33mm;
  box-shadow: 0 2mm 6mm rgba(50,58,77,.06); }
.cover .metric b { display: block; font-size: 17pt; color: $c6d; line-height: 1.2; }
.cover .metric span { font-size: 8.5pt; color: #6B7280; }
.cover .foot { font-size: 9pt; color: #9CA3AF; border-top: 1px solid #E8EAF0; padding-top: 4mm; }
.cover .swatchbar { height: 3mm; border-radius: 3mm; margin-bottom: 6mm;
  background: linear-gradient(90deg, $c1, $c2, $c3, $c4, $c5, $c6, $c7, $c8); }

/* ---- 章节 ---- */
section { page-break-inside: auto; margin-bottom: 9mm; }
h2 { font-size: 15pt; margin: 0 0 4mm; padding-left: 4mm; border-left: 2.5mm solid var(--accent, $c5); }
h2 small { display: block; font-size: 9pt; font-weight: 400; color: #6B7280; letter-spacing: .18em; margin-bottom: 1mm; }
h3 { font-size: 11.5pt; margin: 5mm 0 2mm; color: $c6d; }
.lead { color: #6B7280; }
ol, ul { margin: 0 0 4mm; padding-left: 5mm; }
li { margin-bottom: 1.6mm; }

/* ---- 卡片 ---- */
.grid { display: flex; gap: 4mm; flex-wrap: wrap; }
.card { flex: 1 1 45%; background: #fff; border: 1px solid #E8EAF0; border-radius: 3mm; padding: 4mm 4.5mm;
  box-shadow: 0 1.5mm 5mm rgba(50,58,77,.05); page-break-inside: avoid; }
.card b { color: #323A4D; }
.card .tag { display: inline-block; font-size: 8.5pt; font-weight: 700; letter-spacing: .06em;
  color: $c5d; background: $c5s; border-radius: 999px; padding: .6mm 3mm; margin-bottom: 2mm; }

/* ---- 表格 ---- */
table { width: 100%; border-collapse: collapse; font-size: 9.5pt; page-break-inside: avoid; }
th, td { text-align: left; padding: 2.2mm 3mm; border-bottom: 1px solid #E8EAF0; vertical-align: top; }
th { background: #F7F8FA; font-size: 9pt; color: #6B7280; }
td:last-child { color: #6B7280; }

/* ---- 提示块 ---- */
.note { background: #F7F8FA; border: 1px solid #E8EAF0; border-radius: 3mm; padding: 3.5mm 4mm; font-size: 9.5pt; color: #6B7280; }
.avoid { page-break-inside: avoid; }
"""


def page_files() -> list[Path]:
    """站点页面文件（根目录下的 *.html）。"""
    return sorted(ROOT.glob("*.html"))


def count_charts() -> int:
    """统计站点页面里的图表容器数量（id="chart-…"），避免在文档里硬编码数字。"""
    return sum(len(re.findall(r'id="chart-[^"]+"', p.read_text(encoding="utf-8")))
               for p in page_files())


def count_tests() -> int | None:
    """通过 pytest --collect-only 收集用例数，让报告数字与实际测试保持一致（避免硬编码失同步）。"""
    try:
        import subprocess

        proc = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--collect-only"],
                              cwd=ROOT, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0:
            return None
        match = re.search(r"(\d+)\s+tests? collected", proc.stdout)
        return int(match.group(1)) if match else None
    except Exception:  # noqa: BLE001
        return None


def load_palette() -> dict[str, str]:
    css = PALETTE_CSS.read_text(encoding="utf-8")
    colors: dict[str, str] = {}
    for idx, hexv in re.findall(r"--c(\d):\s*(#[0-9A-Fa-f]{6})", css):
        colors[f"c{idx}"] = hexv
    for idx, hexv in re.findall(r"--c(\d)-soft:\s*(#[0-9A-Fa-f]{6})", css):
        colors[f"c{idx}s"] = hexv
    for idx, hexv in re.findall(r"--c(\d)-deep:\s*(#[0-9A-Fa-f]{6})", css):
        colors[f"c{idx}d"] = hexv
    if len([k for k in colors if re.fullmatch(r"c\d", k)]) < 8:
        raise RuntimeError("未能从 palette.css 解析出 8 个主色")
    for suffix, label in (("s", "soft"), ("d", "deep")):
        missing = [f"c{i}" for i in range(1, 9) if f"c{i}{suffix}" not in colors]
        if missing:
            raise RuntimeError(f"palette.css 缺少 {label} 变体：{missing}")
    return colors


def build_html(pal: dict[str, str]) -> str:
    n_tests = count_tests()
    n_pages = len(page_files())
    n_charts = count_charts()
    metrics = "".join(
        f'<div class="metric"><b>{v}</b><span>{k}</span></div>'
        for v, k in [(str(n_pages), "个页面"), (str(n_charts), "个交互图表"), ("10+", "种图表类型"),
                     (str(n_tests) if n_tests else "数十", "项自动化校验"),
                     ("8", "色相低饱和调色板")]
    )
    cards = ""
    for accent_no, (title, tagline, bullets) in enumerate(HIGHLIGHTS, start=1):
        items = "".join(f"<li>{b}</li>" for b in bullets)
        cards += (f'<div class="card" style="--accent: {pal[f"c{accent_no}"]}">'
                  f'<span class="tag">{title}</span><h3 style="margin-top:0">{tagline}</h3>'
                  f'<ul>{items}</ul></div>')
    rows = "".join(f"<tr><td>{item}</td><td>{src}</td></tr>" for item, src in SOURCES)
    page_rows = "".join(f"<tr><td><b>{title}</b></td><td>{desc}</td></tr>" for title, desc in PAGES)

    tpl = Template("""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>AI × 新质生产力 · 关键亮点说明</title>
<style>$css</style></head>
<body>

<div class="cover">
  <div class="halo"></div>
  <div class="swatchbar"></div>
  <div class="kicker">Data Visualization · Key Highlights</div>
  <h1>人工智能，正在成为<br><span class="grad">新质生产力的核心引擎</span></h1>
  <div class="sub">数据可视化网站 · 关键亮点说明</div>
  <div class="metrics">$metrics</div>
  <div class="foot">
    主题：人工智能作为新质生产力的作用和意义<br>
    技术栈：HTML / CSS / 原生 JavaScript + Apache ECharts 5（本地内置，零构建、可离线运行）<br>
    生成日期：$today
  </div>
</div>

<section>
  <h2 style="--accent: $c5"><small>01 · OVERVIEW</small>项目概览</h2>
  <p class="lead">本网站用一个「从概念到证据、从宏观到微观」的完整叙事，回答人工智能为什么是新质生产力、
     以及它正在如何改变中国经济。全站 $n_pages 个页面、$n_charts 个可交互图表，所有数据均标注来源，
     示意性评估均明确区分。</p>
  <table class="avoid">
    <thead><tr><th style="width:26%">页面</th><th>核心内容</th></tr></thead>
    <tbody>$page_rows</tbody>
  </table>
</section>

<section>
  <h2 style="--accent: $c6"><small>02 · CONTENT</small>关键亮点</h2>
  <div class="grid">$cards</div>
</section>

<section>
  <h2 style="--accent: $c5"><small>03 · SOURCES</small>主要数据来源</h2>
  <table>
    <thead><tr><th style="width:52%">数据</th><th>来源</th></tr></thead>
    <tbody>$rows</tbody>
  </table>
  <p class="note" style="margin-top:4mm">渗透热力图、成熟度雷达、S 扩散曲线、采纳象限图为示意性相对评估，
     用于表达结构差异，已在对应图表下方明确标注，不作为统计数据引用。</p>
</section>

</body></html>""")

    # 注意：string.Template 不会二次扫描「插入的值」，因此 CSS 里的颜色占位符必须先单独替换一遍
    css_rendered = Template(CSS).substitute(**pal)
    return tpl.substitute(
        css=css_rendered, metrics=metrics, cards=cards,
        rows=rows, page_rows=page_rows, today=date.today().isoformat(),
        n_pages=str(n_pages), n_charts=str(n_charts),
        **pal,
    )


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("需要 playwright：pip install playwright") from None

    sys.path.insert(0, str(Path(__file__).parent))
    from check_pages import launch_browser  # 复用「优先系统 Edge」的启动逻辑

    with sync_playwright() as pw:
        browser = launch_browser(pw)
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="load")
        page.emulate_media(media="print")
        page.wait_for_timeout(600)
        page.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True)
        browser.close()


def verify_pdf(pdf_path: Path, min_pages: int = 3) -> tuple[int, int]:
    """校验产物：PDF 头正确、页数不低于下限（否则视为渲染失败）。

    注意：页数用 /Type /Page 明文统计，Edge 当前的 PDF 输出格式下可靠；
    若未来改为对象流压缩导致统计为 0，会报「页数异常」而非静默通过。
    """
    data = pdf_path.read_bytes()
    if not data.startswith(b"%PDF-"):
        raise RuntimeError("生成的文件不是有效 PDF")
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    if pages < min_pages:
        raise RuntimeError(f"PDF 页数异常（解析得 {pages} 页，低于下限 {min_pages}）：可能渲染失败")
    if len(data) < 50_000:
        raise RuntimeError(f"PDF 体积异常（{len(data)} 字节），可能内容缺失")
    return len(data), pages


def main() -> int:
    pal = load_palette()
    OUT_HTML.write_text(build_html(pal), encoding="utf-8")
    print(f"报告 HTML -> {OUT_HTML.relative_to(ROOT)}")

    render_pdf(OUT_HTML, OUT_PDF)
    size, pages = verify_pdf(OUT_PDF)
    print(f"PDF -> {OUT_PDF.relative_to(ROOT)}  {size / 1024:.0f} KB  {pages} 页")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
