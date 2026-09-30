# -*- coding: utf-8 -*-
"""
Utilitários de apresentação no terminal.

Este módulo NÃO contém regra de negócio do combate: ele só cuida de como as
informações aparecem para o jogador (cores, barras de vida, títulos, pausas).

Separar apresentação de regra de negócio é uma boa prática: se amanhã o jogo
virar uma interface web, só este arquivo precisa ser trocado — as classes de
combate continuam idênticas.
"""

from __future__ import annotations

import os
import sys
import time


class Cor:
    """Constantes de cor ANSI usadas na narração do combate."""

    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    FRACO = "\033[2m"

    VERMELHO = "\033[31m"
    VERDE = "\033[32m"
    AMARELO = "\033[33m"
    AZUL = "\033[34m"
    MAGENTA = "\033[35m"
    CIANO = "\033[36m"
    CINZA = "\033[90m"

    VERMELHO_CLARO = "\033[91m"
    VERDE_CLARO = "\033[92m"
    AMARELO_CLARO = "\033[93m"
    AZUL_CLARO = "\033[94m"
    MAGENTA_CLARO = "\033[95m"
    CIANO_CLARO = "\033[96m"


# Flag global: permite rodar o jogo sem cores (útil para salvar a saída em
# arquivo ou para terminais antigos).
USAR_CORES = True


def ativar_cores_no_windows() -> None:
    """
    Liga o suporte a ANSI no terminal do Windows.

    O `os.system("")` parece inútil, mas ele força o Windows a inicializar o
    modo de terminal virtual, que é o que faz as cores funcionarem no cmd.
    Em Linux e macOS a função não faz diferença nenhuma.
    """
    if os.name == "nt":
        os.system("")


def colorir(texto: str, cor: str) -> str:
    """Envolve o texto em uma cor ANSI, respeitando a flag USAR_CORES."""
    if not USAR_CORES:
        return texto
    return f"{cor}{texto}{Cor.RESET}"


def barra_vida(atual: int, maximo: int, largura: int = 18) -> str:
    """
    Desenha uma barra de vida em texto, tipo [#########-------].

    Entrada : hp atual, hp máximo e a largura da barra em caracteres.
    Processo: calcula a proporção e converte em número de blocos preenchidos.
    Saída   : string colorida (verde > 50%, amarelo > 25%, vermelho abaixo).
    """
    if maximo <= 0:
        maximo = 1
    proporcao = max(0.0, min(1.0, atual / maximo))
    preenchido = int(round(proporcao * largura))
    vazio = largura - preenchido

    if proporcao > 0.5:
        cor = Cor.VERDE_CLARO
    elif proporcao > 0.25:
        cor = Cor.AMARELO_CLARO
    else:
        cor = Cor.VERMELHO_CLARO

    corpo = "█" * preenchido + "░" * vazio
    return colorir(f"[{corpo}]", cor)


def barra_mana(atual: int, maximo: int, largura: int = 10) -> str:
    """Mesma ideia da barra de vida, mas sempre azul (mana)."""
    if maximo <= 0:
        return colorir("[" + "░" * largura + "]", Cor.CINZA)
    proporcao = max(0.0, min(1.0, atual / maximo))
    preenchido = int(round(proporcao * largura))
    corpo = "▰" * preenchido + "▱" * (largura - preenchido)
    return colorir(f"[{corpo}]", Cor.AZUL_CLARO)


def titulo(texto: str, largura: int = 68, cor: str = Cor.CIANO_CLARO) -> str:
    """Cria um cabeçalho centralizado entre linhas duplas."""
    linha = "═" * largura
    meio = texto.center(largura)
    return colorir(f"╔{linha}╗\n║{meio}║\n╚{linha}╝", cor)


def subtitulo(texto: str, largura: int = 68, cor: str = Cor.AMARELO_CLARO) -> str:
    """Cabeçalho mais leve, usado entre rodadas do combate."""
    return colorir(f"\n── {texto} ".ljust(largura + 3, "─"), cor)


def limpar_tela() -> None:
    """Limpa o terminal (cls no Windows, clear no resto)."""
    os.system("cls" if os.name == "nt" else "clear")


def pausa_dramatica(segundos: float) -> None:
    """
    Espera alguns instantes entre as falas do combate.

    Existe só para o combate não cuspir 40 linhas de uma vez. Em modo de teste
    automatizado passamos 0 e o jogo roda instantaneamente.
    """
    if segundos > 0:
        time.sleep(segundos)


def esperar_enter(mensagem: str = "Pressione ENTER para continuar...") -> None:
    """Pausa que exige interação do usuário. Tolera Ctrl+C / EOF sem quebrar."""
    try:
        input(colorir(f"\n{mensagem}", Cor.CINZA))
    except (EOFError, KeyboardInterrupt):
        print()


def ler_opcao(mensagem: str, validas: list[str]) -> str:
    """
    Lê uma opção do teclado até o usuário digitar algo válido.

    Entrada : texto da pergunta e a lista de respostas aceitas.
    Processo: repete o input enquanto a resposta não estiver na lista.
    Saída   : a opção escolhida, já sem espaços e em minúsculas.

    Se a entrada for fechada (EOF — acontece ao rodar com pipe ou redirecionando
    um arquivo), devolvemos a ÚLTIMA opção válida. Nos menus deste jogo a última
    opção é sempre "0 - Sair", então o programa encerra sozinho em vez de ficar
    preso. Devolver a PRIMEIRA opção, como fizemos na primeira versão, causava
    um laço infinito: o menu escolhia "1 - Batalha 1v1" para sempre.
    """
    while True:
        try:
            escolha = input(colorir(mensagem, Cor.CIANO_CLARO)).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return validas[-1]
        if escolha in validas:
            return escolha
        print(colorir("  ⚠  Opção inválida. Tente de novo.", Cor.VERMELHO_CLARO))


def escrever(texto: str = "") -> None:
    """Print com flush imediato — garante que a narração saia na ordem certa."""
    print(texto)
    sys.stdout.flush()
