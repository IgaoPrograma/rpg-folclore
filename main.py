# -*- coding: utf-8 -*-
"""
Ponto de entrada do jogo — CP2 de Python (FIAP).

RPG DAS LENDAS — Sistema de batalha por turnos com POO
Tema: folclore brasileiro.

Como executar:
    python main.py            -> menu interativo
    python main.py --demo     -> roda 1v1 e 3v3 automaticamente, sem input
    python main.py --sem-cor  -> desliga as cores ANSI

Este arquivo cuida APENAS da interface (menus, prints e inputs). Toda a regra
de negócio do combate está no pacote `rpg/`. Essa separação é proposital: dá
para trocar este arquivo por uma interface web sem tocar em nenhuma classe.
"""

from __future__ import annotations

import sys

from rpg import utils
from rpg.batalha import Batalha1v1, Batalha3v3
from rpg.elenco import (
    HEROIS,
    MONSTROS,
    criar_heroi,
    criar_monstro,
    time_de_herois_magico,
    time_de_herois_padrao,
    time_de_monstros_padrao,
    time_de_monstros_veloz,
    todos_os_herois,
    todos_os_monstros,
)
from rpg.utils import Cor, colorir, escrever, esperar_enter, ler_opcao, titulo

DELAY_PADRAO = 0.35   # pausa entre as falas do combate, em segundos


# ---------------------------------------------------------------------------
# Telas
# ---------------------------------------------------------------------------
def tela_abertura() -> None:
    """Mostra o cabeçalho do jogo."""
    escrever(titulo("RPG DAS LENDAS — BATALHA NO FOLCLORE", cor=Cor.MAGENTA_CLARO))
    escrever(
        colorir(
            "  Um sistema de combate por turnos construído com POO em Python.\n"
            "  Heróis do sertão enfrentam as criaturas das lendas brasileiras.\n",
            Cor.CINZA,
        )
    )


def tela_fichas() -> None:
    """Lista os sete atributos de cada herói e de cada monstro."""
    escrever(titulo("FICHAS DE COMBATE", cor=Cor.CIANO_CLARO))

    escrever(colorir("\n  ── HERÓIS JOGÁVEIS ──\n", Cor.VERDE_CLARO))
    for heroi in todos_os_herois():
        escrever(f"  {heroi.ficha()}")
        escrever(colorir(f"   Classe: {heroi.classe} — {heroi.descricao}\n", Cor.CINZA))

    escrever(colorir("\n  ── CRIATURAS DO FOLCLORE ──\n", Cor.VERMELHO_CLARO))
    for monstro in todos_os_monstros():
        escrever(f"  {monstro.ficha()}")
        escrever(colorir(f"   {monstro.lenda}\n", Cor.CINZA))

    esperar_enter()


def escolher_heroi():
    """Mostra o menu de heróis e devolve o objeto escolhido."""
    escrever(colorir("\n  Escolha seu herói:", Cor.NEGRITO))
    for chave, (rotulo, _) in HEROIS.items():
        escrever(f"    {chave}. {rotulo}")
    escolha = ler_opcao("\n  > ", list(HEROIS.keys()))
    return criar_heroi(escolha)


def escolher_monstro():
    """Mostra o menu de monstros e devolve o objeto escolhido."""
    escrever(colorir("\n  Escolha o adversário:", Cor.NEGRITO))
    for chave, (rotulo, _) in MONSTROS.items():
        escrever(f"    {chave}. {rotulo}")
    escolha = ler_opcao("\n  > ", list(MONSTROS.keys()))
    return criar_monstro(escolha)


def modo_1v1() -> None:
    """REQUISITO 6 — duelo herói contra monstro."""
    heroi = escolher_heroi()
    monstro = escolher_monstro()

    escrever("")
    batalha = Batalha1v1(heroi, monstro, delay=DELAY_PADRAO)
    batalha.executar()
    esperar_enter()


