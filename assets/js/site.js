/* ==========================================================================
   全站共享脚本：导航、滚动动效、数字滚动、ECharts 统一主题与懒初始化
   ========================================================================== */
(function () {
  "use strict";

  /* ---------- 1. 导航：滚动状态 + 阅读进度 ---------- */
  var nav = document.querySelector(".nav");
  var bar = document.querySelector(".nav-progress");

  function onScroll() {
    var y = window.scrollY || document.documentElement.scrollTop;
    if (nav) nav.classList.toggle("scrolled", y > 8);
    if (bar) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (max > 0 ? Math.min(100, (y / max) * 100) : 0) + "%";
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- 2. 滚动进入动画 ---------- */
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var revealEls = document.querySelectorAll(".reveal");

  if (!("IntersectionObserver" in window) || reduceMotion) {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  } else {
    var revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); revealIO.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { revealIO.observe(el); });
  }

  /* ---------- 3. 数字滚动 ---------- */
  function formatNumber(v, decimals) {
    return v.toLocaleString("zh-CN", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    });
  }

  function runCounter(el) {
    var target = parseFloat(el.dataset.count);
    if (isNaN(target)) return;
    var decimals = parseInt(el.dataset.decimals || "0", 10);
    var dur = parseInt(el.dataset.duration || "1300", 10);
    var t0 = null;

    function tick(t) {
      if (t0 === null) t0 = t;
      var p = Math.min(1, (t - t0) / dur);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = formatNumber(target * eased, decimals);
      if (p < 1) requestAnimationFrame(tick);
      else el.textContent = formatNumber(target, decimals);
    }
    requestAnimationFrame(tick);
  }

  var counters = document.querySelectorAll("[data-count]");
  if (!("IntersectionObserver" in window) || reduceMotion) {
    counters.forEach(function (el) { el.textContent = formatNumber(parseFloat(el.dataset.count), parseInt(el.dataset.decimals || "0", 10)); });
  } else {
    var countIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { runCounter(e.target); countIO.unobserve(e.target); }
      });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { countIO.observe(el); });
  }

  /* ---------- 4. 表格进度条 ---------- */
  var bars = document.querySelectorAll(".bar-fill");
  if (bars.length) {
    var barIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          var el = e.target;
          el.style.width = el.dataset.pct + "%";
          barIO.unobserve(el);
        }
      });
    }, { threshold: 0.3 });
    bars.forEach(function (el) { barIO.observe(el); });
  }

  /* ---------- 5. ECharts 统一主题（多彩低饱和） ---------- */
  var INK = "#323A4D", INK2 = "#6B7280", INK3 = "#9CA3AF", LINE = "#E8EAF0";
  var FONT = '"PingFang SC","HarmonyOS Sans SC","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif';

  if (window.echarts) {
    echarts.registerTheme("aura", {
      color: (window.PALETTE || {}).series,
      textStyle: { fontFamily: FONT, color: INK },
      title: {
        textStyle: { color: INK, fontSize: 15, fontWeight: 700, fontFamily: FONT },
        subtextStyle: { color: INK3, fontSize: 12 }
      },
      legend: {
        textStyle: { color: INK2, fontSize: 12 },
        itemWidth: 12, itemHeight: 8, icon: "roundRect", itemGap: 14
      },
      tooltip: {
        backgroundColor: "rgba(255,255,255,.97)",
        borderColor: LINE, borderWidth: 1,
        padding: [10, 14],
        textStyle: { color: INK, fontSize: 12.5, fontFamily: FONT },
        extraCssText: "box-shadow:0 12px 32px rgba(50,58,77,.14);border-radius:12px;",
        axisPointer: { lineStyle: { color: "#D7DBE4" }, crossStyle: { color: "#D7DBE4" }, shadowStyle: { color: "rgba(112,136,210,.06)" } }
      },
      grid: { left: 8, right: 18, top: 46, bottom: 8, containLabel: true },
      categoryAxis: {
        axisLine: { lineStyle: { color: LINE } },
        axisTick: { show: false },
        axisLabel: { color: INK2, fontSize: 12 },
        splitLine: { show: false }
      },
      valueAxis: {
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: INK3, fontSize: 12 },
        splitLine: { lineStyle: { color: "#EFF1F5", type: [4, 5] } }
      },
      radar: {
        axisName: { color: INK2, fontSize: 12 },
        splitLine: { lineStyle: { color: "#EBEEF3" } },
        splitArea: { areaStyle: { color: ["#FFFFFF", "#FAFBFD"] } },
        axisLine: { lineStyle: { color: "#EBEEF3" } }
      },
      line: { symbolSize: 7, smooth: true, lineStyle: { width: 3 } },
      bar: { itemStyle: { borderRadius: [6, 6, 0, 0] } },
      pie: { itemStyle: { borderColor: "#fff", borderWidth: 3 }, label: { color: INK2 } }
    });
  }

  /* ---------- 6. 图表懒初始化（进入视口才渲染，滚动更流畅） ---------- */
  var charts = {};          // 已初始化的实例（语言切换后重绘用）
  var chartFactories = {};  // id -> optionFactory

  function initChart(id, optionFactory) {
    var el = document.getElementById(id);
    if (!el || !window.echarts) return;
    var inst = echarts.init(el, "aura", { renderer: "canvas" });
    inst.setOption(optionFactory());
    charts[id] = inst;

    // 图表内元素点击跳转（可选）
    el.addEventListener("click", function () { /* 预留 */ });
  }

  window.registerChart = function (id, optionFactory) {
    chartFactories[id] = optionFactory;   // 记住工厂：切换语言时按新语言重建 option
    if (!window.echarts) {
      document.addEventListener("DOMContentLoaded", function () { window.registerChart(id, optionFactory); });
      return;
    }
    var el = document.getElementById(id);
    if (!el) return;
    if (reduceMotion || !("IntersectionObserver" in window)) { initChart(id, optionFactory); return; }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { initChart(id, optionFactory); io.disconnect(); }
      });
    }, { rootMargin: "320px 0px", threshold: 0.01 });
    io.observe(el);
  };

  var resizeTimer = null;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      Object.keys(charts).forEach(function (k) { charts[k].resize(); });
    }, 160);
  });

  /* ---------- 7. 中英双语（中 / EN 切换，无刷新） ---------- */
  var LANG_KEY = "site-lang";
  window.SITE_LANG = localStorage.getItem(LANG_KEY) === "en" ? "en" : "zh";

  /** 图表等脚本里用：T("中文", "English") —— 在 factory 执行时按当前语言取值 */
  window.T = function (zh, en) {
    return window.SITE_LANG === "en" ? en : zh;
  };

  var zhText = new WeakMap();

  function applyI18n() {
    var isEn = window.SITE_LANG === "en";

    document.querySelectorAll("[data-en]").forEach(function (el) {
      if (!zhText.has(el)) zhText.set(el, el.textContent);
      el.textContent = isEn ? el.getAttribute("data-en") : zhText.get(el);
    });

    document.querySelectorAll("[data-en-aria]").forEach(function (el) {
      if (!el.dataset.zhAria) el.dataset.zhAria = el.getAttribute("aria-label") || "";
      el.setAttribute("aria-label", isEn ? el.getAttribute("data-en-aria") : el.dataset.zhAria);
    });

    var htmlEl = document.documentElement;
    if (htmlEl.dataset.enTitle) {
      if (!htmlEl.dataset.zhTitle) htmlEl.dataset.zhTitle = document.title;
      document.title = isEn ? htmlEl.dataset.enTitle : htmlEl.dataset.zhTitle;
    }

    var desc = document.querySelector('meta[name="description"]');
    if (desc && desc.getAttribute("data-en")) {
      if (!desc.dataset.zhContent) desc.dataset.zhContent = desc.getAttribute("content") || "";
      desc.setAttribute("content", isEn ? desc.getAttribute("data-en") : desc.dataset.zhContent);
    }

    htmlEl.lang = isEn ? "en" : "zh-CN";
  }

  /* 导航栏语言切换按钮：六个页面自动获得，无需改各页 HTML */
  (function buildLangToggle() {
    var host = document.querySelector(".nav-inner");
    if (!host) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "lang-toggle";
    var spanZh = document.createElement("span");
    spanZh.textContent = "中";
    var spanEn = document.createElement("span");
    spanEn.textContent = "EN";
    btn.appendChild(spanZh);
    btn.appendChild(spanEn);

    function markToggle() {
      var isEn = window.SITE_LANG === "en";
      spanZh.classList.toggle("on", !isEn);
      spanEn.classList.toggle("on", isEn);
      btn.setAttribute("aria-label", isEn ? "切换到中文" : "Switch to English");
    }

    btn.addEventListener("click", function () {
      window.SITE_LANG = window.SITE_LANG === "en" ? "zh" : "en";
      try { localStorage.setItem(LANG_KEY, window.SITE_LANG); } catch (e) { /* 隐私模式：忽略 */ }
      applyI18n();
      markToggle();
      window.dispatchEvent(new Event("site-lang-change"));
    });

    host.appendChild(btn);
    markToggle();
  })();

  /* 切换语言后，按新语言重建已初始化图表的 option（图表内文字也双语） */
  window.addEventListener("site-lang-change", function () {
    Object.keys(charts).forEach(function (id) {
      if (chartFactories[id]) charts[id].setOption(chartFactories[id](), true);
    });
  });

  applyI18n();

  /* ---------- 8. 页脚年份 ---------- */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();
})();
