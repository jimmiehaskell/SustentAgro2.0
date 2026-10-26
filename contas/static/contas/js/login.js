(function () {
  const formulario = document.getElementById('form-login');
  const resultado = document.getElementById('resultado-login');
  let avisoTimer;

  // MOCK: trocar na camada 1 (BL-28) pelo envio à autenticação real.
  formulario.addEventListener('submit', function (evento) {
    evento.preventDefault();
    resultado.textContent = 'Demonstração: nenhum login foi realizado.';
    resultado.hidden = false;
    clearTimeout(avisoTimer);
    avisoTimer = setTimeout(function () { resultado.hidden = true; }, 3200);
  });
})();
