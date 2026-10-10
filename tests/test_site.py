# -*- coding: utf-8 -*-
"""站点自动化校验：资源完整性、HTML 结构、图表绑定、配色规范。

运行：python -m pytest tests/ -q
"""
from __future__ import annotations

import colorsys
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(p for p in ROOT.glob("*.html"))
REQUIRED_PAGES = {"index.html", "scale.html", "industry.html", "labor.html", "future.html", "social.html"}
NAV_TARGETS = ["index.html", "scale.html", "industry.html", "labor.html", "future.html", "social.html"]
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}


# ---------------------------------------------------------------- helpers
class TagBalanceChecker(HTMLParser):
    """轻量标签闭合校验（忽略 void 元素，script/style 由 HTMLParser 按 CDATA 处理）。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, tuple[int, int]]] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag not in VOID_TAGS:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        if not self.stack:
            self.errors.append(f"多余的结束标签 </{tag}> @ {self.getpos()}")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        self.errors.append(
            f"标签不匹配：期望 </{self.stack[-1][0]}>（开于 {self.stack[-1][1]}），遇到 </{tag}> @ {self.getpos()}"
        )
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def close_report(self) -> list[str]:
        for tag, pos in self.stack:
            self.errors.append(f"未闭合标签 <{tag}> 开于 {pos}")
        return self.errors


def parse_page(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def scripts_of(html: str) -> list[str]:
    """页面引用的脚本路径（归一化：反斜杠转斜杠、去掉 ./ 前缀，兼容单双引号与 defer/async）。"""
    raw = re.findall(r"""<script[^>]*\bsrc=["']([^"']+)["']""", html)
    return [r.replace("\\", "/").removeprefix("./") for r in raw]


def local_refs(html: str) -> list[str]:
    """页面引用的本地资源路径（归一化，兼容单双引号；排除外链/锚点/内联数据）。"""
    refs = re.findall(r"""(?:src|href)=["']([^"']+)["']""", html)
    refs = [r.replace("\\", "/").removeprefix("./") for r in refs]
    return [r for r in refs if not r.startswith(("http://", "https://", "data:", "#", "mailto:"))]


# ---------------------------------------------------------------- 基础结构
def test_required_pages_exist() -> None:
    names = {p.name for p in PAGES}
    missing = REQUIRED_PAGES - names
    assert not missing, f"缺少页面文件: {sorted(missing)}"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_html_tags_balanced(page: Path) -> None:
    checker = TagBalanceChecker()
    checker.feed(parse_page(page))
    assert not checker.close_report(), f"{page.name} 标签不闭合"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_local_resources_exist(page: Path) -> None:
    bad: list[str] = []
    for ref in local_refs(parse_page(page)):
        target = (ROOT / ref).resolve()
        if not target.is_relative_to(ROOT) or not target.exists():
            bad.append(ref)
    assert not bad, f"{page.name} 引用了不存在或越出项目目录的本地资源: {bad}"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_page_has_meta_and_nav(page: Path) -> None:
    html = parse_page(page)
    assert re.search(r"<title>.+?</title>", html, re.S), f"{page.name} 缺少 title"
    assert 'name="description"' in html, f"{page.name} 缺少 description"
    assert 'name="viewport"' in html, f"{page.name} 缺少 viewport（移动端适配）"
    for target in NAV_TARGETS:
        assert f'href="{target}"' in html, f"{page.name} 导航缺少 {target}"
    assert "<footer" in html, f"{page.name} 缺少页脚"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_palette_loaded_before_charts(page: Path) -> None:
    html = parse_page(page)
    assert "assets/css/palette.css" in html, f"{page.name} 未引入 palette.css"
    assert "assets/css/main.css" in html, f"{page.name} 未引入 main.css"
    js = scripts_of(html)
    if any("chart" in s for s in js):
        assert "assets/js/palette.js" in js, f"{page.name} 使用了图表但未加载 palette.js"
        assert "vendor/echarts.min.js" in js, f"{page.name} 使用了图表但未加载 ECharts"
        assert "assets/js/site.js" in js, f"{page.name} 使用了图表但未加载 site.js"


# ---------------------------------------------------------------- 图表绑定
@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_every_chart_container_is_registered(page: Path) -> None:
    html = parse_page(page)
    ids = re.findall(r'id="(chart-[a-z0-9-]+)"', html)
    if not ids:
        pytest.skip(f"{page.name} 无图表容器")
    bundle = "\n".join(
        (ROOT / s).read_text(encoding="utf-8")
        for s in scripts_of(html)
        if (ROOT / s).exists()
    )
    unbound = [i for i in ids if f'registerChart("{i}"' not in bundle and f"registerChart('{i}'" not in bundle]
    assert not unbound, f"{page.name} 中未绑定数据的图表容器: {unbound}"


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_optional_plugins_loaded_when_used(page: Path) -> None:
    """运行时插件（词云 / 中国地图）必须与其使用页面同步加载，否则浏览器会报错。

    识别方式：读取页面引入的 assets/js/*.js，剥离注释后按字面量匹配
    （type: "wordCloud" / CHINA_GEOJSON）。变量别名或动态拼接的写法无法识别。
    """
    html = parse_page(page)
    if "assets/css/main.css" not in html:
        pytest.skip(f"{page.name} 不是站点主页面（未引用 main.css）")
    scripts = scripts_of(html)
    js_files = [s for s in scripts if s.startswith("assets/js/")]
    assert js_files, f"{page.name} 未发现任何 assets/js 脚本引用（脚本标签或路径写法可能已变更）"
    bundle = "\n".join(
        (ROOT / s).read_text(encoding="utf-8") for s in js_files if (ROOT / s).exists()
    )
    assert bundle, f"{page.name} 引用的脚本文件均不存在"
    code = re.sub(r"/\*.*?\*/", "", bundle, flags=re.S)          # 去块注释
    code = re.sub(r"(?m)^\s*//.*$", "", code)                     # 去行注释
    if re.search(r'type:\s*["\']wordCloud["\']', code):
        assert "vendor/echarts-wordcloud.min.js" in scripts, \
            f"{page.name} 使用了 wordCloud 图表系列，但未加载 vendor/echarts-wordcloud.min.js"
    if "CHINA_GEOJSON" in code:
        assert "vendor/china-map.js" in scripts, \
            f"{page.name} 使用了中国地图数据，但未加载 vendor/china-map.js"


