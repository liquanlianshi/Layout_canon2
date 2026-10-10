/* 社会影响页图表：就业与收入 · 日常生活 · 区域协调 · 绿色低碳（共 11 组数据图形） */
(function () {
  "use strict";
  var P = window.PALETTE || {};
  var S = P.series || [], SOFT = P.soft || [], DEEP = P.deep || [];

  function areaGrad(hex, top) {
    return new window.echarts.graphic.LinearGradient(0, 0, 0, 1, [
      { offset: 0, color: "rgba(" + hex + "," + (top || 0.42) + ")" },
      { offset: 1, color: "rgba(" + hex + ",0)" }
    ]);
  }
  function rgb(c, a) {
    var n = parseInt(c.slice(1), 16);
    return [n >> 16 & 255, n >> 8 & 255, n & 255].join(",");
  }

  /* ================= 01 就业与收入 ================= */

  /* ---- 1. 城乡居民人均可支配收入与收入比 ---- */
  window.registerChart("chart-soc-income", function () {
    var years = ["2019", "2020", "2021", "2022", "2023", "2024"];
    return {
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      legend: { top: 0, data: ["城镇居民", "农村居民", "城乡收入比"] },
      grid: { left: 8, right: 12, top: 52, bottom: 8, containLabel: true },
      xAxis: { type: "category", data: years },
      yAxis: [
        { type: "value", name: "元 / 人", nameTextStyle: { color: "#9CA3AF", fontSize: 11 } },
        { type: "value", name: "收入比（倍）", min: 2.0, max: 3.0, nameTextStyle: { color: "#9CA3AF", fontSize: 11 } }
      ],
      series: [
        {
          name: "城镇居民", type: "bar", barWidth: 20, barGap: "18%",
          itemStyle: { color: S[5], borderRadius: [6, 6, 0, 0] },
          data: [42359, 43834, 47412, 49283, 51821, 54188]
        },
        {
          name: "农村居民", type: "bar", barWidth: 20,
          itemStyle: { color: S[3], borderRadius: [6, 6, 0, 0] },
          data: [16021, 17131, 18931, 20133, 21691, 23119]
        },
        {
          name: "城乡收入比", type: "line", yAxisIndex: 1, symbolSize: 9,
          itemStyle: { color: S[1] }, lineStyle: { width: 3, color: S[1] },
          data: [2.64, 2.56, 2.50, 2.45, 2.39, 2.34],
          markPoint: {
            symbolSize: 0,
            label: { color: DEEP[1], fontSize: 12, fontWeight: 700, formatter: "2.64 → 2.34 倍" },
            data: [{ coord: ["2019", 2.64], label: { offset: [10, -18] } }]
          }
        }
      ]
    };
  });

  /* ---- 2. 城镇新增就业 ---- */
  window.registerChart("chart-soc-jobs", function () {
    var years = ["2019", "2020", "2021", "2022", "2023", "2024"];
    var vals = [1352, 1186, 1269, 1206, 1244, 1256];
    return {
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: "{b} 年<br>新增就业 <b>{c} 万人</b>" },
      grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true },
      xAxis: { type: "category", data: years },
      yAxis: { type: "value", name: "万人", min: 1000, nameTextStyle: { color: "#9CA3AF", fontSize: 11 } },
      series: [{
        type: "bar", barWidth: 26,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new window.echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: S[4] }, { offset: 1, color: SOFT[4] }
          ])
        },
        label: { show: true, position: "top", color: "#6B7280", fontSize: 11.5 },
        data: vals,
        markLine: {
          symbol: "none", silent: true,
          lineStyle: { color: "#C9CEDB", type: "dashed" },
          label: { formatter: "年均约 1252 万", color: "#9CA3AF", fontSize: 11, position: "insideEndTop" },
          data: [{ yAxis: 1252 }]
        }
      }]
    };
  });

  /* ================= 02 日常生活 ================= */

  /* ---- 3. 全国网上零售额 ---- */
  window.registerChart("chart-soc-retail", function () {
    var years = ["2019", "2020", "2021", "2022", "2023", "2024"];
    var vals = [10.63, 11.76, 13.09, 13.79, 15.42, 15.52];
    return {
      tooltip: { trigger: "axis", formatter: "{b} 年<br>网上零售额 <b>{c} 万亿元</b>" },
      grid: { left: 8, right: 20, top: 40, bottom: 8, containLabel: true },
      xAxis: { type: "category", data: years, boundaryGap: false },
      yAxis: { type: "value", name: "万亿元", min: 9, nameTextStyle: { color: "#9CA3AF", fontSize: 11 } },
      series: [{
        type: "line", smooth: true, symbolSize: 9,
        itemStyle: { color: S[4] }, lineStyle: { width: 3.5, color: S[4] },
        areaStyle: { color: areaGrad(rgb(S[4]), 0.42) },
        label: { show: true, position: "top", color: DEEP[4], fontSize: 11.5, fontWeight: 700 },
        data: vals
      }]
    };
  });

  /* ---- 4. 移动支付普及率 ---- */
  window.registerChart("chart-soc-pay", function () {
    return {
      series: [{
        type: "gauge", startAngle: 210, endAngle: -30, min: 0, max: 100,
        radius: "92%", center: ["50%", "58%"],
        progress: { show: true, width: 20, roundCap: true, itemStyle: { color: S[2] } },
        axisLine: { lineStyle: { width: 20, color: [[1, "#EFF1F5"]] } },
        axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false }, pointer: { show: false },
        anchor: { show: false },
        detail: {
          valueAnimation: true, offsetCenter: [0, "6%"],
          formatter: "{value}%", fontSize: 40, fontWeight: 800, color: DEEP[2]
        },
        title: { offsetCenter: [0, "42%"], color: "#9CA3AF", fontSize: 12 },
        data: [{ value: 86, name: "普及率（居全球第一）" }]
      }]
    };
  });

  /* ---- 5. 生成式 AI 用户规模 ---- */
  window.registerChart("chart-soc-genai", function () {
    var labels = ["2024.06", "2024.12", "2025.06"];
    var vals = [2.30, 2.49, 5.15];
    return {
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: "{b}<br>用户规模 <b>{c} 亿人</b>" },
      grid: { left: 8, right: 24, top: 40, bottom: 8, containLabel: true },
      xAxis: { type: "category", data: labels },
      yAxis: { type: "value", name: "亿人", nameTextStyle: { color: "#9CA3AF", fontSize: 11 } },
      series: [{
        type: "bar", barWidth: 62,
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: function (p) { return [SOFT[7], SOFT[6], S[7]][p.dataIndex]; }
        },
        label: { show: true, position: "top", fontWeight: 700, color: "#6B7280" },
        data: vals,
        markPoint: {
          symbol: "roundRect", symbolSize: [168, 30], symbolOffset: [0, -46],
          itemStyle: { color: DEEP[7] },
          label: { color: "#fff", fontSize: 12, fontWeight: 700, formatter: "2024.06→2025.06：+124%" },
          data: [{ coord: [2, 5.15] }]
        }
      }]
    };
  });

  /* ================= 03 区域协调 ================= */

  /* ---- 6. 城乡互联网普及率 ---- */
  window.registerChart("chart-soc-gap", function () {
    return {
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: "{b}<br>互联网普及率 <b>{c}%</b>" },
      grid: { left: 8, right: 56, top: 30, bottom: 8, containLabel: true },
      xAxis: { type: "value", max: 100, name: "%", nameTextStyle: { color: "#9CA3AF", fontSize: 11 } },
      yAxis: { type: "category", data: ["农村", "城镇"] },
      series: [{
        type: "bar", barWidth: 34,
        itemStyle: {
          borderRadius: [0, 8, 8, 0],
          color: function (p) { return p.dataIndex === 1 ? S[5] : S[3]; }
        },
        label: { show: true, position: "right", formatter: "{c}%", color: "#6B7280", fontWeight: 700 },
        data: [67.4, 85.3],
        markLine: {
          symbol: ["none", "none"], silent: true,
          lineStyle: { color: DEEP[0], type: "dashed", width: 1.5 },
          label: { formatter: "差距 17.9 个百分点", color: DEEP[0], fontSize: 11.5, position: "middle" },
          data: [{ type: "average" }]
        }
      }]
    };
  });

  /* ---- 7. 农村网络零售额 ---- */
  window.registerChart("chart-soc-rural", function () {
    var years = ["2020", "2021", "2022", "2023", "2024"];
    return {
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: "{b} 年<br>农村网络零售额 <b>{c} 万亿元</b>" },
      grid: { left: 8, right: 16, top: 34, bottom: 8, containLabel: true },
      xAxis: { type: "category", data: years },
      yAxis: { type: "value", name: "万亿元", min: 1.5, nameTextStyle: { color: "#9CA3AF", fontSize: 11 } },
      series: [{
        type: "bar", barWidth: 28,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new window.echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: S[3] }, { offset: 1, color: SOFT[3] }
          ])
        },
        label: { show: true, position: "top", color: "#6B7280", fontSize: 11.5 },
        data: [1.79, 2.05, 2.17, 2.49, 2.56]
      }]
    };
  });

  /* ---- 8. 数字乡村基础设施 ---- */
  window.registerChart("chart-soc-village", function () {
    var items = ["农村互联网普及率（CNNIC）", "行政村通 5G（工信部）", "行政村通宽带（工信部）"];
    var vals = [67.4, 80, 100];
    return {
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: "{b}<br><b>{c}%</b>" },
      grid: { left: 8, right: 62, top: 26, bottom: 8, containLabel: true },
      xAxis: { type: "value", max: 100, name: "%", nameTextStyle: { color: "#9CA3AF", fontSize: 11 } },
      yAxis: { type: "category", data: items, axisLabel: { color: "#6B7280", fontSize: 12 } },
      series: [{
        type: "bar", barWidth: 22,
        itemStyle: {
          borderRadius: [0, 8, 8, 0],
          color: function (p) { return [S[2], S[6], S[3]][p.dataIndex]; }
        },
        label: { show: true, position: "right", formatter: "{c}%", color: "#6B7280", fontWeight: 700 },
        data: vals
      }]
    };
  });

  /* ================= 04 绿色低碳 ================= */

  /* ---- 9. 新能源汽车产量 ---- */
  window.registerChart("chart-soc-ev", function () {
    var years = ["2019", "2020", "2021", "2022", "2023", "2024"];
    var vals = [124.2, 136.6, 354.5, 705.8, 958.7, 1288.8];
    return {
      tooltip: { trigger: "axis", formatter: "{b} 年<br>产量 <b>{c} 万辆</b>" },
      grid: { left: 8, right: 20, top: 46, bottom: 8, containLabel: true },
      xAxis: { type: "category", data: years, boundaryGap: false },
      yAxis: { type: "value", name: "万辆", nameTextStyle: { color: "#9CA3AF", fontSize: 11 } },
      series: [{
        type: "line", smooth: true, symbolSize: 9,
        itemStyle: { color: S[3] }, lineStyle: { width: 3.5, color: S[3] },
        areaStyle: { color: areaGrad(rgb(S[3]), 0.45) },
        label: { show: true, position: "top", color: DEEP[3], fontSize: 11.5, fontWeight: 700 },
        data: vals,
        markArea: {
          silent: true,
          itemStyle: { color: "rgba(112,210,190,.10)" },
          label: { show: true, position: "insideTop", color: DEEP[3], fontSize: 11.5, formatter: "2021 年：规模化提速" },
          data: [[{ xAxis: "2021" }, { xAxis: "2024" }]]
        }
      }]
    };
  });

  /* ---- 10. 数据中心 PUE ---- */
  window.registerChart("chart-soc-pue", function () {
    var items = ["传统数据中心", "政策目标（2025）", "先进水平"];
    var vals = [1.50, 1.30, 1.25];
    return {
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: "{b}<br>PUE <b>{c}</b>" },
      grid: { left: 8, right: 20, top: 34, bottom: 8, containLabel: true },
      xAxis: { type: "category", data: items, axisLabel: { color: "#6B7280", fontSize: 12 } },
      yAxis: { type: "value", min: 1.0, max: 1.6, name: "PUE", nameTextStyle: { color: "#9CA3AF", fontSize: 11 } },
      series: [{
        type: "bar", barWidth: 54,
        itemStyle: { borderRadius: [8, 8, 0, 0], color: function (p) { return [S[0], S[2], S[3]][p.dataIndex]; } },
        label: { show: true, position: "top", formatter: "{c}", color: "#6B7280", fontWeight: 700 },
        data: vals,
        markLine: {
          symbol: "none", silent: true,
          lineStyle: { color: "#C9CEDB", type: "dashed" },
          label: { formatter: "政策上限 1.30", color: "#9CA3AF", fontSize: 11, position: "insideEndTop" },
          data: [{ yAxis: 1.30 }]
        }
      }]
    };
  });

  /* ---- 11. 可再生能源发电装机占比 ---- */
  window.registerChart("chart-soc-renew", function () {
    return {
      tooltip: { trigger: "item", formatter: "{b}<br>占比 <b>{c}%</b>" },
      title: {
        text: "56%", subtext: "可再生能源 · 14.5 亿千瓦",
        left: "50%", top: "36%", textAlign: "center",
        textStyle: { fontSize: 34, fontWeight: 800, color: DEEP[3] },
        subtextStyle: { color: "#9CA3AF", fontSize: 12 }
      },
      series: [{
        type: "pie", radius: ["58%", "80%"], center: ["50%", "50%"],
        avoidLabelOverlap: true, label: { show: false }, labelLine: { show: false },
        itemStyle: { borderColor: "#fff", borderWidth: 3 },
        data: [
          { name: "可再生能源发电装机", value: 56, itemStyle: { color: S[3] } },
          { name: "其他电源装机", value: 44, itemStyle: { color: "#EDF0F5" } }
        ]
      }]
    };
  });
})();
