(function () {
  const pagina = document.querySelector('.contribuicoes-pagina');
  const aviso = document.getElementById('aviso-contribuicoes');
  let avisoTimer;

  function mostrarAviso(texto) {
    aviso.textContent = texto;
    aviso.hidden = false;
    clearTimeout(avisoTimer);
    avisoTimer = setTimeout(function () { aviso.hidden = true; }, 3200);
  }

  // MOCK: trocar na camada 2 (BL-45) pelo cancelamento real da contribuição.
  pagina.querySelectorAll('[data-cancelar-contribuicao]').forEach(function (botao) {
    botao.addEventListener('click', function () {
      mostrarAviso('Simulação: contribuição cancelada apenas nesta tela. Nenhum registro foi alterado.');
    });
  });

  // MOCK: trocar na camada 3 (BL-48) pela ativação real do segundo perfil.
  const ativar = document.getElementById('ativar-agricultor');
  if (ativar) {
    ativar.addEventListener('click', function () {
      const selo = document.createElement('span');
      selo.className = 'selo selo-apoio';
      selo.id = 'perfil-agricultor-ativo';
      selo.textContent = 'Perfil de agricultor(a) ativo';
      ativar.replaceWith(selo);
      mostrarAviso('Simulação: perfil ativo apenas nesta tela. Nenhuma permissão foi alterada.');
    });
  }
})();