def test_no_duplicate_chart_ids_across_pages() -> None:
    seen: dict[str, str] = {}
    dupes = []
    for page in PAGES:
        for cid in re.findall(r'id="(chart-[a-z0-9-]+)"', parse_page(page)):
            if cid in seen:
                dupes.append((cid, seen[cid], page.name))
            seen[cid] = page.name
    assert not dupes, f"图表 id 跨页重复（会混淆维护）: {dupes}"


def test_local_server_path_guard() -> None:
    """本地检查服务的路径白名单判定（纯函数级守护，防编码/反斜杠/穿越绕过）。"""
    sys.path.insert(0, str(ROOT / "tools"))
    import check_pages  # noqa: PLC0415

    allowed = ["/", "/index.html", "/scale.html", "/assets/css/main.css",
               "/assets/js/site.js", "/vendor/echarts.min.js", "/favicon.ico"]
    denied = ["/.reasonix/", "/%2ereasonix/", "/.pytest_cache/",
              "/toolS/../../.reasonix/", "/assets/%2e%2e/README.md",
              "/assets/%252e%252e/README.md",
              "/assets/x%5c..%5c..%5cREADME.md", "/README.md", "/docs/"]
    for path in allowed:
        assert not check_pages.is_denied(path), f"{path} 应被放行但被拒绝"
    for path in denied:
        assert check_pages.is_denied(path), f"{path} 应被拒绝但被放行"


def test_release_verifier_member_guard() -> None:
    """交付验收脚本的 zip-slip 防护：成员名安全判定。"""
    sys.path.insert(0, str(ROOT / "tools"))
    import verify_release  # noqa: PLC0415

    safe = ["index.html", "assets/css/main.css", "docs/screenshots/index.jpg",
            "a/b/c.txt", "中文目录/页面.html"]
    unsafe = ["", "/etc/passwd", "\\x", "C:/x", "a\\b", "a/../../b", "..", "../x", "./.."]
    for name in safe:
        assert verify_release.member_is_safe(name), f"{name!r} 应判为安全成员名"
    for name in unsafe:
        assert not verify_release.member_is_safe(name), f"{name!r} 应判为不安全成员名"


