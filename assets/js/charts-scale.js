/* 产业规模页图表：核心产业规模 · 专利格局 · 东数西算地图 · 算力结构 */
(function () {
  "use strict";
  var P = window.PALETTE || {};
  var S = P.series || [], SOFT = P.soft || [];
  var T = window.T || function (zh) { return zh; };

  /* ---- 1. 核心产业规模 + 2030 目标 ---- */
  window.registerChart("chart-scale-core", function () {
    function bar(value, color, isTarget) {
      return {
        value: value,
        itemStyle: isTarget
          ? { color: "rgba(112,210,190,.22)", borderColor: S[3], borderWidth: 1.6, borderType: "dashed", borderRadius: [8, 8, 0, 0] }
          : {
              borderRadius: [8, 8, 0, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: color }, { offset: 1, color: color + "55" }
              ])
            },
        label: {
          show: true, position: "top", fontSize: 12,
          color: isTarget ? "#38819F" : "#6B7280",
          formatter: isTarget ? "{c}\n" + T("规划目标", "Target") : "{c}"
        }
      };
    }
    return {
      tooltip: { trigger: "axis", valueFormatter: function (v) { return v.toLocaleString("zh-CN") + " " + T("亿元", "100 mn yuan"); } },
      grid: { left: 8, right: 20, top: 46, bottom: 4, containLabel: true },
      xAxis: { type: "category", data: [T("2022 年", "2022"), T("2023 年", "2023"), T("2024 年", "2024"), T("2030 年", "2030")] },
      yAxis: { type: "value", name: T("亿元", "100 mn yuan"), max: 11500, nameTextStyle: { color: "#9CA3AF" } },
      series: [{
        type: "bar",
        barWidth: "42%",
        data: [
          bar(5080, S[4], false),
          bar(5784, S[5], false),
          bar(6000, S[6], false),
          bar(10000, null, true)
        ]
      }]
    };
  });

  /* ---- 2. 生成式 AI 专利格局 ---- */
  window.registerChart("chart-scale-patent", function () {
    var rows = [
      { name: T("中国", "China"), v: 38210, c: S[0] },
      { name: T("美国", "United States"), v: 6276, c: S[5] },
      { name: T("韩国", "South Korea"), v: 4155, c: S[6] },
      { name: T("日本", "Japan"), v: 3306, c: S[4] },
      { name: T("印度", "India"), v: 1350, c: S[3] }
    ];
    return {
      tooltip: {
        trigger: "axis", axisPointer: { type: "shadow" },
        valueFormatter: function (v) { return v.toLocaleString("zh-CN") + " " + T("件", "patents"); }
      },
      grid: { left: 8, right: 66, top: 20, bottom: 4, containLabel: true },
      xAxis: { type: "value", axisLabel: { formatter: function (v) { return v >= 10000 ? T(v / 10000 + " 万", v / 1000 + "k") : v; } } },
      yAxis: {
        type: "category",
        inverse: true,
        data: rows.map(function (r) { return r.name; })
      },
      series: [{
        type: "bar",
        barWidth: 18,
        data: rows.map(function (r) {
          return {
            value: r.v,
            itemStyle: {
              borderRadius: [0, 9, 9, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: r.c + "88" }, { offset: 1, color: r.c }
              ])
            }
          };
        }),
        label: {
          show: true, position: "right", color: "#6B7280", fontSize: 12,
          formatter: function (p) { return p.value.toLocaleString("zh-CN"); }
        }
      }]
    };
  });

  /* ---- 3. 东数西算 · 枢纽分布地图 ---- */
  window.registerChart("chart-scale-hubmap", function () {
    if (window.CHINA_GEOJSON && !echarts.getMap("china")) {
      echarts.registerMap("china", window.CHINA_GEOJSON);
    }
    // 语言切换会重跑本工厂：每次按当前语言重建节点名称（地图 geoJSON 的 nameMap 不受影响）
    var HUBS = [
      { short: T("京津冀", "Beijing-Tianjin-Hebei"), full: T("京津冀枢纽 · 张家口集群", "Beijing-Tianjin-Hebei Hub · Zhangjiakou Cluster"), coord: [114.88, 40.82] },
      { short: T("长三角", "Yangtze River Delta"), full: T("长三角枢纽 · 芜湖 / 长三角示范区集群", "Yangtze River Delta Hub · Wuhu / YRD Demonstration Zone Cluster"), coord: [118.43, 31.35] },
      { short: T("粤港澳", "Greater Bay Area"), full: T("粤港澳大湾区枢纽 · 韶关集群", "Guangdong-Hong Kong-Macao Greater Bay Area Hub · Shaoguan Cluster"), coord: [113.60, 24.80] },
      { short: T("成渝", "Chengdu-Chongqing"), full: T("成渝枢纽 · 天府 / 重庆集群", "Chengdu-Chongqing Hub · Tianfu / Chongqing Cluster"), coord: [104.07, 30.57] },
      { short: T("内蒙古", "Inner Mongolia"), full: T("内蒙古枢纽 · 和林格尔集群", "Inner Mongolia Hub · Helingeer Cluster"), coord: [111.75, 40.84] },
      { short: T("贵州", "Guizhou"), full: T("贵州枢纽 · 贵安集群", "Guizhou Hub · Gui'an Cluster"), coord: [106.63, 26.65] },
      { short: T("甘肃", "Gansu"), full: T("甘肃枢纽 · 庆阳集群", "Gansu Hub · Qingyang Cluster"), coord: [107.64, 35.71] },
      { short: T("宁夏", "Ningxia"), full: T("宁夏枢纽 · 中卫集群", "Ningxia Hub · Zhongwei Cluster"), coord: [105.19, 37.51] }
    ];
    var fullOf = {};
    HUBS.forEach(function (h) { fullOf[h.short] = h.full; });

    return {
      tooltip: {
        trigger: "item",
        formatter: function (p) {
          if (p.seriesType === "effectScatter") return "<b>" + (fullOf[p.name] || p.name) + "</b>";
          return p.name || "";
        }
      },
      geo: {
        map: "china",
        roam: false,
        zoom: 1.05,
        top: 12, bottom: 8,
        itemStyle: { areaColor: "#F4F6FA", borderColor: "#DEE3ED", borderWidth: 1 },
        emphasis: { itemStyle: { areaColor: "#ECF0F8" }, label: { show: false } },
        select: { disabled: true }
      },
      series: [{
        name: T("算力枢纽", "Computing hubs"),
        type: "effectScatter",
        coordinateSystem: "geo",
        showEffectOn: "render",
        rippleEffect: { scale: 3.6, brushType: "stroke", period: 4.6 },
        symbolSize: 10,
        label: {
          show: true, position: "right", distance: 8, color: "#5A6274", fontSize: 11.5,
          formatter: "{b}", textBorderColor: "#fff", textBorderWidth: 2
        },
        data: HUBS.map(function (h, i) {
          return {
            name: h.short,
            value: h.coord.concat([1]),
            itemStyle: {
              color: S[i % S.length],
              shadowBlur: 12,
              shadowColor: S[i % S.length],
              opacity: .95
            }
          };
        })
      }]
    };
  });

  /* ---- 4. 算力结构环形图 ---- */
  window.registerChart("chart-scale-compute", function () {
    return {
      tooltip: { trigger: "item", valueFormatter: function (v) { return v + " " + T("EFLOPS（约）", "EFLOPS (approx.)"); } },
      title: {
        text: "280",
        subtext: T("EFLOPS（约）", "EFLOPS (approx.)"),
        left: "50%", top: "38%", textAlign: "center",
        textStyle: { fontSize: 34, color: "#323A4D", fontWeight: 800 },
        subtextStyle: { fontSize: 12, color: "#9CA3AF" }
      },
      legend: { bottom: 0, left: "center" },
      series: [{
        type: "pie",
        radius: ["56%", "76%"],
        center: ["50%", "52%"],
        itemStyle: { borderColor: "#fff", borderWidth: 4, borderRadius: 10 },
        label: { formatter: "{b}\n{c} EFLOPS", color: "#6B7280", fontSize: 12, lineHeight: 18 },
        labelLine: { length: 12, length2: 10, lineStyle: { color: "#D7DBE4" } },
        data: [
          { value: 90, name: T("智能算力", "Intelligent computing power"), itemStyle: { color: S[5] } },
          { value: 190, name: T("通用算力", "General computing power"), itemStyle: { color: SOFT[6] } }
        ]
      }]
    };
  });
})();
