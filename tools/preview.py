# -*- coding: utf-8 -*-
"""本地预览服务：只暴露站点白名单文件，用于在浏览器中查看成品。

安全设计与 tools/check_pages.py 完全一致（复用同一份白名单判定 is_denied）：
  * 只绑定 127.0.0.1（仅本机可达）；
  * 只放行 5 个页面 + /assets/ + /vendor/ + favicon，其余路径一律 403
    —— .reasonix 附件、.pytest_cache、交付 zip 等均不可访问；
  * 校验 Host 头，抵御 DNS rebinding（恶意网页把域名解析到 127.0.0.1 后读取本机文件）。

用法：
  python tools/preview.py            # 默认端口 8080
  python tools/preview.py 9000       # 自定义端口
  浏览器访问 http://127.0.0.1:8080/ ，Ctrl+C 停止
"""
from __future__ import annotations

import functools
import http.server
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_pages import ROOT, QuietHandler  # noqa: E402  （同目录工具，复用白名单）

ALLOWED_HOSTS = {"127.0.0.1", "localhost"}


def host_allowed(raw_host: str | None) -> bool:
    """Host 头是否属于允许的本机名（防 DNS rebinding，纯函数便于测试）。

    大小写不敏感、忽略端口、空 Host 拒绝；IPv6 字面量（[::1]）会被拒绝 ——
    本服务仅绑定 IPv4 回环，无需放行。
    """
    host = (raw_host or "").strip().split(":")[0].strip().lower()
    return host in ALLOWED_HOSTS


class PreviewHandler(QuietHandler):
    """白名单服务 + Host 头校验（QuietHandler 已实现 is_denied 路径白名单）。"""

    def _host_ok(self) -> bool:
        return host_allowed(self.headers.get("Host"))

    def do_GET(self):  # noqa: N802
        if not self._host_ok():
            self.send_error(403, "host not allowed")
            return
        super().do_GET()

    def do_HEAD(self):  # noqa: N802
        if not self._host_ok():
            self.send_error(403, "host not allowed")
            return
        super().do_HEAD()


def main() -> int:
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"[FAIL] 端口参数不是数字：{sys.argv[1]!r}（用法：python tools/preview.py [端口]）")
            return 2
    else:
        port = 8080
    handler = functools.partial(PreviewHandler, directory=str(ROOT))
    try:
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError as exc:
        print(f"[FAIL] 无法绑定 127.0.0.1:{port}（端口被占用？）：{exc}")
        return 1

    print(f"预览服务已启动：http://127.0.0.1:{port}/")
    print("仅暴露站点白名单文件（5 个页面 + assets/ + vendor/），其余路径一律 403")
    print("按 Ctrl+C 停止")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n预览服务已停止")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
