(function () {
  let pagina = document.querySelector('.cadastro-pagina');
  let avisoTimer;
  let trocandoPerfil = false;

  // Demonstração do estado de erro previsto no protótipo, sem consulta externa.
  function cnpjValido(valor) {
    const cnpj = String(valor).replace(/\D/g, '');
    if (cnpj.length !== 14 || /^(\d)\1+$/.test(cnpj)) return false;
    function digito(tamanho) {
      const pesos = tamanho === 12
        ? [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        : [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
      const resto = pesos.reduce((soma, peso, i) => soma + peso * Number(cnpj[i]), 0) % 11;
      return resto < 2 ? 0 : 11 - resto;
    }
    return digito(12) === Number(cnpj[12]) && digito(13) === Number(cnpj[13]);
  }

  // MOCK: trocar na camada 1 pelo envio aos formulários de cadastro (BL-28, BL-29).
  function simularCadastro(evento) {
    evento.preventDefault();
    if (!pagina.querySelector('#form-cadastro').reportValidity()) return;
    const cnpj = pagina.querySelector('#cad-cnpj');
    if (cnpj) {
      const ajuda = pagina.querySelector('#cad-cnpj-msg');
      if (!cnpjValido(cnpj.value)) {
        ajuda.className = 'erro';
        ajuda.textContent = 'CNPJ inválido: os dígitos verificadores não conferem. Confira o número no cartão do CNPJ.';
        cnpj.setAttribute('aria-invalid', 'true');
        cnpj.focus();
        return;
      }
      cnpj.removeAttribute('aria-invalid');
      ajuda.className = 'ajuda';
      ajuda.textContent = 'Confira os 14 dígitos. Teste um número errado para ver o aviso.';
    }
    const resultado = pagina.querySelector('#resultado-cadastro');
    resultado.textContent = 'Simulação concluída. Nenhuma conta foi criada e nenhum dado foi salvo.';
    resultado.hidden = false;
    clearTimeout(avisoTimer);
    avisoTimer = setTimeout(() => { resultado.hidden = true; }, 3200);
  }

  async function trocarPerfil(evento) {
    evento.preventDefault();
    if (trocandoPerfil) return;
    trocandoPerfil = true;
    const destino = evento.currentTarget.action;
    try {
      // O servidor continua responsável pelo HTML; a troca não desloca a página.
      const resposta = await fetch(destino);
      if (!resposta.ok) throw new Error('Não foi possível carregar o perfil.');
      const documento = new DOMParser().parseFromString(await resposta.text(), 'text/html');
      const novaPagina = documento.querySelector('.cadastro-pagina');
      if (!novaPagina) throw new Error('Formulário não encontrado.');
      clearTimeout(avisoTimer);
      pagina.replaceWith(novaPagina);
      pagina = novaPagina;
      history.replaceState(null, '', destino);
      prepararPagina();
      pagina.querySelector('[aria-pressed="true"]').focus({ preventScroll: true });
    } catch (erro) {
      window.location.assign(destino);
    } finally {
      trocandoPerfil = false;
    }
  }

  function prepararPagina() {
    pagina.querySelectorAll('.perfis form').forEach(form => form.addEventListener('submit', trocarPerfil));
    pagina.querySelector('#form-cadastro').addEventListener('submit', simularCadastro);
    const botao = pagina.querySelector('#simular-cadastro');
    botao.addEventListener('click', simularCadastro);
    botao.disabled = false;
    const cnpj = pagina.querySelector('#cad-cnpj');
    if (cnpj) cnpj.setAttribute('aria-describedby', 'cad-cnpj-msg');
  }

  prepararPagina();
})();
