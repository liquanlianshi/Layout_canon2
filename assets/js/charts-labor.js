/* 劳动力变革页图表：岗位瀑布图 · 技能重构环形 · 核心技能排名 */
(function () {
  "use strict";
  var P = window.PALETTE || {};
  var S = P.series || [], SOFT = P.soft || [], DEEP = P.deep || [];

  /* ---- 1. 岗位创造与替代（瀑布图，单位：百万人） ---- */
  window.registerChart("chart-labor-jobs", function () {
    var base = [0, -92, 0];
    var data = [
      { value: -92, itemStyle: { color: S[0], borderRadius: [0, 8, 8, 0] } },
      { value: 170, itemStyle: { color: S[3], borderRadius: [8, 8, 0, 0] } },
      { value: 78,  itemStyle: { color: S[5], borderRadius: [8, 8, 0, 0] } }
    ];
    var labelFmt = function (p) {
      if (p.value === 0) return "";
      return (p.value > 0 ? "+" : "") + p.value;
    };
    return {
      tooltip: {
        trigger: "axis",
        valueFormatter: function (v) { return (v > 0 ? "+" : "") + v + window.T(" 百万人", " mn people"); }
      },
      grid: { left: 8, right: 22, top: 46, bottom: 4, containLabel: true },
      xAxis: { type: "category", data: [window.T("被淘汰岗位", "Jobs displaced"), window.T("新增岗位", "Jobs created"), window.T("净变化", "Net change")] },
      yAxis: { type: "value", name: window.T("百万人", "mn people"), min: -110, max: 190, nameTextStyle: { color: "#9CA3AF" } },
      series: [
        {
          type: "bar", stack: "total", silent: true, barWidth: "38%",
          itemStyle: { color: "transparent" }, emphasis: { itemStyle: { color: "transparent" } },
          data: base, tooltip: { show: false }
        },
        {
          type: "bar", stack: "total", barWidth: "38%",
          data: data,
          label: {
            show: true, position: "top", color: "#4A5265", fontSize: 13, fontWeight: 700,
            formatter: function (p) {
              if (p.value === -92) { return "-92"; }
              return labelFmt(p);
            }
          },
          markLine: {
            silent: true, symbol: "none",
            lineStyle: { color: DEEP[5] || "#38519F", type: "dashed", width: 1.4 },
            label: { formatter: window.T("净增 7800 万", "Net gain 78 mn"), color: DEEP[5] || "#38519F", fontSize: 11, position: "insideEndTop" },
            data: [{ yAxis: 78 }]
          }
        }
      ]
    };
  });

  /* ---- 2. 技能重构环形 ---- */
  window.registerChart("chart-labor-skills", function () {
    return {
      tooltip: { trigger: "item", valueFormatter: function (v) { return v + "%"; } },
      title: {
        text: "39%",
        subtext: window.T("核心技能将被重构", "of core skills to be restructured"),
        left: "50%", top: "34%", textAlign: "center",
        textStyle: { fontSize: 40, color: "#323A4D", fontWeight: 800 },
        subtextStyle: { fontSize: 12.5, color: "#9CA3AF" }
      },
      legend: { bottom: 0, left: "center" },
      series: [{
        type: "pie",
        radius: ["58%", "78%"],
        center: ["50%", "48%"],
        itemStyle: { borderColor: "#fff", borderWidth: 4, borderRadius: 10 },
        label: { show: false },
        emphasis: { label: { show: false } },
        data: [
          { value: 39, name: window.T("将被重构的技能", "Skills to be restructured"), itemStyle: { color: S[1] } },
          { value: 61, name: window.T("保持稳定的技能", "Skills that stay stable"), itemStyle: { color: SOFT[6] } }
        ]
      }]
    };
  });

  /* ---- 3. 2030 核心技能 TOP8 ---- */
  window.registerChart("chart-labor-skillrank", function () {
    var skills = [
      { name: window.T("分析思维", "Analytical thinking"), rank: 1 },
      { name: window.T("韧性、灵活性与敏捷", "Resilience, flexibility and agility"), rank: 2 },
      { name: window.T("领导力与社会影响力", "Leadership and social influence"), rank: 3 },
      { name: window.T("创造性思维", "Creative thinking"), rank: 4 },
      { name: window.T("动机与自我意识", "Motivation and self-awareness"), rank: 5 },
      { name: window.T("技术素养", "Technological literacy"), rank: 6 },
      { name: window.T("同理心与主动倾听", "Empathy and active listening"), rank: 7 },
      { name: window.T("好奇心与终身学习", "Curiosity and lifelong learning"), rank: 8 }
    ];
    return {
      tooltip: {
        trigger: "axis", axisPointer: { type: "shadow" },
        formatter: function (ps) {
          var p = ps[0];
          return window.T("第 " + skills[p.dataIndex].rank + " 位 · ", "#" + skills[p.dataIndex].rank + " · ") + skills[p.dataIndex].name;
        }
      },
      grid: { left: 8, right: 46, top: 16, bottom: 4, containLabel: true },
      xAxis: { type: "value", show: false, max: 9 },
      yAxis: {
        type: "category", inverse: true,
        data: skills.map(function (s) { return s.name; }),
        axisLabel: { fontSize: 12 }
      },
      series: [{
        type: "bar",
        barWidth: 16,
        data: skills.map(function (s, i) {
          var c = S[i % S.length];
          return {
            value: 9 - s.rank,
            itemStyle: {
              borderRadius: [0, 9, 9, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: c + "66" }, { offset: 1, color: c }
              ])
            }
          };
        }),
        label: {
          show: true, position: "right", color: "#6B7280", fontSize: 12,
          formatter: function (p) { return "TOP " + skills[p.dataIndex].rank; }
        }
      }]
    };
  });
})();
