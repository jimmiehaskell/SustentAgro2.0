// Botão de tema: alterna entre claro e escuro e lembra a escolha (D-32)
(function () {
  var botao = document.getElementById('botao-tema');
  if (!botao) return;
  function atualizar() {
    var escuro = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    botao.textContent = escuro ? 'Tema claro' : 'Tema escuro';
  }
  botao.addEventListener('click', function () {
    var novo = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-bs-theme', novo);
    try { localStorage.setItem('tema', novo); } catch (e) {}
    atualizar();
  });
  atualizar();
})();
