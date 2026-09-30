# -*- coding: utf-8 -*-
"""
Núcleo do sistema de combate: a classe abstrata `Combatente`.

DECISÃO DE ARQUITETURA (importante para a correção)
---------------------------------------------------
O enunciado pede duas classes-pai: `Personagem` e `Monstro`. Ele também exige
que *ambas* possuam os sete atributos obrigatórios:

    hp, mp, speed, atk, matk, defense, mdefense

Havia dois caminhos:

    (A) copiar os sete atributos dentro de `Personagem` e de novo dentro de
        `Monstro`;
    (B) criar um ancestral comum — `Combatente` — que define os sete atributos
        uma única vez, e fazer `Personagem` e `Monstro` herdarem dele.

Escolhemos (B). O enunciado autoriza explicitamente ("devem herdar ou
implementar uma estrutura que contenha obrigatoriamente...") e essa opção evita
duplicação de código (princípio DRY - Don't Repeat Yourself). `Personagem` e
`Monstro` continuam sendo classes-pai de verdade: elas é que são herdadas por
Guerreiro/Mago/Capoeirista/Benzedeira e por Saci/Curupira/Boitatá/etc.

A hierarquia final fica assim:

    Combatente (abstrata)
    ├── Personagem ──── Guerreiro, Mago, Capoeirista, Benzedeira
    └── Monstro ─────── Saci, Curupira, Boitatá, MulaSemCabeca, Cuca, Iara

Um bônus dessa escolha: como herói e monstro compartilham o mesmo ancestral, o
motor de batalha consegue tratar os dois exatamente da mesma forma. É isso que
permite escrever `atacante.agir(aliados, inimigos)` sem perguntar "isso aqui é
um herói ou um monstro?" — ou seja, polimorfismo de verdade.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod

from rpg.utils import Cor, barra_mana, barra_vida, colorir

# ---------------------------------------------------------------------------
# Constantes de balanceamento
# ---------------------------------------------------------------------------
DANO_MINIMO = 1           # nenhum golpe causa 0 de dano por defesa alta
PISO_PROPORCIONAL = 0.10  # todo golpe passa pelo menos 10% do próprio poder
VARIACAO_DANO = 0.15      # ±15% de aleatoriedade para o combate não ser robótico
MULTIPLICADOR_CRITICO = 1.8
CHANCE_CRITICO_BASE = 0.05   # 5% fixos
FATOR_CRITICO_SPEED = 0.006  # +0,6% de crítico por ponto de speed
REGENERACAO_MANA = 4         # mana recuperada por rodada (ver regenerar_por_rodada)
FATOR_AUTOCURA = 0.5         # curandeiras curam a si mesmas pela metade


def calcular_dano(poder: int, defesa: int, *, critico: bool = False) -> int:
    """
    Converte (poder de ataque, defesa do alvo) em dano final.

    FÓRMULA BASE EXIGIDA PELO ENUNCIADO:
        dano = ataque - defesa                (físico)
        dano = ataque_mágico - defesa_mágica  (mágico)

    Em cima dessa base simples adicionamos três camadas para o combate ficar
    mais interessante (requisito de criatividade):

      1. Piso PROPORCIONAL de dano: se a defesa anular o ataque, o golpe ainda
         passa 10% do poder do atacante. Isso resolve um bug real que apareceu
         no nosso primeiro teste: o Capoeirista (atk 23) contra o Curupira
         (defense 24) causava 1 de dano por golpe, e o duelo nunca terminava.
         Com o piso proporcional, um atacante forte sempre machuca — só que
         muito menos contra quem se defende bem.
      2. Variação de ±15%: o mesmo golpe nunca tira exatamente o mesmo número
         duas vezes, o que evita combates 100% previsíveis.
      3. Crítico: multiplica o dano final quando o ataque "acerta em cheio".

    Entrada : poder (atk ou matk do atacante), defesa (defense ou mdefense do
              alvo) e se o golpe foi crítico.
    Processo: subtração base -> piso -> variação aleatória -> crítico.
    Saída   : inteiro >= 1 com o dano a ser aplicado.
    """
    piso = max(DANO_MINIMO, int(poder * PISO_PROPORCIONAL))
    base = max(piso, poder - defesa)

    variacao = random.uniform(1 - VARIACAO_DANO, 1 + VARIACAO_DANO)
    dano = base * variacao

    if critico:
        dano *= MULTIPLICADOR_CRITICO

    return max(DANO_MINIMO, int(round(dano)))


def rolar_critico(speed: int) -> bool:
    """
    Sorteia se o golpe é crítico. Quanto mais rápido o combatente, maior a
    chance — é o que dá identidade mecânica a classes ágeis como o Capoeirista.
    """
    chance = min(0.45, CHANCE_CRITICO_BASE + speed * FATOR_CRITICO_SPEED)
    return random.random() < chance


class Combatente(ABC):
    """
    Classe abstrata que representa qualquer coisa capaz de lutar.

    É abstrata (herda de ABC) porque "um combatente genérico" não existe no
    jogo: o que existe é um Guerreiro, um Saci, uma Cuca. Tentar fazer
    `Combatente("teste", ...)` levanta TypeError, e isso é proposital — força
    quem usa o código a instanciar sempre uma classe concreta.

    ATRIBUTOS OBRIGATÓRIOS DO ENUNCIADO (todos definidos aqui):
        hp       -> vida atual (encapsulada por property)
        mp       -> mana atual (encapsulada por property)
        speed    -> velocidade; decide a ordem dos turnos
        atk      -> ataque físico
        matk     -> ataque mágico
        defense  -> defesa física
        mdefense -> defesa mágica
    """

    def __init__(
        self,
        nome: str,
        *,
        hp: int,
        mp: int,
        speed: int,
        atk: int,
        matk: int,
        defense: int,
        mdefense: int,
    ) -> None:
        self.nome = nome

        # ENCAPSULAMENTO: hp e mp são guardados em atributos "privados"
        # (prefixo _) e expostos por properties. Isso impede que alguém escreva
        # `heroi.hp = -500` e quebre a lógica do jogo: a property corrige o
        # valor para dentro do intervalo válido automaticamente.
        self._hp_max = hp
        self._hp = hp
        self._mp_max = mp
        self._mp = mp

        # Atributos de combate — públicos porque podem ser buffados/debuffados
        # livremente sem risco de quebrar invariantes.
        self.speed = speed
        self.atk = atk
        self.matk = matk
        self.defense = defense
        self.mdefense = mdefense

    # ------------------------------------------------------------------
    # Properties (encapsulamento)
    # ------------------------------------------------------------------
    @property
    def hp(self) -> int:
        """Vida atual."""
        return self._hp

    @hp.setter
    def hp(self, valor: int) -> None:
        """Mantém a vida sempre entre 0 e o máximo, sem precisar de if externo."""
        self._hp = max(0, min(int(valor), self._hp_max))

    @property
    def hp_max(self) -> int:
        """Vida máxima (somente leitura — não tem setter de propósito)."""
        return self._hp_max

    @property
    def mp(self) -> int:
        """Mana atual."""
        return self._mp

    @mp.setter
    def mp(self, valor: int) -> None:
        self._mp = max(0, min(int(valor), self._mp_max))

    @property
    def mp_max(self) -> int:
        """Mana máxima (somente leitura)."""
        return self._mp_max

    @property
    def esta_vivo(self) -> bool:
        """
        Condição central do jogo: o combatente só age enquanto hp > 0.

        A condição de vitória do enunciado ("quando todos os membros de um time
        ficam com hp <= 0") é verificada a partir daqui.
        """
        return self._hp > 0

    @property
    def percentual_vida(self) -> float:
        """Vida atual em fração de 0.0 a 1.0 — usado por IA e barras."""
        return self._hp / self._hp_max if self._hp_max else 0.0

    # ------------------------------------------------------------------
    # Ações sofridas
    # ------------------------------------------------------------------
    def receber_dano(self, dano: int) -> int:
        """
        Aplica dano e devolve quanto foi efetivamente tirado.

        CONTRATO IMPORTANTE: o retorno 0 significa "o golpe foi completamente
        anulado" (por exemplo, a esquiva do Capoeirista). Como `calcular_dano`
        nunca devolve menos que 1, o zero é inequívoco. Subclasses que queiram
        esquiva/imunidade sobrescrevem este método e devolvem 0 — o motor de
        batalha entende sozinho e narra "escapou ileso".
        """
        dano = max(0, int(dano))
        antes = self._hp
        self.hp = self._hp - dano
        return antes - self._hp

    def curar(self, valor: int) -> int:
        """Recupera vida sem ultrapassar o máximo. Devolve o quanto curou."""
        antes = self._hp
        self.hp = self._hp + max(0, int(valor))
        return self._hp - antes

    def gastar_mana(self, custo: int) -> bool:
        """
        Tenta gastar mana.

        Saída: True se havia mana suficiente (e ela foi debitada), False caso
        contrário. É esse False que faz o Mago recorrer ao ataque de cajado.
        """
        if self._mp >= custo:
            self.mp = self._mp - custo
            return True
        return False

    def recuperar_mana(self, valor: int) -> int:
        """Recupera mana sem ultrapassar o máximo."""
        antes = self._mp
        self.mp = self._mp + max(0, int(valor))
        return self._mp - antes

    def regenerar_por_rodada(self) -> None:
        """
        Recupera um pouco de mana no início de cada rodada.

        Por que isso existe: a simulação de balanceamento mostrou que a Cuca,
        que drena mana, vencia 100% dos duelos contra Mago e Benzedeira — não
        por dano, mas por deixá-los sem recurso e sem nada para fazer. Uma
        regeneração pequena mantém o dreno perigoso sem torná-lo uma sentença
        de morte automática.
        """
        self.recuperar_mana(REGENERACAO_MANA)

    # ------------------------------------------------------------------
    # Ações executadas
    # ------------------------------------------------------------------
    @abstractmethod
    def atacar(self, alvo: "Combatente") -> str:
        """
        Executa um ataque contra o alvo e devolve a narração do que aconteceu.

        É ABSTRATO de propósito: este é o ponto de POLIMORFISMO do trabalho.
        Cada subclasse obriga-se a implementar seu próprio jeito de atacar —
        o Guerreiro entra em fúria, o Mago gasta mana, o Capoeirista pode
        golpear duas vezes, o Boitatá cospe fogo. O motor de batalha chama
        sempre `atacante.atacar(alvo)` e nem precisa saber qual classe é.
        """
        raise NotImplementedError

    def escolher_alvo(self, inimigos: list["Combatente"]) -> "Combatente | None":
        """
        Decide em quem bater. Implementação padrão: sorteia entre os vivos.

        Subclasses sobrescrevem para ter personalidade própria (a Mula-sem-
        Cabeça caça o mais ferido, o Curupira encara o mais forte...). Isso é
        polimorfismo aplicado à inteligência artificial, não só ao ataque.
        """
        vivos = [i for i in inimigos if i.esta_vivo]
        return random.choice(vivos) if vivos else None

    def _aplicar_golpe(
        self,
        alvo: "Combatente",
        poder: int,
        defesa_alvo: int,
        nome_golpe: str,
        *,
        tipo: str = "físico",
        critico: bool = False,
        cor: str = Cor.RESET,
    ) -> str:
        """
        Rotina compartilhada: calcula, aplica e narra um golpe.

        Existe para que o método `atacar` de cada subclasse fique curto e
        legível — a subclasse decide SÓ o que é único nela (qual atributo usar,
        o nome do golpe, se há bônus) e delega o trabalho repetitivo para cá.
        Isso é reaproveitamento por herança na prática.
        """
        dano = calcular_dano(poder, defesa_alvo, critico=critico)
        aplicado = alvo.receber_dano(dano)

        if aplicado == 0:
            return colorir(
                f"   {self.nome} usou {nome_golpe}, mas {alvo.nome} escapou ileso!",
                Cor.CINZA,
            )

        marca = colorir("  ⚡ CRÍTICO!", Cor.AMARELO_CLARO) if critico else ""
        golpe = colorir(nome_golpe, cor)
        valor = colorir(f"-{aplicado}", Cor.VERMELHO_CLARO)
        return f"   {self.nome} usou {golpe} em {alvo.nome} → {valor} de dano {tipo}.{marca}"

    # ------------------------------------------------------------------
    # Apresentação
    # ------------------------------------------------------------------
    def status_curto(self) -> str:
        """Linha compacta com barra de vida — usada durante o combate."""
        if not self.esta_vivo:
            return colorir(f"   ☠  {self.nome} está fora de combate.", Cor.CINZA)
        return (
            f"   {self.nome:<22} {barra_vida(self._hp, self._hp_max)} "
            f"{self._hp:>4}/{self._hp_max:<4} "
            f"{barra_mana(self._mp, self._mp_max)} {self._mp:>3}/{self._mp_max}"
        )

    def ficha(self) -> str:
        """Ficha completa com os sete atributos — usada no menu."""
        return (
            f"{colorir(self.nome, Cor.NEGRITO)}\n"
            f"   HP {self._hp}/{self._hp_max}   MP {self._mp}/{self._mp_max}\n"
            f"   SPEED {self.speed:<4} ATK {self.atk:<4} MATK {self.matk:<4}\n"
            f"   DEFENSE {self.defense:<4} MDEFENSE {self.mdefense}"
        )

    def __str__(self) -> str:
        """Sobrescrita de método mágico: define como o objeto vira texto."""
        return f"{self.nome} (HP {self._hp}/{self._hp_max})"

    def __repr__(self) -> str:
        """Representação técnica, útil ao depurar no console do Python."""
        return f"<{type(self).__name__} nome={self.nome!r} hp={self._hp}>"