def test_preview_host_guard() -> None:
    """预览服务的 Host 校验（防 DNS rebinding）：纯函数级回归。"""
    sys.path.insert(0, str(ROOT / "tools"))
    import preview  # noqa: PLC0415

    allowed = ["127.0.0.1", "127.0.0.1:8080", "LOCALHOST:9000", "localhost", " localhost "]
    denied = ["", "   ", "evil.com", "evil.com:8080", "127.0.0.1.evil.com",
              "localhost.evil.com", "[::1]:8080", None]
    for host in allowed:
        assert preview.host_allowed(host), f"{host!r} 应被允许"
    for host in denied:
        assert not preview.host_allowed(host), f"{host!r} 应被拒绝"


def test_report_builder_helpers() -> None:
    """报告生成器的纯函数：调色板解析与 HTML 渲染（不触发浏览器）。"""
    sys.path.insert(0, str(ROOT / "tools"))
    import make_report  # noqa: PLC0415

    pal = make_report.load_palette()
    for i in range(1, 9):
        assert re.fullmatch(r"#[0-9A-Fa-f]{6}", pal[f"c{i}"]), f"主色 c{i} 解析异常"
        assert pal[f"c{i}s"], f"缺少 c{i} 的 soft 变体"
        assert pal[f"c{i}d"], f"缺少 c{i} 的 deep 变体"
    html = make_report.build_html(pal)
    # 检查未替换的模板占位符（形如 $name），而非任意 $ 字符
    assert not re.search(r"\$[a-z_]", html), "生成的 HTML 仍含未替换的模板占位符（Template 二次替换陷阱）"
    assert "新质生产力" in html and "色相" in html


def test_readme_numbers_match_reality() -> None:
    """README 声明的图表数量必须与页面实际一致（防止文档与实现漂移）。"""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    actual = sum(len(re.findall(r'id="chart-[^"]+"', p.read_text(encoding="utf-8")))
                 for p in ROOT.glob("*.html"))
    assert re.search(rf"(?<!\d){actual} 个可交互图表", readme), f"README 未声明可交互图表数量（实际 {actual} 个）"
    assert f"含 {actual} 个可交互 ECharts 图表" in readme, f"README 顶部数字与实际不一致（实际 {actual} 个）"


def test_report_numbers_match_source() -> None:
    """已生成的报告 HTML 必须与当前源码一致（防止忘记重跑 tools/make_report.py）。"""
    html_path = ROOT / "docs" / "亮点说明.html"
    if not html_path.exists():
        pytest.skip("尚未生成 docs/亮点说明.html")
    html = html_path.read_text(encoding="utf-8")
    pages = list(ROOT.glob("*.html"))
    charts = sum(len(re.findall(r'id="chart-[^"]+"', p.read_text(encoding="utf-8"))) for p in pages)
    assert f"<b>{len(pages)}</b><span>个页面</span>" in html, "报告中的页面数已过期，请重新运行 tools/make_report.py"
    assert f"<b>{charts}</b><span>个交互图表</span>" in html, "报告中的图表数已过期，请重新运行 tools/make_report.py"


def test_pdf_report_excludes_removed_sections() -> None:
    """已生成的交付 PDF 不得再含已删除章节（PDF 内容流是压缩的，必须解压文本后断言）。

    去掉空白后再比对，避免关键词被换行拆开导致漏检；缺 pymupdf 时跳过。
    """
    pdf = ROOT / "docs" / "亮点说明.pdf"
    if not pdf.exists():
        pytest.skip("尚未生成 docs/亮点说明.pdf")
    fitz = pytest.importorskip("fitz")

    doc = fitz.open(pdf)
    body = re.sub(r"\s+", "", "\n".join(page.get_text() for page in doc))
    for word in ("运行与自测", "REPRODUCE", "页面整页预览", "配色规范", "preview.py", "check_pages"):
        assert re.sub(r"\s+", "", word) not in body, f"交付 PDF 中仍包含应删除内容：{word}"
    for word in ("项目概览", "关键亮点", "主要数据来源"):
        assert word in body, f"交付 PDF 缺少应有章节：{word}"


