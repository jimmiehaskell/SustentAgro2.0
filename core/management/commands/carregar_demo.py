"""python manage.py carregar_demo (BL-27, Pedro). RF-32: apaga e recria os dados de demonstração."""
import secrets

from decouple import config
from django.core.management.base import BaseCommand, CommandError

from core.demo.carga import carregar


class Command(BaseCommand):
    help = 'Apaga e recria os dados de demonstração (pessoas, ONGs, necessidades, ofertas e reservas).'

    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_true', help='Não pede confirmação antes de apagar.')
        parser.add_argument('--senha', help='Senha das contas de demonstração (ou DEMO_SENHA no .env).')

    def handle(self, *args, **opcoes):
        if not opcoes['noinput']:
            resposta = input('Isto APAGA as pessoas, ONGs, ofertas e reservas do banco (superusuários ficam). '
                             'Digite "sim" para continuar: ')
            if resposta.strip().lower() != 'sim':
                raise CommandError('Cancelado. Nada foi apagado.')

        senha = opcoes['senha'] or config('DEMO_SENHA', default='')
        senha_gerada = not senha
        if senha_gerada:
            senha = secrets.token_urlsafe(9)

        resumo = carregar(senha)

        self.stdout.write(self.style.SUCCESS('Dados de demonstração carregados:'))
        for nome, quantidade in resumo.items():
            self.stdout.write(f'  {nome}: {quantidade}')
        if senha_gerada:
            self.stdout.write(f'Senha de todas as contas de demonstração: {senha}')
        self.stdout.write('Exemplos de login: antonio.ribeiro (agricultor), mariana.costa (doadora), '
                          'solnascente (ONG ativa), hortavilaplanalto (ONG pendente).')
