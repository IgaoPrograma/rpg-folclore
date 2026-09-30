# -*- coding: utf-8 -*-
"""
Heróis jogáveis: a classe-pai `Personagem` e suas quatro filhas.

Atende aos requisitos 2, 3 e 4 do enunciado:
  • `Personagem` é uma das duas classes-pai exigidas;
  • `Guerreiro` e `Mago` são obrigatórias e herdam dela;
  • `Capoeirista` e `Benzedeira` são as classes inéditas criadas pelo grupo,
    cada uma com regra própria de atributos e sobrescrita do método de ataque.

Tema do trabalho: FOLCLORE BRASILEIRO. Os heróis são figuras do sertão e da
mata que enfrentam as criaturas das lendas.
"""

from __future__ import annotations

import random

from rpg.combatente import FATOR_AUTOCURA, Combatente, rolar_critico
from rpg.utils import Cor, colorir


class Personagem(Combatente):
    """
    Classe-pai de todos os heróis jogáveis.

    O que ela acrescenta em relação a `Combatente`:
      • identidade de RPG (classe, nível, xp, descrição);
      • o método `agir()`, que representa o TURNO COMPLETO do herói;
      • uma estratégia padrão de escolha de alvo.

    Por que `agir()` existe separado de `atacar()`?
    ------------------------------------------------
    Nem todo turno é um ataque. A Benzedeira, por exemplo, pode decidir curar
    um aliado em vez de bater. Se o motor de batalha chamasse `atacar()`
    diretamente, ela não teria como fazer isso.

    Então dividimos a responsabilidade em dois níveis de polimorfismo:
        agir()   -> "o que eu faço no meu turno?"   (Benzedeira sobrescreve)
        atacar() -> "como é o meu golpe?"           (todas sobrescrevem)

    O motor chama sempre `agir()`, e o comportamento padrão de `agir()` é
    simplesmente escolher um alvo e atacar.
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
        classe: str,
        descricao: str = "",
    ) -> None:
        # super() chama o __init__ da classe-pai (Combatente), que cuida dos
        # sete atributos obrigatórios. Sem isso teríamos que repetir sete
        # atribuições aqui — é exatamente o que a herança evita.
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
        self.classe = classe
        self.descricao = descricao
        self.nivel = 1
        self.xp = 0

    # ------------------------------------------------------------------
    # Turno
    # ------------------------------------------------------------------
    def agir(self, aliados: list["Personagem"], inimigos: list[Combatente]) -> str:
        """
        Executa o turno do herói. Comportamento padrão: escolher alvo e atacar.

        Entrada : lista de aliados (para classes de suporte) e de inimigos.
        Processo: seleciona um alvo vivo e delega para `atacar()`.
        Saída   : texto narrando o que aconteceu no turno.
        """
        alvo = self.escolher_alvo(inimigos)
        if alvo is None:
            return colorir(f"   {self.nome} não encontra inimigos de pé.", Cor.CINZA)
        return self.atacar(alvo)

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """
        Estratégia PADRÃO dos heróis: focar em quem está mais machucado.

        Cada classe filha sobrescreve isso com a própria doutrina de combate —
        e isso não é só enfeite narrativo: a simulação de balanceamento mostrou
        que, quando os três heróis focavam o mesmo alvo e cada monstro atacava
        um alvo diferente, os heróis venciam 99% dos combates 3v3. Dano
        concentrado derruba inimigos mais cedo, e inimigo morto não revida.

        Dar doutrina própria a cada herói equilibrou o 3v3 sem mexer em um
        único atributo — a correção veio do comportamento, não dos números.
        """
        vivos = [i for i in inimigos if i.esta_vivo]
        if not vivos:
            return None
        return min(vivos, key=lambda alvo: alvo.hp)

    # ------------------------------------------------------------------
    # Progressão
    # ------------------------------------------------------------------
    def ganhar_xp(self, quantidade: int) -> str | None:
        """
        Acumula experiência e sobe de nível a cada 100 pontos.

        Não é exigido pelo enunciado — entra como camada de criatividade e
        mostra um método que altera o estado interno do objeto ao longo do jogo.
        """
        self.xp += quantidade
        if self.xp < self.nivel * 100:
            return None

        self.xp -= self.nivel * 100
        self.nivel += 1
        self._hp_max += 10
        self.hp = self.hp + 10
        self.atk += 2
        self.matk += 2
        self.defense += 1
        self.mdefense += 1
        return colorir(
            f"   ✦ {self.nome} subiu para o nível {self.nivel}!", Cor.AMARELO_CLARO
        )

    def __str__(self) -> str:
        return f"{self.nome}, {self.classe} (HP {self.hp}/{self.hp_max})"


# ===========================================================================
# CLASSES OBRIGATÓRIAS
# ===========================================================================


class Guerreiro(Personagem):
    """
    O Cangaceiro do sertão: couro grosso, facão pesado e teimosia.

    Identidade mecânica — FÚRIA DO SERTÃO: quando a vida cai abaixo de 40%,
    o ataque físico aumenta 50%. É um herói que fica mais perigoso quanto mais
    perto da morte está, o que recompensa quem o mantém na linha de frente.

    Atributos: muito hp/atk/defense, quase nenhum mp/matk.
    """

    LIMIAR_FURIA = 0.40
    BONUS_FURIA = 1.5

    def __init__(self, nome: str) -> None:
        super().__init__(
            nome,
            hp=135,
            mp=20,
            speed=12,
            atk=27,
            matk=4,
            defense=14,
            mdefense=8,
            classe="Guerreiro",
            descricao="Cangaceiro de couro e facão. Fica mais forte quando sangra.",
        )

    @property
    def em_furia(self) -> bool:
        """True quando a vida está abaixo do limiar que dispara a fúria."""
        return self.percentual_vida <= self.LIMIAR_FURIA

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: o cangaceiro encara de frente o inimigo mais forte."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return max(vivos, key=lambda alvo: alvo.atk) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        """
        SOBRESCRITA (polimorfismo): golpe físico puro, com bônus se em fúria.

        Fluxo: define o poder -> checa fúria -> sorteia crítico -> aplica.
        """
        poder = self.atk
        nome_golpe = "Talho de Facão"

        if self.em_furia:
            poder = int(self.atk * self.BONUS_FURIA)
            nome_golpe = "FÚRIA DO SERTÃO"

        critico = rolar_critico(self.speed)
        return self._aplicar_golpe(
            alvo,
            poder,
            alvo.defense,          # ataque físico é reduzido pela defesa física
            nome_golpe,
            tipo="físico",
            critico=critico,
            cor=Cor.VERMELHO_CLARO,
        )


class Mago(Personagem):
    """
    O Pajé: domina as forças da mata, mas depende inteiramente da mana.

    Identidade mecânica — GESTÃO DE MANA: a magia custa 12 de MP e é devastadora.
    Quando a mana acaba, ele NÃO fica inútil: recorre a uma bordoada de cajado,
    fraca e física. Isso mostra um `atacar()` com dois caminhos possíveis.

    Atributos: muito mp/matk, pouco hp e defesa física.
    """

    CUSTO_MAGIA = 12

    def __init__(self, nome: str) -> None:
        super().__init__(
            nome,
            hp=105,
            mp=150,
            speed=14,
            atk=10,
            matk=34,
            defense=10,
            mdefense=15,
            classe="Mago",
            descricao="Pajé que canaliza a mata. Devastador — enquanto houver mana.",
        )

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: o pajé calcula — queima quem tem menos defesa mágica."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return min(vivos, key=lambda alvo: alvo.mdefense) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        """
        SOBRESCRITA: tenta magia; se faltar mana, cai para o ataque físico.

        Repare que `gastar_mana` devolve False quando não há MP suficiente —
        é esse retorno que controla o desvio do fluxo.
        """
        if self.gastar_mana(self.CUSTO_MAGIA):
            critico = rolar_critico(self.speed)
            return self._aplicar_golpe(
                alvo,
                self.matk,
                alvo.mdefense,      # ataque mágico é reduzido pela defesa mágica
                "Sopro da Mata",
                tipo="mágico",
                critico=critico,
                cor=Cor.MAGENTA_CLARO,
            )

        return self._aplicar_golpe(
            alvo,
            self.atk,
            alvo.defense,
            "Bordoada de Cajado (sem mana!)",
            tipo="físico",
            cor=Cor.CINZA,
        )


# ===========================================================================
# CLASSES INÉDITAS CRIADAS PELO GRUPO (requisito 4)
# ===========================================================================


class Capoeirista(Personagem):
    """
    CLASSE INÉDITA #1 — o Capoeirista da roda.

    Identidade mecânica, construída em cima da velocidade:

      • GINGA (ataque): depois do primeiro golpe, há chance de emendar um
        segundo ("Meia-Lua de Compasso"). A chance é speed/55, limitada a 55%.
      • ESQUIVA (defesa): sobrescreve `receber_dano` para às vezes anular o
        golpe por completo. Chance = speed/80, limitada a 28%.

    Essa classe é o melhor exemplo de polimorfismo do projeto, porque
    sobrescreve DOIS métodos herdados com comportamentos diferentes: um
    ofensivo (`atacar`) e um defensivo (`receber_dano`).

    Atributos: speed altíssima, atk mediano, defesas baixas — vive de não ser
    acertado, não de aguentar pancada.
    """

    LIMITE_COMBO = 0.55
    LIMITE_ESQUIVA = 0.28

    def __init__(self, nome: str) -> None:
        super().__init__(
            nome,
            hp=115,
            mp=45,
            speed=28,
            atk=26,
            matk=12,
            defense=11,
            mdefense=12,
            classe="Capoeirista",
            descricao="Mestre de roda. Quase nunca é acertado, quase sempre bate duas vezes.",
        )

    @property
    def chance_combo(self) -> float:
        """Probabilidade de emendar o segundo golpe, derivada da velocidade."""
        return min(self.LIMITE_COMBO, self.speed / 55)

    @property
    def chance_esquiva(self) -> float:
        """Probabilidade de anular um golpe recebido, derivada da velocidade."""
        return min(self.LIMITE_ESQUIVA, self.speed / 80)

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: só respeita quem acompanha o ritmo — vai no mais rápido."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return max(vivos, key=lambda alvo: alvo.speed) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        """
        SOBRESCRITA ofensiva: um golpe garantido + chance de um segundo.

        Saída: a narração pode conter DUAS linhas (uma por golpe), o que é
        perfeitamente compatível com o motor de batalha — ele só imprime o
        texto que recebe, sem supor quantas linhas virão.
        """
        critico = rolar_critico(self.speed)
        linhas = [
            self._aplicar_golpe(
                alvo,
                self.atk,
                alvo.defense,
                "Armada",
                tipo="físico",
                critico=critico,
                cor=Cor.VERDE_CLARO,
            )
        ]

        # Só tenta o combo se o alvo ainda estiver de pé — bater em quem já caiu
        # seria desperdício (e ficaria estranho na narração).
        if alvo.esta_vivo and random.random() < self.chance_combo:
            linhas.append(
                self._aplicar_golpe(
                    alvo,
                    int(self.atk * 0.7),   # o segundo golpe é mais leve
                    alvo.defense,
                    "Meia-Lua de Compasso (combo!)",
                    tipo="físico",
                    critico=rolar_critico(self.speed),
                    cor=Cor.CIANO_CLARO,
                )
            )

        return "\n".join(linhas)

    def receber_dano(self, dano: int) -> int:
        """
        SOBRESCRITA defensiva: chance de esquivar e zerar o dano.

        Devolver 0 é o contrato combinado em `Combatente.receber_dano`: o
        atacante lê esse zero e narra "escapou ileso" automaticamente. Ou seja,
        adicionamos uma mecânica nova SEM tocar em uma linha sequer do motor
        de batalha nem das outras classes. Isso é o ganho prático do
        polimorfismo.
        """
        if random.random() < self.chance_esquiva:
            return 0

        # super() aqui chama a implementação original da classe-pai, que faz a
        # subtração de vida de verdade. Estendemos o comportamento, não o
        # substituímos por completo.
        return super().receber_dano(dano)


class Benzedeira(Personagem):
    """
    CLASSE INÉDITA #2 — a Benzedeira, curandeira de terreiro.

    Identidade mecânica — DECISÃO DE TURNO: ela é a única classe jogável que
    sobrescreve `agir()`. Antes de atacar, ela olha o time inteiro; se algum
    aliado (ou ela mesma) estiver abaixo de 50% de vida e houver mana, ela REZA
    e cura em vez de atacar. Isso transforma o 3v3 num combate com suporte de
    verdade.

    No 1v1 ela é autossuficiente, mas a autocura vale metade — senão o duelo
    nunca terminaria.

    Atributos: mp e mdefense altos, atk baixo, matk decente.
    """

    CUSTO_REZA = 16
    CUSTO_MAGIA = 10
    LIMIAR_CURA = 0.50
    PODER_CURA = 38

    def __init__(self, nome: str) -> None:
        super().__init__(
            nome,
            hp=120,
            mp=110,
            speed=17,
            atk=13,
            matk=32,
            defense=13,
            mdefense=19,
            classe="Benzedeira",
            descricao="Cura com reza forte e ataca com oração de fogo. O coração do time.",
        )

    def agir(self, aliados: list[Personagem], inimigos: list[Combatente]) -> str:
        """
        SOBRESCRITA do turno inteiro: curar tem prioridade sobre atacar.

        Entrada : aliados vivos do time e inimigos vivos.
        Processo: procura o aliado vivo mais ferido; se ele estiver abaixo de
                  50% da vida e houver mana, reza. Caso contrário, ataca
                  chamando `super().agir(...)`, que reusa a lógica da classe-pai.
        Saída   : narração do turno.
        """
        candidatos = [a for a in aliados if a.esta_vivo]
        if candidatos:
            mais_ferido = min(candidatos, key=lambda a: a.percentual_vida)
            precisa_cura = mais_ferido.percentual_vida < self.LIMIAR_CURA

            if precisa_cura and self.gastar_mana(self.CUSTO_REZA):
                # "A reza é mais forte nos outros": curar a si mesma rende
                # metade. Sem essa regra, a Benzedeira se curava indefinidamente
                # no 1v1 e o duelo nunca terminava — foi o que a simulação de
                # balanceamento mostrou.
                poder = self.PODER_CURA
                if mais_ferido is self:
                    poder = int(poder * FATOR_AUTOCURA)
                curado = mais_ferido.curar(poder)
                quem = "si mesma" if mais_ferido is self else mais_ferido.nome
                return (
                    f"   {self.nome} fez uma "
                    f"{colorir('Reza Forte', Cor.VERDE_CLARO)} em {quem} → "
                    f"{colorir(f'+{curado}', Cor.VERDE_CLARO)} de vida."
                )

        # Ninguém precisa de cura (ou faltou mana): age como um herói normal.
        return super().agir(aliados, inimigos)

    def escolher_alvo(self, inimigos: list[Combatente]) -> Combatente | None:
        """SOBRESCRITA: a oração de fogo busca a menor resistência mágica."""
        vivos = [i for i in inimigos if i.esta_vivo]
        return min(vivos, key=lambda alvo: alvo.mdefense) if vivos else None

    def atacar(self, alvo: Combatente) -> str:
        """SOBRESCRITA: oração de fogo (mágica) ou galho seco quando sem mana."""
        if self.gastar_mana(self.CUSTO_MAGIA):
            return self._aplicar_golpe(
                alvo,
                self.matk,
                alvo.mdefense,
                "Oração de Fogo",
                tipo="mágico",
                critico=rolar_critico(self.speed),
                cor=Cor.AMARELO_CLARO,
            )

        return self._aplicar_golpe(
            alvo,
            self.atk,
            alvo.defense,
            "Pancada de Galho Seco (sem mana!)",
            tipo="físico",
            cor=Cor.CINZA,
        )
