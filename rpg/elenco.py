# -*- coding: utf-8 -*-
"""
Elenco do jogo — REQUISITO 5: instanciação dos objetos.

Aqui saímos do mundo das classes (o molde) e entramos no mundo dos objetos
(a peça pronta). Cada chamada `Guerreiro("Lampião")` cria uma INSTÂNCIA nova,
com sua própria cópia dos sete atributos na memória.

Por que usar FUNÇÕES FÁBRICA em vez de uma lista pronta de objetos?
------------------------------------------------------------------
Porque objeto guarda estado. Se criássemos `LAMPIAO = Guerreiro("Lampião")` no
topo do módulo, ele sairia machucado da primeira batalha e entraria na segunda
já sem vida — o famoso bug de estado compartilhado. As fábricas devolvem
sempre um objeto novo, com a vida cheia.
"""

from __future__ import annotations

from rpg.batalha import Time
from rpg.monstros import Boitata, Cuca, Curupira, Iara, Monstro, MulaSemCabeca, Saci
from rpg.personagens import Benzedeira, Capoeirista, Guerreiro, Mago, Personagem

# ---------------------------------------------------------------------------
# Heróis disponíveis
# ---------------------------------------------------------------------------
# Cada entrada é: chave -> (rótulo no menu, função que cria o objeto)
HEROIS = {
    "1": ("Lampião, o Guerreiro", lambda: Guerreiro("Lampião")),
    "2": ("Tibiriçá, o Mago", lambda: Mago("Tibiriçá")),
    "3": ("Besouro, o Capoeirista", lambda: Capoeirista("Besouro")),
    "4": ("Dona Rosa, a Benzedeira", lambda: Benzedeira("Dona Rosa")),
}

# ---------------------------------------------------------------------------
# Monstros disponíveis
# ---------------------------------------------------------------------------
MONSTROS = {
    "1": ("Saci-Pererê", Saci),
    "2": ("Curupira", Curupira),
    "3": ("Boitatá", Boitata),
    "4": ("Mula-sem-Cabeça", MulaSemCabeca),
    "5": ("Cuca", Cuca),
    "6": ("Iara", Iara),
}


def criar_heroi(chave: str) -> Personagem:
    """Instancia o herói correspondente à chave do menu."""
    _, fabrica = HEROIS[chave]
    return fabrica()


def criar_monstro(chave: str) -> Monstro:
    """Instancia o monstro correspondente à chave do menu."""
    _, classe = MONSTROS[chave]
    return classe()


def time_de_herois_padrao() -> Time:
    """
    Monta o trio clássico para o 3v3.

    Composição pensada: um tanque na frente (Guerreiro), um causador de dano
    ágil (Capoeirista) e um suporte que segura o time de pé (Benzedeira).
    """
    return Time(
        "Guardiões do Sertão",
        [
            Guerreiro("Lampião"),
            Capoeirista("Besouro"),
            Benzedeira("Dona Rosa"),
        ],
    )


def time_de_herois_magico() -> Time:
    """Variante do trio, trocando o Capoeirista pelo dano mágico do Mago."""
    return Time(
        "Filhos da Mata",
        [
            Guerreiro("Maria Bonita"),
            Mago("Tibiriçá"),
            Benzedeira("Dona Rosa"),
        ],
    )


def time_de_monstros_padrao() -> Time:
    """
    Trio de monstros equilibrado: um tanque físico, um mago e uma curandeira.

    Repare que os três usam estratégias DIFERENTES de escolha de alvo, então o
    time inteiro se comporta de forma coordenada sem nenhuma linha de código
    dizendo isso — é só a soma dos polimorfismos individuais.
    """
    return Time("Lendas da Noite", [Curupira(), Boitata(), Iara()])


def time_de_monstros_veloz() -> Time:
    """Variante de desgaste: drena mana, cura e ataca primeiro."""
    return Time("Assombração do Mato", [Saci(), Cuca(), Iara()])


def todos_os_herois() -> list[Personagem]:
    """Cria um de cada herói — usado na tela de fichas."""
    return [criar_heroi(chave) for chave in HEROIS]


def todos_os_monstros() -> list[Monstro]:
    """Cria um de cada monstro — usado na tela de fichas."""
    return [criar_monstro(chave) for chave in MONSTROS]
