# -*- coding: utf-8 -*-
"""
Ferramenta de balanceamento — roda milhares de combates em silêncio e mede.

Por que este arquivo existe
---------------------------
Balancear um RPG "no olho" não funciona: a gente joga três partidas, acha que
está bom, e na verdade uma classe ganha 99% das vezes. Este script roda cada
confronto possível centenas de vezes com `verbose=False` e imprime a taxa de
vitória e a duração média.

Foi com ele que encontramos (e corrigimos) quatro problemas reais — estão
descritos no README, seção "Balanceamento orientado a dados".

Como executar:
    python ferramentas/simulacao_balanceamento.py
    python ferramentas/simulacao_balanceamento.py 1000   (mais amostras)
"""

from __future__ import annotations

import os
import statistics
import sys

# Permite rodar o script direto de dentro da pasta ferramentas/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rpg.batalha import Batalha1v1, Batalha3v3  # noqa: E402
from rpg.elenco import (  # noqa: E402
    HEROIS,
    MONSTROS,
    criar_heroi,
    criar_monstro,
    time_de_herois_magico,
    time_de_herois_padrao,
    time_de_monstros_padrao,
    time_de_monstros_veloz,
)

# Faixa considerada saudável: nenhuma vantagem deve ser absoluta.
FAIXA_SAUDAVEL = (0.10, 0.90)


def simular_1v1(amostras: int) -> None:
    """Cruza todos os heróis contra todos os monstros e imprime a tabela."""
    print(f"\n{'HERÓI':<12} {'MONSTRO':<18} {'VITÓRIAS':>9} {'TURNOS':>8}   SITUAÇÃO")
    print("-" * 62)

    alertas = 0
    for chave_heroi, (rotulo_heroi, _) in HEROIS.items():
        for chave_monstro, (rotulo_monstro, _) in MONSTROS.items():
            vitorias = 0
            turnos: list[int] = []

            for _ in range(amostras):
                heroi = criar_heroi(chave_heroi)
                monstro = criar_monstro(chave_monstro)
                batalha = Batalha1v1(heroi, monstro, verbose=False)
                if batalha.executar() is heroi:
                    vitorias += 1
                turnos.append(batalha.rodada)

            taxa = vitorias / amostras
            media = statistics.mean(turnos)
            saudavel = FAIXA_SAUDAVEL[0] <= taxa <= FAIXA_SAUDAVEL[1]
            marca = "ok" if saudavel else "<-- vantagem forte"
            alertas += 0 if saudavel else 1

            nome_heroi = rotulo_heroi.split(",")[0]
            print(
                f"{nome_heroi:<12} {rotulo_monstro:<18} "
                f"{taxa:>8.0%} {media:>8.1f}   {marca}"
            )

    print(f"\nConfrontos com vantagem forte: {alertas}")


def simular_3v3(amostras: int) -> None:
    """Cruza as formações de time e imprime a taxa de vitória dos heróis."""
    print(f"\n{'CONFRONTO 3v3':<32} {'HERÓIS':>8} {'RODADAS':>9}")
    print("-" * 52)

    confrontos = [
        (time_de_herois_padrao, time_de_monstros_padrao, "Guardiões x Lendas da Noite"),
        (time_de_herois_magico, time_de_monstros_padrao, "Filhos da Mata x Lendas"),
        (time_de_herois_padrao, time_de_monstros_veloz, "Guardiões x Assombração"),
        (time_de_herois_magico, time_de_monstros_veloz, "Filhos da Mata x Assombração"),
    ]

    for fabrica_herois, fabrica_monstros, rotulo in confrontos:
        vitorias = 0
        rodadas: list[int] = []

        for _ in range(amostras):
            herois = fabrica_herois()
            monstros = fabrica_monstros()
            batalha = Batalha3v3(herois, monstros, verbose=False)
            if batalha.executar() is herois:
                vitorias += 1
            rodadas.append(batalha.rodada)

        print(
            f"{rotulo:<32} {vitorias / amostras:>7.0%} "
            f"{statistics.mean(rodadas):>9.1f}"
        )


def main() -> None:
    amostras = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    print("=" * 62)
    print(f"  SIMULAÇÃO DE BALANCEAMENTO — {amostras} combates por confronto")
    print("=" * 62)
    simular_1v1(amostras)
    simular_3v3(amostras)
    print()


if __name__ == "__main__":
    main()
