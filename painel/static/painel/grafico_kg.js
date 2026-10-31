// Gráfico "Quilos recebidos por mês" do painel de impacto (RF-30, ADR-005).
// As cores vêm do sustentagro.css, e o gráfico se redesenha quando o tema muda.
(function () {
  var canvas = document.getElementById('grafico-kg');
  var dados = document.getElementById('dados-kg-por-mes');
  if (!canvas || !dados || typeof Chart === 'undefined') return;

  var linhas = JSON.parse(dados.textContent);
  var meses = linhas.map(function (linha) { return linha[0]; });
  var quilos = linhas.map(function (linha) { return linha[1]; });
  var formatar = new Intl.NumberFormat('pt-BR');

  function cor(nome) {
    return getComputedStyle(document.documentElement).getPropertyValue(nome).trim();
  }

  // A última barra é o mês em andamento e fica em limão, como no protótipo
  function coresDasBarras() {
    return quilos.map(function (_, i) { return i === quilos.length - 1 ? cor('--sa-limao') : cor('--sa-verde'); });
  }

  var grafico = new Chart(canvas, {
    type: 'bar',
    data: { labels: meses, datasets: [{ data: quilos, backgroundColor: coresDasBarras(), borderRadius: 4 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: function (item) { return formatar.format(item.raw) + ' kg'; } } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: cor('--bs-secondary-color') } },
        y: {
          beginAtZero: true,
          grid: { color: cor('--bs-border-color') },
          ticks: { color: cor('--bs-secondary-color'), callback: function (valor) { return formatar.format(valor); } },
        },
      },
    },
  });

  new MutationObserver(function () {
    grafico.data.datasets[0].backgroundColor = coresDasBarras();
    grafico.options.scales.x.ticks.color = cor('--bs-secondary-color');
    grafico.options.scales.y.ticks.color = cor('--bs-secondary-color');
    grafico.options.scales.y.grid.color = cor('--bs-border-color');
    grafico.update();
  }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-bs-theme'] });
})();
