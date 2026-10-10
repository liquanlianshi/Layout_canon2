/* Hero 主视觉：低饱和度神经网络粒子动画（Canvas，纯手写，无依赖）
   亮点：节点取自全站调色板，连线距离衰减，鼠标轻微视差，自动适配尺寸 */
(function () {
  "use strict";

  var canvas = document.getElementById("hero-canvas");
  if (!canvas) return;

  var ctx = canvas.getContext("2d");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var COLORS = ((window.PALETTE || {}).series) || ["#7088D2", "#70B6D2", "#70D2BE", "#D2AA70"];
  var DPR = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0;
  var nodes = [];
  var mouse = { x: -999, y: -999 };
  var raf = null;

  function resize() {
    var rect = canvas.getBoundingClientRect();
    W = Math.max(320, rect.width);
    H = Math.max(240, rect.height);
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    seed();
  }

  function seed() {
    var count = Math.round(Math.min(64, Math.max(26, (W * H) / 16000)));
    nodes = [];
    for (var i = 0; i < count; i++) {
      nodes.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.22,
        vy: (Math.random() - 0.5) * 0.22,
        r: 2.2 + Math.random() * 3.6,
        c: COLORS[i % COLORS.length],
        phase: Math.random() * Math.PI * 2
      });
    }
  }

  function hexToRgb(hex) {
    var h = hex.replace("#", "");
    if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    var n = parseInt(h, 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }

  function frame(t) {
    ctx.clearRect(0, 0, W, H);
    var MAX = Math.min(170, Math.max(110, W * 0.16));

    for (var i = 0; i < nodes.length; i++) {
      var a = nodes[i];
      a.x += a.vx; a.y += a.vy;
      if (a.x < -20) a.x = W + 20; if (a.x > W + 20) a.x = -20;
      if (a.y < -20) a.y = H + 20; if (a.y > H + 20) a.y = -20;

      var px = a.x + (mouse.x - W / 2) * 0.012;
      var py = a.y + (mouse.y - H / 2) * 0.012;

      for (var j = i + 1; j < nodes.length; j++) {
        var b = nodes[j];
        var dx = px - b.x, dy = py - b.y;
        var d = Math.sqrt(dx * dx + dy * dy);
        if (d < MAX) {
          var alpha = (1 - d / MAX) * 0.3;
          var ca = hexToRgb(a.c), cb = hexToRgb(b.c);
          var g = ctx.createLinearGradient(px, py, b.x, b.y);
          g.addColorStop(0, "rgba(" + ca.join(",") + "," + alpha.toFixed(3) + ")");
          g.addColorStop(1, "rgba(" + cb.join(",") + "," + alpha.toFixed(3) + ")");
          ctx.strokeStyle = g;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(px, py);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }

      var pulse = reduce ? 0.85 : 0.72 + Math.sin(t / 900 + a.phase) * 0.18;
      var rgb = hexToRgb(a.c);
      ctx.beginPath();
      ctx.arc(px, py, a.r * pulse, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(" + rgb.join(",") + ",.9)";
      ctx.fill();
      ctx.beginPath();
      ctx.arc(px, py, a.r * 2.6 * pulse, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(" + rgb.join(",") + ",.12)";
      ctx.fill();
    }

    if (!reduce) raf = requestAnimationFrame(frame);
  }

  window.addEventListener("resize", function () {
    cancelAnimationFrame(raf);
    resize();
    if (!reduce) raf = requestAnimationFrame(frame);
  });

  canvas.addEventListener("pointermove", function (e) {
    var rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  });
  canvas.addEventListener("pointerleave", function () { mouse.x = mouse.y = -999; });

  resize();
  raf = requestAnimationFrame(frame);
})();
