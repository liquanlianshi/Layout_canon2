# -*- coding: utf-8 -*-
"""无头浏览器逐页检查：真实渲染每个页面，收集 JS 错误，确认图表绘制成功。

用法：python tools/check_pages.py [--shots]
依赖：pip install playwright（使用系统 Edge/Chrome，无需下载浏览器）
退出码：0 = 全部通过；1 = 存在错误；2 = 未安装 playwright（仅完成安全自检）

本地静态服务只暴露站点白名单文件（页面 + /assets/ + /vendor/），
其余路径一律 403；脚本启动时会先做一次安全自检（见 is_denied / self_check）。
"""
from __future__ import annotations

import functools
import http.server
import posixpath
import sys
import threading
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOT_DIR = ROOT / ".reasonix" / "scratch" / "screenshots"
PAGES = ["index.html", "scale.html", "industry.html", "labor.html", "future.html", "social.html"]

ALLOWED_PREFIXES = ("/assets/", "/vendor/")
ALLOWED_FILES = {"/", "/favicon.ico"} | {"/" + name for name in PAGES}   # "/" 映射到 index.html


def is_denied(raw_path: str) -> bool:
    """请求路径是否应被拒绝（纯函数，便于单元测试）。

    与 SimpleHTTPRequestHandler.translate_path 的规范化顺序对齐：
    去掉查询串/锚点 → URL 解码 → 反斜杠归一 → posixpath.normpath → 白名单前缀判定。
    这样 `%2e`、`%2e%2e`、`%5c..%5c` 等编码写法都先还原再判定，无法绕过。
    """
    clean = raw_path.split("?", 1)[0].split("#", 1)[0]
    decoded = urllib.parse.unquote(urllib.parse.unquote(clean))  # 解两轮，兼顾双重编码防御
    normalized = posixpath.normpath(decoded.replace("\\", "/"))
    if normalized in ALLOWED_FILES:
        return False
    return not any(normalized.startswith(prefix) for prefix in ALLOWED_PREFIXES)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """只暴露站点白名单文件；其余（含隐藏目录、编码/反斜杠绕过）一律 403。"""

    def log_message(self, fmt, *args):  # noqa: ANN002
        pass

    def do_GET(self):  # noqa: N802
        if is_denied(self.path):
            self.send_error(403, "path not exposed")
            return
        super().do_GET()

    def do_HEAD(self):  # noqa: N802
        if is_denied(self.path):
            self.send_error(403, "path not exposed")
            return
        super().do_HEAD()


def start_server() -> tuple[http.server.ThreadingHTTPServer, int]:
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def launch_browser(pw):  # noqa: ANN001
    last = None
    for channel in ("msedge", "chrome", None):
        try:
            if channel:
                print(f"  使用系统浏览器: {channel}")
                return pw.chromium.launch(channel=channel)
            print("  使用 playwright 自带 chromium")
            return pw.chromium.launch()
        except Exception as exc:  # noqa: BLE001
            last = exc
    raise RuntimeError(f"无法启动任何浏览器: {last}")


