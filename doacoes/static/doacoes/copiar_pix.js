// Botão "Copiar chave" da doação em dinheiro (RF-17): copia a chave Pix e avisa no próprio botão.
// Se o navegador bloquear a cópia, seleciona a chave para a pessoa copiar na mão.
(function () {
  document.querySelectorAll('[data-copiar]').forEach(function (botao) {
    var original = botao.textContent;
    function avisar(texto) {
      botao.textContent = texto;
      setTimeout(function () { botao.textContent = original; }, 2500);
    }
    botao.addEventListener('click', function () {
      var chave = document.getElementById(botao.dataset.copiar);
      function selecionar() {
        var faixa = document.createRange();
        faixa.selectNodeContents(chave);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(faixa);
        avisar('Chave selecionada: copie com Ctrl+C');
      }
      if (!navigator.clipboard) { selecionar(); return; }
      navigator.clipboard.writeText(chave.textContent.trim()).then(function () { avisar('Chave copiada'); }, selecionar);
    });
  });
})();
