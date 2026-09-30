# -*- coding: utf-8 -*-
"""
Motor de combate: `Time`, `Batalha` (abstrata), `Batalha1v1` e `Batalha3v3`.

Atende aos requisitos 6 e 7 do enunciado.

Observação de projeto: o motor NÃO conhece nenhuma classe concreta. Ele nunca
escreve `if isinstance(x, Guerreiro)`. Ele só sabe que recebeu objetos que
respondem a `agir()`, `escolher_alvo()` e `esta_vivo` — o resto é com cada
classe. É por isso que dá para criar uma classe nova (um Arqueiro, um Boto) sem
alterar uma linha sequer deste arquivo.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod

from rpg.combatente import Combatente
from rpg.utils import (
    Cor,
    colorir,
    escrever,
    pausa_dramatica,
    subtitulo,
    titulo,
)

LIMITE_RODADAS = 60  # trava de segurança contra combates que nunca terminam


class Time:
    """
    Agrupa combatentes sob um nome.

    Isto é COMPOSIÇÃO, não herança: um Time não "é um" Combatente — ele
    "tem vários" Combatentes. Usar a relação certa (tem-um vs. é-um) é um dos
    pontos que mais aparecem na avaliação de POO.
    """

    def __init__(self, nome: str, membros: list[Combatente]) -> None:
        self.nome = nome
        self.membros = membros

    @property
    def vivos(self) -> list[Combatente]:
        """Lista só de quem ainda tem hp > 0."""
        return [m for m in self.membros if m.esta_vivo]

    @property
    def derrotado(self) -> bool:
        """
        CONDIÇÃO DE DERROTA DO ENUNCIADO: verdadeiro quando TODOS os membros
        estão com hp <= 0.
        """
        return len(self.vivos) == 0

    def status(self) -> str:
        """Bloco de texto com a barra de vida de cada membro."""
        linhas = [colorir(f"  {self.nome}", Cor.NEGRITO)]
        linhas.extend(m.status_curto() for m in self.membros)
        return "\n".join(linhas)

    def __len__(self) -> int:
        """Permite usar len(time) — outro método mágico sobrescrito."""
        return len(self.membros)

    def __iter__(self):
        """Permite usar `for membro in time:` diretamente."""
        return iter(self.membros)

    def __str__(self) -> str:
        return f"{self.nome} ({len(self.vivos)}/{len(self.membros)} de pé)"


class Batalha(ABC):
    """
    Classe-pai abstrata dos modos de combate.

    Concentra tudo que 1v1 e 3v3 têm em comum:
      • narração com pausa dramática;
      • ordenação de turnos por `speed`;
      • contador de rodadas e trava de segurança.

    Cada modo implementa `executar()` do seu jeito. Mais uma vez: herança para
    reaproveitar, polimorfismo para especializar.
    """

    def __init__(self, *, delay: float = 0.0, verbose: bool = True) -> None:
        self.delay = delay
        self.verbose = verbose
        self.rodada = 0
        self.historico: list[str] = []

    def narrar(self, texto: str = "") -> None:
        """
        Imprime (se verbose) e guarda no histórico.

        O histórico existe para permitir rodar uma batalha em silêncio
        (`verbose=False`) e analisar o resultado depois — foi assim que
        balanceamos os atributos das classes durante o desenvolvimento.
        """
        self.historico.append(texto)
        if self.verbose:
            escrever(texto)
            pausa_dramatica(self.delay)

    @staticmethod
    def ordenar_por_velocidade(combatentes: list[Combatente]) -> list[Combatente]:
        """
        REGRA DO ENUNCIADO: a `speed` decide quem ataca primeiro.

        Processo: embaralha e depois ordena por speed decrescente. O embaralhar
        antes garante que empates de velocidade sejam desempatados por sorteio,
        e não pela ordem em que os objetos foram criados (o `sorted` do Python
        é estável, então sem o shuffle o primeiro da lista venceria sempre).
        """
        copia = list(combatentes)
        random.shuffle(copia)
        return sorted(copia, key=lambda c: c.speed, reverse=True)

    @abstractmethod
    def executar(self) -> Combatente | Time | None:
        """Roda o combate até o fim e devolve o vencedor."""
        raise NotImplementedError


class Batalha1v1(Batalha):
    """
    REQUISITO 6 — duelo por turnos entre um herói e um monstro.

    Fluxo:
      1. A speed decide quem começa.
      2. Enquanto os dois estiverem vivos, alternam turnos.
      3. Em cada turno o combatente age (ataca, ou cura, se for Benzedeira).
      4. Termina quando alguém chega a hp <= 0.
    """

    def __init__(self, heroi: Combatente, monstro: Combatente, **kwargs) -> None:
        super().__init__(**kwargs)
        self.heroi = heroi
        self.monstro = monstro

    def executar(self) -> Combatente | None:
        """
        Executa o duelo completo.

        Saída: o objeto vencedor, ou None se estourar o limite de rodadas
        (empate técnico — raro, mas a trava evita loop infinito).
        """
        self.narrar(titulo("DUELO NA MATA", cor=Cor.CIANO_CLARO))
        self.narrar(f"  {self.heroi.nome} encara {self.monstro.nome}!\n")

        ordem = self.ordenar_por_velocidade([self.heroi, self.monstro])
        self.narrar(
            colorir(
                f"  ⚡ {ordem[0].nome} é mais rápido (speed {ordem[0].speed} "
                f"contra {ordem[1].speed}) e ataca primeiro.\n",
                Cor.AMARELO_CLARO,
            )
        )

        while self.heroi.esta_vivo and self.monstro.esta_vivo:
            self.rodada += 1
            if self.rodada > LIMITE_RODADAS:
                self.narrar(colorir("\n  A noite cai e os dois recuam. Empate.", Cor.CINZA))
                return None

            # Regeneração de mana no início da rodada (ver combatente.py).
            for combatente in (self.heroi, self.monstro):
                if combatente.esta_vivo:
                    combatente.regenerar_por_rodada()

            self.narrar(subtitulo(f"Turno {self.rodada}"))

            for atacante in ordem:
                if not atacante.esta_vivo:
                    continue

                # Quem é o oponente? Quem não for o atacante.
                oponente = self.monstro if atacante is self.heroi else self.heroi
                if not oponente.esta_vivo:
                    break

                # POLIMORFISMO NA PRÁTICA: a mesma linha serve para Guerreiro,
                # Mago, Capoeirista, Benzedeira, Saci, Cuca... Cada objeto sabe
                # como é o próprio turno.
                self.narrar(atacante.agir([atacante], [oponente]))

                if not oponente.esta_vivo:
                    self.narrar(
                        colorir(f"\n   ☠  {oponente.nome} caiu!", Cor.VERMELHO_CLARO)
                    )
                    break

            self.narrar()
            self.narrar(self.heroi.status_curto())
            self.narrar(self.monstro.status_curto())

        vencedor = self.heroi if self.heroi.esta_vivo else self.monstro
        self.narrar(titulo(f"VITÓRIA DE {vencedor.nome.upper()}", cor=Cor.VERDE_CLARO))

        # Se quem venceu foi o herói e ele sabe ganhar XP, recompensa.
        if vencedor is self.heroi and hasattr(self.heroi, "ganhar_xp"):
            subiu = self.heroi.ganhar_xp(getattr(self.monstro, "xp_recompensa", 0))
            if subiu:
                self.narrar(subiu)

        return vencedor


class Batalha3v3(Batalha):
    """
    REQUISITO 7 — combate em equipe, 3 heróis contra 3 monstros.

    Diferenças em relação ao 1v1:
      • a fila de turnos mistura os SEIS combatentes, ordenados por speed;
      • cada um escolhe o próprio alvo dentro do time inimigo (cada classe tem
        sua própria regra — ver `escolher_alvo` em cada classe);
      • o combate acaba quando um time inteiro fica com hp <= 0.
    """

    def __init__(self, time_herois: Time, time_monstros: Time, **kwargs) -> None:
        super().__init__(**kwargs)
        self.time_herois = time_herois
        self.time_monstros = time_monstros
        # Guarda quem já teve a queda anunciada, para não repetir a mensagem
        # "foi derrotado" a cada ação seguinte da rodada.
        self._ja_anunciados: list[Combatente] = []

    def _time_de(self, combatente: Combatente) -> tuple[Time, Time]:
        """
        Descobre a qual time o combatente pertence.

        Saída: (time dele, time inimigo). Usar identidade (`is`) em vez de
        `isinstance` mantém o motor independente das classes concretas — um
        monstro poderia até lutar ao lado dos heróis que o código funcionaria.
        """
        if any(m is combatente for m in self.time_herois.membros):
            return self.time_herois, self.time_monstros
        return self.time_monstros, self.time_herois

    def executar(self) -> Time | None:
        """Executa o combate 3v3 completo e devolve o time vencedor."""
        self.narrar(titulo("BATALHA 3 VS 3 — A NOITE DAS LENDAS", cor=Cor.MAGENTA_CLARO))
        self.narrar(self.time_herois.status())
        self.narrar("")
        self.narrar(self.time_monstros.status())

        todos = self.time_herois.membros + self.time_monstros.membros
        fila = self.ordenar_por_velocidade(todos)

        self.narrar(colorir("\n  Ordem de ação (por speed):", Cor.AMARELO_CLARO))
        for pos, c in enumerate(fila, start=1):
            self.narrar(colorir(f"    {pos}º {c.nome} (speed {c.speed})", Cor.CINZA))

        while not self.time_herois.derrotado and not self.time_monstros.derrotado:
            self.rodada += 1
            if self.rodada > LIMITE_RODADAS:
                self.narrar(colorir("\n  O sol nasce e a batalha se dissolve. Empate.", Cor.CINZA))
                return None

            # Regeneração de mana no início da rodada (ver combatente.py).
            for combatente in fila:
                if combatente.esta_vivo:
                    combatente.regenerar_por_rodada()

            self.narrar(subtitulo(f"RODADA {self.rodada}"))

            for atacante in fila:
                if not atacante.esta_vivo:
                    continue

                aliados_time, inimigos_time = self._time_de(atacante)

                # Se o time inimigo já caiu inteiro, a rodada acaba na hora.
                if inimigos_time.derrotado:
                    break

                # Passamos listas de VIVOS: a Benzedeira e a Iara usam os aliados
                # para decidir quem curar, e todos usam os inimigos para escolher
                # alvo. Mais uma vez, uma linha só para qualquer classe.
                self.narrar(atacante.agir(aliados_time.vivos, inimigos_time.vivos))

                # Anuncia, uma única vez, quem caiu nesta ação.
                for caido in inimigos_time.membros:
                    ja_anunciado = any(c is caido for c in self._ja_anunciados)
                    if not caido.esta_vivo and not ja_anunciado:
                        self._ja_anunciados.append(caido)
                        self.narrar(
                            colorir(f"   ☠  {caido.nome} foi derrotado!", Cor.VERMELHO_CLARO)
                        )

            self.narrar("")
            self.narrar(self.time_herois.status())
            self.narrar("")
            self.narrar(self.time_monstros.status())

        # CONDIÇÃO DE VITÓRIA/DERROTA: qual time ficou sem ninguém de pé.
        if self.time_monstros.derrotado:
            vencedor = self.time_herois
            cor = Cor.VERDE_CLARO
        else:
            vencedor = self.time_monstros
            cor = Cor.VERMELHO_CLARO

        self.narrar(titulo(f"{vencedor.nome.upper()} VENCEU!", cor=cor))
        self.narrar(
            colorir(
                f"  Combate encerrado em {self.rodada} rodadas. "
                f"Sobreviventes: {', '.join(c.nome for c in vencedor.vivos)}.",
                Cor.CINZA,
            )
        )
        return vencedor