def test_vendor_manifest_helpers() -> None:
    """vendor 清单工具的纯函数：GeoJSON 提取、正则匹配与规范化幂等。"""
    pytest.importorskip("requests")
    sys.path.insert(0, str(ROOT / "tools"))
    import setup_vendor  # noqa: PLC0415

    raw = (setup_vendor.VENDOR / "china-map.js").read_text(encoding="utf-8")
    assert setup_vendor.GEO_PATTERN.search(raw), "GEO_PATTERN 应能匹配 china-map.js"
    payload = setup_vendor.local_china_payload()
    geo = json.loads(payload)
    assert geo.get("type") == "FeatureCollection", "提取出的应是 GeoJSON FeatureCollection"
    assert len(geo["features"]) >= 30, "中国地图应包含 30+ 个省级要素"
    once = setup_vendor.canonical(payload)
    assert setup_vendor.canonical(once) == once, "规范化应幂等：再规范化一次结果不变"


# ---------------------------------------------------------------- 配色规范
def hex_to_hsv(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)


def palette_css() -> str:
    return (ROOT / "assets" / "css" / "palette.css").read_text(encoding="utf-8")


def test_palette_is_low_saturation() -> None:
    """核心验收标准：所有主色饱和度低（HSV S <= 0.60）。"""
    mains = re.findall(r"--c(\d):\s*(#[0-9A-Fa-f]{6})", palette_css())
    assert len(mains) >= 8, "调色板主色数量不足 8 个"
    offenders = []
    for idx, hexv in mains:
        _h, s, _v = hex_to_hsv(hexv)
        if s > 0.60:
            offenders.append((f"--c{idx}", hexv, round(s, 3)))
    assert not offenders, f"存在饱和度超过 60% 的主色（不符合低饱和度要求）: {offenders}"


def test_palette_is_colourful() -> None:
    """核心验收标准：色相覆盖广（跨度 >= 300°），保证「鲜艳多彩」。"""
    mains = re.findall(r"--c(\d):\s*(#[0-9A-Fa-f]{6})", palette_css())
    hues = sorted(hex_to_hsv(h)[0] * 360 for _i, h in mains)
    span = hues[-1] - hues[0]
    assert span >= 300, f"色相跨度仅 {span:.0f}°，不够「鲜艳多彩」"


def test_palette_brightness_in_range() -> None:
    """明度不能太低（要鲜活），也不能糊成白色。"""
    mains = re.findall(r"--c(\d):\s*(#[0-9A-Fa-f]{6})", palette_css())
    bad = [(f"--c{i}", h, round(hex_to_hsv(h)[2], 3)) for i, h in mains
           if not (0.55 <= hex_to_hsv(h)[2] <= 0.95)]
    assert not bad, f"主色明度超出 [0.55, 0.95] 区间: {bad}"


def test_palette_js_matches_css() -> None:
    js = (ROOT / "assets" / "js" / "palette.js").read_text(encoding="utf-8")
    css = palette_css()
    css_mains = [h for _i, h in re.findall(r"--c(\d):\s*(#[0-9A-Fa-f]{6})", css)]
    for hexv in css_mains:
        assert hexv in js, f"palette.js 缺少主色 {hexv}（CSS 与 JS 不一致）"


def test_no_hardcoded_bright_blue_regression() -> None:
    """回归保护：不得引入截图里那种高饱和蓝（如 #2445EA）。"""
    bright = re.compile(r"#(?:2445EA|2444EE|1E50FF|0A5CFF)", re.I)
    for f in list(PAGES) + list((ROOT / "assets").rglob("*.*")):
        if f.suffix.lower() in {".html", ".css", ".js"}:
            assert not bright.search(f.read_text(encoding="utf-8", errors="ignore")), \
                f"{f.name} 出现高饱和蓝，破坏低饱和度规范"
