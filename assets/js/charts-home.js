/* 首页图表：生成式 AI 用户规模 · 全球 AI 支出 */
(function () {
  "use strict";
  var P = window.PALETTE || {};
  var S = P.series || [], SOFT = P.soft || [];

  function vGrad(c1, c2) {
    return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
      { offset: 0, color: c1 }, { offset: 1, color: c2 }
    ]);
  }

  /* ---- 生成式 AI 用户规模（柱） + 普及率（线） ---- */
  window.registerChart("chart-genai-users", function () {
    return {
      tooltip: { trigger: "axis", valueFormatter: function (v) { return v + (v > 100 ? window.T(" 亿美元", " 100 mn USD") : ""); } },
      legend: { top: 0, right: 4, data: [window.T("用户规模（亿人）", "Users (100 mn)"), window.T("普及率（%）", "Penetration (%)")] },
      grid: { left: 8, right: 12, top: 52, bottom: 4, containLabel: true },
      xAxis: { type: "category", data: ["2024.6", "2024.12", "2025.6"] },
      yAxis: [
        { type: "value", name: window.T("亿人", "100 mn people"), max: 6, nameTextStyle: { color: "#9CA3AF" } },
        { type: "value", name: window.T("普及率 %", "Penetration %"), max: 50, nameTextStyle: { color: "#9CA3AF" } }
      ],
      series: [
        {
          name: window.T("用户规模（亿人）", "Users (100 mn)"),
          type: "bar",
          data: [2.3, 2.49, 5.15],
          barWidth: "36%",
          itemStyle: { borderRadius: [10, 10, 0, 0], color: vGrad(S[4], SOFT[4]) },
          label: { show: true, position: "top", color: "#6B7280", fontSize: 12, formatter: window.T("{c} 亿", "{c} 100 mn") }
        },
        {
          name: window.T("普及率（%）", "Penetration (%)"),
          type: "line",
          yAxisIndex: 1,
          data: [16.4, 17.7, 36.5],
          smooth: true,
          symbolSize: 9,
          lineStyle: { width: 3, color: S[1] },
          itemStyle: { color: S[1], borderColor: "#fff", borderWidth: 2 },
          label: { show: true, position: "bottom", color: "#B4633F", fontSize: 12, formatter: "{c}%" }
        }
      ]
    };
  });

  /* ---- 全球 AI 支出 ---- */
  window.registerChart("chart-global-spend", function () {
    return {
      tooltip: {
        trigger: "axis",
        valueFormatter: function (v) { return v.toLocaleString("zh-CN") + window.T(" 亿美元", " 100 mn USD"); }
      },
      grid: { left: 8, right: 18, top: 40, bottom: 4, containLabel: true },
      xAxis: { type: "category", boundaryGap: false, data: ["2023", "2024", "2025E", "2028E"] },
      yAxis: { type: "value", name: window.T("亿美元", "100 mn USD"), nameTextStyle: { color: "#9CA3AF" } },
      series: [
        {
          name: window.T("全球 AI 支出", "Global AI spending"),
          type: "line",
          data: [1540, 2350, 3070, 6320],
          smooth: true,
          symbolSize: 9,
          lineStyle: { width: 3, color: S[6] },
          itemStyle: { color: S[6], borderColor: "#fff", borderWidth: 2 },
          areaStyle: { color: vGrad("rgba(152,112,210,.28)", "rgba(152,112,210,.02)") },
          label: { show: true, position: "top", color: "#6B7280", fontSize: 12 },
          markArea: {
            silent: true,
            itemStyle: { color: "rgba(112,136,210,.05)" },
            label: { show: true, position: "insideTop", color: "#9CA3AF", fontSize: 11, formatter: window.T("预测区间", "Forecast window") },
            data: [[{ xAxis: "2025E" }, { xAxis: "2028E" }]]
          }
        }
      ]
    };
  });
})();
