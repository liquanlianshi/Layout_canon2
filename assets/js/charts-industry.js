/* 行业渗透页图表：渗透热力图 · 价值传导桑基图 · 效率实证 · 行业雷达 */
(function () {
  "use strict";
  var P = window.PALETTE || {};
  var S = P.series || [], SOFT = P.soft || [], DEEP = P.deep || [];
  var T = window.T || function (zh) { return zh; };

  /* ---- 1. 行业 × 环节 渗透热力图 ---- */
  window.registerChart("chart-ind-heatmap", function () {
    var industries = [
      T("制造业", "Manufacturing"), T("金融", "Finance"), T("医疗健康", "Healthcare"), T("零售电商", "Retail & e-commerce"),
      T("交通物流", "Transport & logistics"), T("教育", "Education"), T("政务民生", "Public services"), T("农业", "Agriculture")
    ];
    var stages = [
      T("研发设计", "R&D & design"), T("生产 / 服务", "Production & service"), T("营销销售", "Marketing & sales"),
      T("运营管理", "Operations"), T("客户服务", "Customer service")
    ];
    var matrix = [
      [55, 72, 35, 60, 42],
      [45, 70, 52, 65, 68],
      [48, 62, 20, 45, 58],
      [30, 55, 68, 58, 62],
      [42, 58, 18, 50, 40],
      [40, 55, 25, 38, 50],
      [25, 68, 12, 58, 66],
      [30, 45, 22, 28, 25]
    ];
    var data = [];
    matrix.forEach(function (row, y) {
      row.forEach(function (v, x) { data.push([x, y, v]); });
    });

    return {
      tooltip: {
        position: "top",
        formatter: function (p) {
          return industries[p.value[1]] + " · " + stages[p.value[0]] + "<br><b>" + T("渗透度 ", "penetration ") + p.value[2] + "</b>";
        }
      },
      grid: { left: 8, right: 20, top: 16, bottom: 66, containLabel: true },
      xAxis: {
        type: "category", data: stages, splitArea: { show: true },
        axisLabel: { color: "#6B7280", fontSize: 12 }
      },
      yAxis: {
        type: "category", data: industries, inverse: true, splitArea: { show: true },
        axisLabel: { color: "#6B7280", fontSize: 12 }
      },
      visualMap: {
        min: 0, max: 80,
        calculable: true,
        orient: "horizontal",
        left: "center", bottom: 0,
        itemWidth: 12, itemHeight: 120,
        textStyle: { color: "#9CA3AF", fontSize: 11 },
        inRange: { color: ["#F3F8FB", SOFT[4], S[4], DEEP[4]] }
      },
      series: [{
        type: "heatmap",
        data: data,
        label: { show: true, color: "#3A4256", fontSize: 11 },
        itemStyle: { borderColor: "#fff", borderWidth: 3, borderRadius: 6 },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: "rgba(56,129,159,.35)", borderColor: S[4], borderWidth: 2 }
        }
      }]
    };
  });

  /* ---- 2. 价值传导桑基图 ---- */
  window.registerChart("chart-ind-sankey", function () {
    var nodeEn = {
      "机器学习": "Machine learning",
      "计算机视觉": "Computer vision",
      "自然语言处理": "Natural language processing",
      "生成式 AI": "Generative AI",
      "智能质检与预测维护": "AI quality inspection & predictive maintenance",
      "影像与辅助诊断": "Imaging & assisted diagnosis",
      "智能客服": "AI customer service",
      "内容与代码生成": "Content & code generation",
      "降本": "Cost reduction",
      "提效": "Efficiency gains",
      "创新": "Innovation",
      "体验": "Experience"
    };
    function tn(zh) { return T(zh, nodeEn[zh] || zh); }

    var nodes = [
      { name: tn("机器学习") }, { name: tn("计算机视觉") }, { name: tn("自然语言处理") }, { name: tn("生成式 AI") },
      { name: tn("智能质检与预测维护") }, { name: tn("影像与辅助诊断") }, { name: tn("智能客服") }, { name: tn("内容与代码生成") },
      { name: tn("降本") }, { name: tn("提效") }, { name: tn("创新") }, { name: tn("体验") }
    ];
    var colorOf = {};
    nodes.forEach(function (n, i) { colorOf[n.name] = S[i % S.length]; });

    function L(s, t, v) { return { source: tn(s), target: tn(t), value: v, lineStyle: { color: "gradient", opacity: .34 } }; }

    return {
      tooltip: { trigger: "item", triggerOn: "mousemove" },
      series: [{
        type: "sankey",
        left: 4, right: 118, top: 12, bottom: 12,
        nodeWidth: 16,
        nodeGap: 12,
        emphasis: { focus: "adjacency" },
        nodeAlign: "justify",
        data: nodes.map(function (n) {
          return { name: n.name, itemStyle: { color: colorOf[n.name], borderWidth: 0, borderRadius: 4 } };
        }),
        label: { color: "#4A5265", fontSize: 12 },
        lineStyle: { curveness: .55 },
        links: [
          L("机器学习", "智能质检与预测维护", 30),
          L("计算机视觉", "智能质检与预测维护", 24),
          L("计算机视觉", "影像与辅助诊断", 20),
          L("自然语言处理", "智能客服", 26),
          L("生成式 AI", "内容与代码生成", 30),
          L("生成式 AI", "智能客服", 14),
          L("智能质检与预测维护", "降本", 34),
          L("智能质检与预测维护", "提效", 20),
          L("影像与辅助诊断", "提效", 12),
          L("影像与辅助诊断", "体验", 8),
          L("智能客服", "降本", 18),
          L("智能客服", "体验", 22),
          L("内容与代码生成", "提效", 20),
          L("内容与代码生成", "创新", 10)
        ]
      }]
    };
  });

  /* ---- 3. 效率实证 ---- */
  window.registerChart("chart-ind-efficiency", function () {
    var rows = [
      { name: T("客服 · 生产率提升", "Customer service · productivity gain"), v: 14.0, src: T("麦肯锡 2023", "McKinsey 2023"), c: S[2] },
      { name: T("知识工作 · 任务提速", "Knowledge work · faster tasks"), v: 25.1, src: "BCG 2023", c: S[4] },
      { name: T("编码 · 任务耗时缩短", "Coding · less time per task"), v: 55.8, src: "GitHub 2022", c: S[6] }
    ];
    return {
      tooltip: {
        trigger: "axis", axisPointer: { type: "shadow" },
        valueFormatter: function (v) { return v + "%"; }
      },
      grid: { left: 8, right: 70, top: 20, bottom: 4, containLabel: true },
      xAxis: { type: "value", max: 65, axisLabel: { formatter: "{value}%" } },
      yAxis: { type: "category", data: rows.map(function (r) { return r.name; }), axisLabel: { fontSize: 12 } },
      series: [{
        type: "bar",
        barWidth: 20,
        data: rows.map(function (r) {
          return {
            value: r.v,
            itemStyle: {
              borderRadius: [0, 10, 10, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: r.c + "77" }, { offset: 1, color: r.c }
              ])
            }
          };
        }),
        label: {
          show: true, position: "right", color: "#6B7280", fontSize: 12,
          formatter: function (p) { return p.value + "%  ·  " + rows[p.dataIndex].src; }
        }
      }]
    };
  });

  /* ---- 4. 行业成熟度雷达 ---- */
  window.registerChart("chart-ind-radar", function () {
    var dims = [
      T("渗透广度", "Penetration breadth"), T("应用深度", "Application depth"),
      T("价值实现", "Value realisation"), T("数据基础", "Data foundation")
    ];
    var rows = [
      { name: T("制造业", "Manufacturing"), v: [80, 72, 75, 78], c: S[3] },
      { name: T("金融", "Finance"), v: [72, 68, 70, 85], c: S[5] },
      { name: T("医疗健康", "Healthcare"), v: [58, 62, 60, 65], c: S[1] },
      { name: T("农业", "Agriculture"), v: [35, 30, 32, 38], c: S[2] }
    ];
    return {
      tooltip: {},
      legend: { bottom: 0, data: rows.map(function (r) { return r.name; }) },
      radar: {
        indicator: dims.map(function (d) { return { name: d, max: 100 }; }),
        radius: "62%",
        center: ["50%", "46%"],
        splitNumber: 4
      },
      series: [{
        type: "radar",
        symbolSize: 6,
        data: rows.map(function (r) {
          return {
            name: r.name,
            value: r.v,
            lineStyle: { width: 2.4, color: r.c },
            itemStyle: { color: r.c },
            areaStyle: { color: r.c, opacity: .16 }
          };
        })
      }]
    };
  });

  /* ---- 5. 落地场景热度词云 ---- */
  window.registerChart("chart-ind-wordcloud", function () {
    var words = [
      [T("智能质检", "AI quality inspection"), 100], [T("智能客服", "AI customer service"), 96], [T("内容生成", "Content generation"), 93], [T("预测性维护", "Predictive maintenance"), 88],
      [T("代码助手", "Coding copilots"), 86], [T("智能风控", "AI risk control"), 84], [T("医学影像分析", "Medical imaging analysis"), 80], [T("供应链优化", "Supply-chain optimisation"), 70],
      [T("自动驾驶", "Autonomous driving"), 68], [T("数字人直播", "Digital-human livestreaming"), 62], [T("智能排产", "Smart scheduling"), 58], [T("智能巡检", "Smart inspection"), 56],
      [T("智慧课堂", "Smart classrooms"), 52], [T("AI 制药", "AI drug discovery"), 48], [T("遥感解译", "Remote-sensing interpretation"), 42], [T("智慧育种", "Smart breeding"), 34]
    ];
    return {
      tooltip: {
        formatter: function (p) { return "<b>" + p.name + "</b><br>" + T("相对热度 ", "relative buzz ") + p.value; }
      },
      series: [{
        type: "wordCloud",
        shape: "circle",
        left: "center", top: "center",
        width: "96%", height: "92%",
        sizeRange: [13, 46],
        rotationRange: [-18, 18],
        rotationStep: 18,
        gridSize: 14,
        drawOutOfBound: false,
        textStyle: { fontFamily: '"PingFang SC","Microsoft YaHei",sans-serif', fontWeight: 700 },
        emphasis: { textStyle: { shadowBlur: 8, shadowColor: "rgba(50,58,77,.25)" } },
        data: words.map(function (w, i) {
          return { name: w[0], value: w[1], textStyle: { color: S[i % S.length] } };
        })
      }]
    };
  });
})();