def self_check(base: str) -> bool:
    """安全自检：站点文件可访问（200），隐藏/越权路径必须被拒绝（403）。

    覆盖：隐藏目录、百分号编码绕过、路径穿越、白名单前缀内的编码 ..、
    Windows 反斜杠分隔符、HEAD 方法。
    """
    import urllib.error
    import urllib.request

    cases = [
        ("GET", "/", 200),
        ("GET", "/index.html", 200),
        ("GET", "/assets/css/main.css", 200),
        ("GET", "/.reasonix/", 403),
        ("GET", "/%2ereasonix/", 403),
        ("GET", "/.pytest_cache/", 403),
        ("GET", "/toolS/../../.reasonix/", 403),
        ("GET", "/assets/%2e%2e/README.md", 403),
        ("GET", "/assets/x%5c..%5c..%5cREADME.md", 403),
        ("HEAD", "/.reasonix/", 403),
    ]
    ok = True
    for method, path, want in cases:
        req = urllib.request.Request(base + path, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                code = resp.status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except Exception:  # noqa: BLE001
            code = -1
        good = code == want
        ok &= good
        print(f"  自检 {method:4s} {path:28s} -> HTTP {code} (期望 {want}) {'OK' if good else 'NG'}")
    return ok


def main() -> int:
    take_shots = "--shots" in sys.argv

    httpd, port = start_server()
    base = f"http://127.0.0.1:{port}"
    print(f"本地服务: {base}")
    failures: list[str] = []

    # 安全自检不依赖浏览器，先跑（即使未安装 playwright 也能验证暴露面）
    print("\n安全自检（本地服务暴露面）：")
    if not self_check(base):
        failures.append("http 暴露面自检")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        httpd.shutdown()
        print("\n跳过浏览器检查：未安装 playwright（pip install playwright）")
        if failures:
            return 1
        print("注意：页面渲染未经验证，退出码 2（不代表已通过）")
        return 2

    if take_shots:
        SHOT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = launch_browser(pw)
        context = browser.new_context(viewport={"width": 1440, "height": 900},
                                      device_scale_factor=1)
        for name in PAGES:
            page = context.new_page()
            errors: list[str] = []
            page.on("console", lambda m, e=errors: e.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
            page.on("pageerror", lambda exc, e=errors: e.append(f"pageerror: {exc}"))
            page.on("requestfailed", lambda req, e=errors: e.append(f"requestfailed: {req.url}"))

            page.goto(f"{base}/{name}", wait_until="load", timeout=30_000)
            # 分段滚动，触发所有图表的懒初始化
            height = page.evaluate("document.body.scrollHeight")
            step = 500
            y = 0
            while y < height:
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(90)
                y += step
                height = page.evaluate("document.body.scrollHeight")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(900)

            containers = page.eval_on_selector_all('[id^="chart-"]', "els => els.map(e => e.id)")
            rendered = page.eval_on_selector_all(
                '[id^="chart-"]', "els => els.filter(e => e.querySelector('canvas')).length"
            )
            empty = [c for c in containers if page.query_selector(f"#{c} canvas") is None]
            counts = page.evaluate(
                "() => ({imgs: document.images.length, "
                "brokenImgs: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).length})"
            )

            ok = not errors and not empty and counts["brokenImgs"] == 0
            status = "PASS" if ok else "FAIL"
            print(f"[{status}] {name:15s} 图表 {rendered}/{len(containers)} 渲染  "
                  f"console错误 {len(errors)}  破图 {counts['brokenImgs']}")
            if empty:
                print(f"        未渲染容器: {empty}")
            for e in errors[:8]:
                print(f"        {e}")
            if not ok:
                failures.append(name)

            if take_shots:
                page.screenshot(path=str(SHOT_DIR / f"{Path(name).stem}.png"), full_page=True)

            page.close()

        # ---- 额外验证：file:// 直接双击打开（用户最常见的打开方式） ----
        page = context.new_page()
        file_errors: list[str] = []
        page.on("console", lambda m, e=file_errors: e.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda exc, e=file_errors: e.append(f"pageerror: {exc}"))
        page.goto((ROOT / "index.html").as_uri(), wait_until="load", timeout=30_000)
        height = page.evaluate("document.body.scrollHeight")
        y = 0
        while y < height:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(90)
            y += 500
            height = page.evaluate("document.body.scrollHeight")
        page.wait_for_timeout(800)
        file_rendered = page.eval_on_selector_all('[id^="chart-"]', "els => els.filter(e => e.querySelector('canvas')).length")
        file_total = page.eval_on_selector_all('[id^="chart-"]', "els => els.length")
        ok = not file_errors and file_rendered == file_total and file_total > 0
        print(f"[{'PASS' if ok else 'FAIL'}] {'file:// index.html':15s} 图表 {file_rendered}/{file_total} 渲染  "
              f"console错误 {len(file_errors)}")
        for e in file_errors[:6]:
            print(f"        {e}")
        if not ok:
            failures.append("file://index.html")
        page.close()

        context.close()
        browser.close()

    httpd.shutdown()

    print()
    if failures:
        print(f"存在问题的页面: {failures}")
        return 1
    print("全部页面通过：无 JS 错误、图表全部渲染、无资源加载失败")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
