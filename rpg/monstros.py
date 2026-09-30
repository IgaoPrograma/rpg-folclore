# -*- coding: utf-8 -*-
"""
Criaturas do folclore brasileiro: a classe-pai `Monstro` e suas filhas.

Atende ao requisito 2 (segunda classe-pai obrigatória) e ao requisito 10
(criatividade): em vez de goblins e dragões genéricos, os inimigos são as
lendas que todo brasileiro ouviu na infância.

Cada monstro sobrescreve `escolher_alvo` com uma inteligência própria, coerente
com a lenda. Isso é polimorfismo aplicado à IA: o motor de batalha só chama
`monstro.escolher_alvo(herois)` e cada criatura decide do seu jeito.
"""

from __future__ import annotations

import random

from rpg.combatente import FATOR_AUTOCURA, Combatente, rolar_critico
from rpg.utils import Cor, colorir


class Monstro(Combatente):
    """
    Classe-pai de todas as criaturas inimigas.

    Diferenças em relação a `Personagem`:
      • tem `xp_recompensa` (o que os heróis ganham ao derrotá-la);
      • tem `lenda`, um texto de ambientação;
      • `atacar()` já vem IMPLEMENTADO aqui, com base em `tipo_ataque`.

    Por que `Monstro.atacar` é concreto e `Personagem.atacar` é abstrato?
    Porque herói é o centro do jogo: cada classe jogável PRECISA ter identidade
    própria, então forçamos a sobrescrita. Já um monstro comum pode se
    contentar com o ataque padrão — e ainda assim todos os seis implementados
    abaixo sobrescrevem, para ganhar personalidade.
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
        tipo_ataque: str = "fisico",
        xp_recompensa: int = 50,
        lenda: str = "",
    ) -> None:
        super().__init__(
            nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
        )
        self.tipo_ataque = tipo_ataque
        self.xp_recompensa = xp_recompensa
        self.lenda = lenda

    def agir(self, aliados: list["Monstro"], inimigos: list[Combatente]) -> str:
        """
        Turno do monstro — mesma assinatura de `Personagem.agir`.

        Essa simetria é proposital: o motor de batalha chama `agir(aliados,
        inimigos)` sem se importar se o objeto é herói ou monstro. Se as
        assinaturas fossem diferentes, o motor precisaria de um `if isinstance`
        — exatamente o tipo de código que o polimorfismo existe para eliminar.
        """
        alvo = self.escolher_alvo(inimigos)
        if alvo is None:
            return colorir(f"   {self.nome} rosna para o vazio.", Cor.CINZA)
        return self.atacar(alvo)

    def atacar(self, alvo: Combatente) -> str:
        """Ataque padrão: físico ou mágico, conforme `tipo_ataque`."""
        if self.tipo_ataque == "magico":
            return self._aplicar_golpe(
                alvo, self.matk, alvo.mdefense, "Investida Mágica",
                tipo="mágico", critico=rolar_critico(self.speed),
                cor=Cor.MAGENTA_CLARO,
            )
        return self._aplicar_golpe(
            alvo, self.atk, alvo.defense, "Investida",
            tipo="físico", critico=rolar_critico(self.speed),
            cor=Cor.VERMELHO_CLARO,
        )

    def __str__(self) -> str:
        return f"{self.nome} [monstro] (HP {self.hp}/{self.hp_max})"


# ===========================================================================
# AS CRIATURAS
# ===========================================================================


class Saci(Monstro):
    """
    Saci-Pererê — o moleque de uma perna só, redemoinho e cachimbo.

    Mecânica: velocidade absurda (quase sempre começa o combate) e chance de
    atacar duas vezes.
    IA: persegue o herói MAIS LENTO, porque gosta de pregar peça em quem não
    consegue acompanhá-lo.
    """

    def __init__(self, nome: str = "Saci-Pererê") -> None:
        super().__init__(
            nome,
            hp=110, mp=40, speed=32, atk=27, matk=14, defense=8, mdefense=11,
            tipo_ataque="fisico", xp_recompensa=45,
            lenda="Redemoinho de poeira, gargalhada e cachimbo aceso.",
        )

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: caça o mais lento do grupo."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return min(vivos, key=lambda alvo: alvo.speed) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        """SOBRESCRITA: rajada rápida com 45% de chance de um segundo golpe."""
        linhas = [
            self._aplicar_golpe(
                alvo, self.atk, alvo.defense, "Redemoinho",
                tipo="físico", critico=rolar_critico(self.speed),
                cor=Cor.AMARELO_CLARO,
            )
        ]
        if alvo.esta_vivo and random.random() < 0.45:
            linhas.append(
                self._aplicar_golpe(
                    alvo, int(self.atk * 0.6), alvo.defense,
                    "Peteleco do Cachimbo", tipo="físico", cor=Cor.AMARELO,
                )
            )
        return "\n".join(linhas)


class Curupira(Monstro):
    """
    Curupira — guardião da mata, de pés virados para trás.

    Mecânica: defesa física altíssima. Um Guerreiro leva muito tempo para
    derrubá-lo; um Mago passa por cima dele, porque a defesa MÁGICA é baixa.
    Isso cria uma decisão tática real: quem eu mando enfrentar o quê.
    IA: encara o herói de MAIOR ATK — ele protege a floresta atacando a maior
    ameaça primeiro.
    """

    def __init__(self, nome: str = "Curupira") -> None:
        super().__init__(
            nome,
            hp=140, mp=30, speed=18, atk=29, matk=10, defense=17, mdefense=10,
            tipo_ataque="fisico", xp_recompensa=70,
            lenda="Pés virados para trás. Quem o segue, se perde para sempre.",
        )

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: vai para cima do inimigo mais perigoso fisicamente."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return max(vivos, key=lambda alvo: alvo.atk) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        return self._aplicar_golpe(
            alvo, self.atk, alvo.defense, "Golpe de Raiz",
            tipo="físico", critico=rolar_critico(self.speed),
            cor=Cor.VERDE,
        )


class Boitata(Monstro):
    """
    Boitatá — a serpente de fogo que protege os campos.

    Mecânica: puro dano mágico, ignora defesa física. É o contraponto do
    Curupira: quem tem mdefense baixa derrete.
    IA: procura o herói de MENOR MDEFENSE — vai onde o fogo queima mais.
    """

    def __init__(self, nome: str = "Boitatá") -> None:
        super().__init__(
            nome,
            hp=115, mp=90, speed=16, atk=12, matk=35, defense=11, mdefense=14,
            tipo_ataque="magico", xp_recompensa=75,
            lenda="Cobra de fogo cujos olhos enxergam no escuro da noite.",
        )

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: busca a menor resistência mágica."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return min(vivos, key=lambda alvo: alvo.mdefense) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        return self._aplicar_golpe(
            alvo, self.matk, alvo.mdefense, "Língua de Fogo",
            tipo="mágico", critico=rolar_critico(self.speed),
            cor=Cor.VERMELHO_CLARO,
        )


class MulaSemCabeca(Monstro):
    """
    Mula-sem-Cabeça — coice de fogo, fúria cega.

    Mecânica: o maior ATK do jogo com a menor defesa. Mata rápido e morre
    rápido — o clássico "glass cannon".
    IA: executora. Vai sempre no herói de MENOR HP para finalizar.
    """

    def __init__(self, nome: str = "Mula-sem-Cabeça") -> None:
        super().__init__(
            nome,
            hp=100, mp=20, speed=23, atk=36, matk=8, defense=7, mdefense=9,
            tipo_ataque="fisico", xp_recompensa=65,
            lenda="Galopa soltando fogo pelo pescoço onde deveria haver cabeça.",
        )

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: finaliza quem já está caindo."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return min(vivos, key=lambda alvo: alvo.hp) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        return self._aplicar_golpe(
            alvo, self.atk, alvo.defense, "Coice Flamejante",
            tipo="físico", critico=rolar_critico(self.speed),
            cor=Cor.VERMELHO,
        )


class Iara(Monstro):
    """
    Iara — a mãe-d'água, sereia dos rios que encanta quem a escuta.

    Identidade mecânica — SUPORTE INIMIGO: é o espelho da Benzedeira. Ela
    sobrescreve `agir()` para CURAR o aliado mais ferido em vez de atacar.
    Foi criada justamente para resolver um desequilíbrio que a simulação em
    massa revelou: sem uma curandeira do lado dos monstros, o time dos heróis
    vencia 100% dos combates 3v3.

    IA de ataque: quando não precisa curar, alveja o herói de menor mdefense.
    """

    CUSTO_ENCANTO = 18
    LIMIAR_CURA = 0.50
    PODER_CURA = 36

    def __init__(self, nome: str = "Iara") -> None:
        super().__init__(
            nome,
            hp=110, mp=120, speed=19, atk=12, matk=26, defense=12, mdefense=18,
            tipo_ataque="magico", xp_recompensa=80,
            lenda="Canta na beira do rio; quem escuta, mergulha e não volta.",
        )

    def agir(self, aliados: list["Monstro"], inimigos: list[Combatente]) -> str:
        """
        SOBRESCRITA do turno: curar tem prioridade sobre atacar.

        Mesma estrutura da Benzedeira — e é exatamente esse o ponto. Duas
        classes de hierarquias diferentes (`Personagem` e `Monstro`) resolvem o
        mesmo problema com o mesmo formato de método, e o motor de batalha
        chama as duas da mesma forma, sem saber a diferença.
        """
        candidatos = [a for a in aliados if a.esta_vivo]
        if candidatos:
            mais_ferido = min(candidatos, key=lambda a: a.percentual_vida)
            if (
                mais_ferido.percentual_vida < self.LIMIAR_CURA
                and self.gastar_mana(self.CUSTO_ENCANTO)
            ):
                # Mesma regra da Benzedeira: o canto vale metade em si mesma.
                poder = self.PODER_CURA
                if mais_ferido is self:
                    poder = int(poder * FATOR_AUTOCURA)
                curado = mais_ferido.curar(poder)
                quem = "si mesma" if mais_ferido is self else mais_ferido.nome
                return (
                    f"   {self.nome} entoa o "
                    f"{colorir('Canto das Águas', Cor.CIANO_CLARO)} sobre {quem} → "
                    f"{colorir(f'+{curado}', Cor.VERDE_CLARO)} de vida."
                )

        return super().agir(aliados, inimigos)

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: afoga quem tem menos resistência mágica."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return min(vivos, key=lambda alvo: alvo.mdefense) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        return self._aplicar_golpe(
            alvo, self.matk, alvo.mdefense, "Torrente",
            tipo="mágico", critico=rolar_critico(self.speed),
            cor=Cor.AZUL_CLARO,
        )


class Cuca(Monstro):
    """
    Cuca — a bruxa-jacaré que rouba o sono das crianças.

    Mecânica: além do dano mágico, DRENA MANA do alvo. É a criatura mais
    perigosa contra Mago e Benzedeira, porque ataca o recurso deles, não só a
    vida. Mostra um ataque que faz duas coisas ao mesmo tempo.
    IA: alveja quem tem MAIS MANA — quem ela puder sabotar melhor.
    """

    DRENO_MANA = 9

    def __init__(self, nome: str = "Cuca") -> None:
        super().__init__(
            nome,
            hp=130, mp=100, speed=14, atk=15, matk=28, defense=12, mdefense=16,
            tipo_ataque="magico", xp_recompensa=85,
            lenda="Dorme um olho de cada vez, e canta para as crianças não acordarem.",
        )

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: prefere sabotar o conjurador com mais mana."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return max(vivos, key=lambda alvo: alvo.mp) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        """
        SOBRESCRITA: dano mágico + roubo de mana.

        Compõe a narração em duas partes: a linha padrão do golpe, devolvida
        por `_aplicar_golpe`, mais uma linha extra sobre o dreno — mas só se
        realmente houve mana para drenar.
        """
        texto = self._aplicar_golpe(
            alvo, self.matk, alvo.mdefense, "Canto da Cuca",
            tipo="mágico", critico=rolar_critico(self.speed),
            cor=Cor.MAGENTA,
        )

        mana_antes = alvo.mp
        alvo.mp = alvo.mp - self.DRENO_MANA
        drenado = mana_antes - alvo.mp

        if drenado > 0:
            self.recuperar_mana(drenado)
            texto += colorir(
                f"\n   O canto rouba {drenado} de mana de {alvo.nome}!", Cor.MAGENTA
            )
        return texto