def modo_3v3() -> None:
    """REQUISITO 7 — combate em equipe, 3 heróis contra 3 monstros."""
    escrever(colorir("\n  Escolha a formação dos heróis:", Cor.NEGRITO))
    escrever("    1. Guardiões do Sertão  (Guerreiro + Capoeirista + Benzedeira)")
    escrever("    2. Filhos da Mata       (Guerreiro + Mago + Benzedeira)")
    escolha_time = ler_opcao("\n  > ", ["1", "2"])
    herois = time_de_herois_padrao() if escolha_time == "1" else time_de_herois_magico()

    escrever(colorir("\n  Escolha o bando inimigo:", Cor.NEGRITO))
    escrever("    1. Lendas da Noite      (Curupira + Boitatá + Iara)")
    escrever("    2. Assombração do Mato  (Saci + Cuca + Iara)")
    escolha_inimigo = ler_opcao("\n  > ", ["1", "2"])
    monstros = (
        time_de_monstros_padrao() if escolha_inimigo == "1" else time_de_monstros_veloz()
    )

    escrever("")
    batalha = Batalha3v3(herois, monstros, delay=DELAY_PADRAO)
    batalha.executar()
    esperar_enter()


def modo_demo(delay: float = 0.0) -> None:
    """
    Roda um 1v1 e um 3v3 do começo ao fim sem pedir nada ao usuário.

    Permite rodar `python main.py --demo` e ver o sistema inteiro funcionando
    em poucos segundos, sem precisar digitar nada.
    """
    escrever(titulo("MODO DEMONSTRAÇÃO", cor=Cor.AMARELO_CLARO))

    escrever(colorir("\n>>> PARTE 1 — Batalha 1v1\n", Cor.NEGRITO))
    Batalha1v1(criar_heroi("1"), criar_monstro("2"), delay=delay).executar()

    escrever(colorir("\n\n>>> PARTE 2 — Batalha 3v3\n", Cor.NEGRITO))
    Batalha3v3(
        time_de_herois_padrao(), time_de_monstros_padrao(), delay=delay
    ).executar()

    escrever(colorir("\n  Demonstração concluída.\n", Cor.CINZA))


def menu_principal() -> None:
    """Laço principal do programa."""
    while True:
        escrever(colorir("\n  MENU PRINCIPAL", Cor.NEGRITO))
        escrever("    1. Batalha 1v1 (herói contra monstro)")
        escrever("    2. Batalha 3v3 (time contra time)")
        escrever("    3. Ver fichas de todos os combatentes")
        escrever("    4. Modo demonstração (automático)")
        escrever("    0. Sair")

        opcao = ler_opcao("\n  > ", ["1", "2", "3", "4", "0"])

        if opcao == "1":
            modo_1v1()
        elif opcao == "2":
            modo_3v3()
        elif opcao == "3":
            tela_fichas()
        elif opcao == "4":
            modo_demo(delay=DELAY_PADRAO)
        else:
            escrever(colorir("\n  Até a próxima lenda!\n", Cor.CIANO_CLARO))
            return


def main() -> None:
    """
    Lê os argumentos de linha de comando e decide como iniciar o programa.

    Entrada : sys.argv (--demo, --sem-cor).
    Processo: configura cores e dispara o modo escolhido.
    Saída   : nenhuma (o programa roda até o usuário sair).
    """
    utils.ativar_cores_no_windows()

    if "--sem-cor" in sys.argv:
        utils.USAR_CORES = False

    tela_abertura()

    if "--demo" in sys.argv:
        modo_demo(delay=0.0)
        return

    try:
        menu_principal()
    except KeyboardInterrupt:
        escrever(colorir("\n\n  Jogo encerrado pelo usuário.\n", Cor.CINZA))


# Esta checagem faz o bloco só rodar quando o arquivo é EXECUTADO diretamente
# (`python main.py`), e não quando ele é importado por outro módulo.
if __name__ == "__main__":
    main()
