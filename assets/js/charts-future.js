/* 未来展望页图表：技术扩散 S 曲线 · 2030 目标仪表盘 · 成熟度象限散点 */
(function () {
  "use strict";
  var P = window.PALETTE || {};
  var S = P.series || [], SOFT = P.soft || [], DEEP = P.deep || [];

  /* ---- 1. S 型技术扩散曲线（示意） ---- */
  window.registerChart("chart-future-scurve", function () {
    var years = ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030"];
    var curve = [1, 2, 3, 5, 8, 13, 22, 31, 42, 54, 65, 75, 83, 89];
    var marks = [
      { coord: ["2017", 1], name: "规划发布" },
      { coord: ["2022", 13], name: "生成式 AI 引爆" },
      { coord: ["2025", 42], name: "当前位置 · 加速期" },
      { coord: ["2030", 89], name: "规模化期" }
    ];
    return {
      tooltip: {
        trigger: "axis",
        valueFormatter: function (v) { return "采用率约 " + v + "%（示意）"; }
      },
      grid: { left: 8, right: 30, top: 46, bottom: 4, containLabel: true },
      xAxis: { type: "category", boundaryGap: false, data: years },
      yAxis: { type: "value", name: "采用率 %", max: 100, nameTextStyle: { color: "#9CA3AF" } },
      series: [{
        type: "line",
        data: curve,
        smooth: true,
        symbolSize: 6,
        lineStyle: { width: 3.4, color: S[6] },
        itemStyle: { color: S[6], borderColor: "#fff", borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(152,112,210,.30)" },
            { offset: 1, color: "rgba(152,112,210,.02)" }
          ])
        },
        markArea: {
          silent: true,
          itemStyle: { color: "rgba(152,112,210,.07)" },
          label: { show: true, position: "insideTop", color: DEEP[6] || "#63389F", fontSize: 11, formatter: "加速期" },
          data: [[{ xAxis: "2025" }, { xAxis: "2030" }]]
        },
        markPoint: {
          symbol: "pin",
          symbolSize: 42,
          itemStyle: { color: "#fff", borderColor: S[6], borderWidth: 1.6 },
          label: { color: "#4A5265", fontSize: 10.5, lineHeight: 13, formatter: function (p) { return p.name; } },
          data: marks.map(function (m) {
            return { coord: m.coord, name: m.name, value: "" };
          })
        }
      }]
    };
  });

  /* ---- 2. 2030 目标完成度仪表盘 ---- */
  window.registerChart("chart-future-goal", function () {
    return {
      tooltip: { show: false },
      series: [{
        type: "gauge",
        startAngle: 215,
        endAngle: -35,
        min: 0,
        max: 100,
        radius: "96%",
        center: ["50%", "58%"],
        progress: {
          show: true, width: 18, roundCap: true,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: SOFT[4] }, { offset: 1, color: S[4] }
            ])
          }
        },
        axisLine: { roundCap: true, lineStyle: { width: 18, color: [[1, "#EEF1F6"]] } },
        pointer: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        anchor: { show: false },
        title: { show: true, offsetCenter: [0, "30%"], fontSize: 12.5, color: "#9CA3AF" },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, "-2%"],
          formatter: function (v) { return Math.round(v) + "%"; },
          fontSize: 40,
          fontWeight: 800,
          color: "#323A4D"
        },
        data: [{ value: 60, name: "2024 年规模 ÷ 2030 年目标" }]
      }]
    };
  });

  /* ---- 3. 成熟度 × 采纳度 象限散点 ---- */
  window.registerChart("chart-future-techquad", function () {
    var pts = [
      { name: "智能客服", v: [86, 82], c: S[5], pos: "left" },
      { name: "AI 编程助手", v: [80, 70], c: S[6], pos: "bottom" },
      { name: "医学影像诊断", v: [72, 50], c: S[1], pos: "bottom" },
      { name: "智能驾驶（L2+）", v: [64, 46], c: S[4], pos: "left" },
      { name: "智慧教育", v: [56, 42], c: S[7], pos: "top" },
      { name: "AI 制药", v: [46, 26], c: S[3], pos: "right" },
      { name: "人形机器人", v: [32, 16], c: S[0], pos: "right" }
    ];
    return {
      tooltip: {
        trigger: "item",
        formatter: function (p) {
          var zone = p.value[0] >= 50 && p.value[1] >= 50 ? "规模化落地期"
            : p.value[0] >= 50 ? "技术就绪 · 待采纳"
            : "培育 / 萌芽期";
          return "<b>" + p.name + "</b><br>成熟度 " + p.value[0] + " · 采纳度 " + p.value[1] + "<br>" + zone;
        }
      },
      grid: { left: 10, right: 34, top: 30, bottom: 12, containLabel: true },
      xAxis: {
        type: "value", min: 0, max: 100, name: "技术成熟度 →",
        nameLocation: "middle", nameGap: 28, nameTextStyle: { color: "#9CA3AF", fontSize: 12 }
      },
      yAxis: {
        type: "value", min: 0, max: 100, name: "社会采纳度 →",
        nameTextStyle: { color: "#9CA3AF", fontSize: 12 }
      },
      series: [{
        type: "scatter",
        symbolSize: 20,
        data: pts.map(function (p) {
          return {
            name: p.name,
            value: p.v,
            itemStyle: {
              color: p.c, opacity: .9,
              borderColor: "#fff", borderWidth: 2,
              shadowBlur: 10, shadowColor: p.c + "66"
            },
            label: {
              show: true, position: p.pos, formatter: p.name,
              color: "#4A5265", fontSize: 12,
              textBorderColor: "#fff", textBorderWidth: 3
            }
          };
        }),
        markLine: {
          silent: true, symbol: "none",
          lineStyle: { color: "#DDE2EC", type: "dashed", width: 1.2 },
          label: { show: false },
          data: [{ xAxis: 50 }, { yAxis: 50 }]
        },
        markArea: {
          silent: true,
          data: [
            [
              { xAxis: 50, yAxis: 50, itemStyle: { color: "rgba(112,182,210,.12)" },
                label: { show: true, position: "insideTopRight", color: "#5B93AC", fontSize: 11.5, formatter: "规模化落地期" } },
              { xAxis: 100, yAxis: 100 }
            ],
            [
              { xAxis: 50, yAxis: 0, itemStyle: { color: "rgba(112,210,190,.10)" },
                label: { show: true, position: "insideBottomRight", color: "#4E9E8C", fontSize: 11.5, formatter: "技术就绪 · 待采纳" } },
              { xAxis: 100, yAxis: 50 }
            ],
            [
              { xAxis: 0, yAxis: 0, itemStyle: { color: "rgba(210,170,112,.09)" },
                label: { show: true, position: "insideBottomLeft", color: "#A5824C", fontSize: 11.5, formatter: "培育 / 萌芽期" } },
              { xAxis: 50, yAxis: 50 }
            ],
            [
              { xAxis: 0, yAxis: 50, itemStyle: { color: "rgba(197,112,210,.07)" },
                label: { show: true, position: "insideTopLeft", color: "#A05AAF", fontSize: 11.5, formatter: "早期探索期" } },
              { xAxis: 50, yAxis: 100 }
            ]
          ]
        }
      }]
    };
  });
})();
