# RPG das Lendas — Sistema de Batalha com POO

Sistema de combate por turnos em Python, construído para o **CP2 de Python**
(Programação Orientada a Objetos) — FIAP.

Em vez do cenário medieval de sempre, o tema é o **folclore brasileiro**:
heróis do sertão e da roda de capoeira enfrentam Saci, Curupira, Boitatá,
Mula-sem-Cabeça, Cuca e Iara.

---

## Integrantes

| Nome | RM |
|------|-----|
| Caio Ryan Velten Alves | 572913 |
| Carlos Alberto Oliveira Nascimento | 565694 |
| Davi França Aranda | 572751 |
| João Vitor Fernandes Gomes | 573882 |
| Murilo de Oliveira Moreira | 573534 |

---

## Como executar

Não há dependências externas — só a biblioteca padrão do **Python 3.10+**.

```bash
# menu interativo
python main.py

# roda um 1v1 e um 3v3 automaticamente, sem precisar digitar nada
python main.py --demo

# desliga as cores ANSI (terminais antigos ou saída para arquivo)
python main.py --sem-cor

# ferramenta de balanceamento: simula centenas de combates e mede
python ferramentas/simulacao_balanceamento.py
```

---

## Estrutura do projeto

```
rpg-folclore/
├── main.py                              # interface: menus, prints e inputs
├── README.md
├── rpg/
│   ├── __init__.py
│   ├── combatente.py                    # classe abstrata base + fórmula de dano
│   ├── personagens.py                   # Personagem + 4 classes jogáveis
│   ├── monstros.py                      # Monstro + 6 criaturas do folclore
│   ├── batalha.py                       # Time, Batalha, Batalha1v1, Batalha3v3
│   ├── elenco.py                        # instanciação dos objetos (fábricas)
│   └── utils.py                         # cores, barras de vida, entrada de dados
└── ferramentas/
    └── simulacao_balanceamento.py       # simulador usado para balancear o jogo
```

A regra de negócio do combate está toda dentro de `rpg/`. O `main.py` só cuida
da interface. Dá para trocar o terminal por uma interface web sem alterar uma
linha das classes.

---

## Hierarquia de classes

```
Combatente (classe abstrata — define os 7 atributos obrigatórios)
│
├── Personagem  (classe-pai dos heróis)
│   ├── Guerreiro     → Fúria do Sertão: +50% de ataque abaixo de 40% de vida
│   ├── Mago          → gasta mana; sem mana, recorre à bordoada de cajado
│   ├── Capoeirista   ★ INÉDITA: combo duplo + esquiva que anula o golpe
│   └── Benzedeira    ★ INÉDITA: cura o aliado mais ferido em vez de atacar
│
└── Monstro     (classe-pai das criaturas)
    ├── Saci            → velocidade extrema, ataque duplo
    ├── Curupira        → muralha física (mas frágil contra magia)
    ├── Boitatá         → dano mágico puro
    ├── Mula-sem-Cabeça → maior ataque do jogo, menor defesa
    ├── Cuca            → dano mágico + drena a mana do alvo
    └── Iara            → curandeira do lado dos monstros
```

### Por que existe a classe `Combatente`?

O enunciado exige duas classes-pai (`Personagem` e `Monstro`) e que **ambas**
tenham os sete atributos obrigatórios. Havia dois caminhos:

- **(A)** copiar os sete atributos dentro de cada uma das duas classes;
- **(B)** criar um ancestral comum que os define uma única vez.

Escolhemos **(B)**. O enunciado autoriza explicitamente ("devem herdar **ou
implementar** uma estrutura que contenha obrigatoriamente..."), e assim evitamos
duplicar código — princípio DRY (*Don't Repeat Yourself*).

`Personagem` e `Monstro` continuam sendo classes-pai de verdade: são elas que
Guerreiro/Mago/Capoeirista/Benzedeira e Saci/Curupira/etc. herdam.

O ganho prático: como herói e monstro compartilham o mesmo ancestral, o motor
de batalha trata os dois de forma idêntica. É isso que permite escrever
`atacante.agir(aliados, inimigos)` sem nunca perguntar "isso é um herói ou um
monstro?".

---

## Atributos dos combatentes

Os sete atributos obrigatórios estão definidos em `Combatente.__init__`:

| Atributo | Significado | Onde é usado |
|----------|-------------|--------------|
| `hp` | vida | condição de derrota (`hp <= 0`) |
| `mp` | mana | custo das magias e das curas |
| `speed` | velocidade | **define a ordem dos turnos** e a chance de crítico |
| `atk` | ataque físico | dano físico |
| `matk` | ataque mágico | dano mágico |
| `defense` | defesa física | reduz o dano físico recebido |
| `mdefense` | defesa mágica | reduz o dano mágico recebido |

### Heróis

| Classe | HP | MP | SPD | ATK | MATK | DEF | MDEF |
|--------|----|----|-----|-----|------|-----|------|
| Guerreiro | 135 | 20 | 12 | 27 | 4 | 14 | 8 |
| Mago | 105 | 150 | 14 | 10 | 34 | 10 | 15 |
| Capoeirista | 115 | 45 | 28 | 26 | 12 | 11 | 12 |
| Benzedeira | 120 | 110 | 17 | 13 | 32 | 13 | 19 |

### Monstros

| Criatura | HP | MP | SPD | ATK | MATK | DEF | MDEF |
|----------|----|----|-----|-----|------|-----|------|
| Saci-Pererê | 110 | 40 | 32 | 27 | 14 | 8 | 11 |
| Curupira | 140 | 30 | 18 | 29 | 10 | 17 | 10 |
| Boitatá | 115 | 90 | 16 | 12 | 35 | 11 | 14 |
| Mula-sem-Cabeça | 100 | 20 | 23 | 36 | 8 | 7 | 9 |
| Cuca | 130 | 100 | 14 | 15 | 28 | 12 | 16 |
| Iara | 110 | 120 | 19 | 12 | 26 | 12 | 18 |

---

## Como funciona o combate

### Cálculo de dano

A fórmula base é a pedida no enunciado:

```
dano = ataque        - defesa          (golpe físico)
dano = ataque_mágico - defesa_mágica   (golpe mágico)
```

Em cima dela colocamos três camadas:

1. **Piso proporcional** — se a defesa anular o ataque, o golpe ainda passa 10%
   do poder do atacante.
2. **Variação de ±15%** — o mesmo golpe nunca tira exatamente o mesmo número.
3. **Crítico** — multiplica o dano por 1,8; a chance cresce com a `speed`.

### Ordem dos turnos

A `speed` decide quem ataca primeiro, como pede o enunciado. No 3v3, os **seis**
combatentes entram numa única fila ordenada por velocidade. Empates são
desempatados por sorteio (embaralhamos antes de ordenar, porque o `sorted` do
Python é estável e, sem isso, o primeiro da lista venceria sempre).

### Seleção de alvos

Cada classe tem a própria doutrina de combate — e isso é mecânica, não enfeite:

| Combatente | Mira em |
|------------|---------|
| Guerreiro | maior `atk` (encara a maior ameaça) |
| Mago | menor `mdefense` (maximiza o dano mágico) |
| Capoeirista | maior `speed` (só respeita quem acompanha o ritmo) |
| Benzedeira | cura o aliado mais ferido; senão, menor `mdefense` |
| Saci | menor `speed` (gosta de atormentar os lentos) |
| Curupira | maior `atk` (protege a mata da maior ameaça) |
| Boitatá | menor `mdefense` |
| Mula-sem-Cabeça | menor `hp` (executora) |
| Cuca | maior `mp` (sabota conjuradores) |
| Iara | cura o aliado mais ferido; senão, menor `mdefense` |

### Condição de vitória

Um time perde quando **todos** os seus membros ficam com `hp <= 0`, conforme o
enunciado. Implementado em `Time.derrotado`.

---

## Balanceamento orientado a dados

Balancear "no olho" não funciona, então escrevemos
`ferramentas/simulacao_balanceamento.py`, que roda cada confronto possível
centenas de vezes em silêncio e mede taxa de vitória e duração.

Ele encontrou quatro problemas reais que jamais apareceriam jogando algumas
partidas na mão:

1. **Combate infinito.** Na primeira versão dos atributos, o Capoeirista
   (atk 23) contra o Curupira (defense 24) causava 1 de dano por golpe. → Criamos o **piso proporcional de dano**.
2. **Heróis venciam 100% dos 3v3.** Só o time deles tinha curandeira.
   → Criamos a **Iara**, a curandeira do lado dos monstros.
3. **A Cuca vencia 100% contra Mago e Benzedeira** apenas drenando mana, sem
   dano. → Criamos a **regeneração de mana por rodada**.
4. **Heróis ainda venciam 99% dos 3v3**, mesmo perdendo vários duelos 1v1
   individuais. O motivo não estava nos atributos: os três heróis focavam o
   mesmo alvo (dano concentrado) enquanto cada monstro atacava um alvo
   diferente (dano espalhado) — e inimigo morto não revida. → Demos **doutrina
   de alvo própria a cada herói**. A correção veio do comportamento, não dos
   números — e de quebra rendeu mais polimorfismo.

**Resultado:** o 3v3 principal (Guardiões do Sertão x Lendas da Noite) fica
equilibrado, em torno de 55% para os heróis.

No 1v1 existem confrontos desiguais **de propósito** — é um sistema de
vantagens táticas, estilo pedra-papel-tesoura. O Curupira, com defesa física
alta, é o pesadelo do Capoeirista; mas o Mago o derrete, porque a defesa
mágica dele é baixa. Escolher quem enfrenta o quê é parte do jogo.

---

## Onde cada conceito de POO aparece

| Conceito | Onde ver |
|----------|----------|
| **Classe e objeto** | `rpg/elenco.py` — as fábricas instanciam heróis e monstros |
| **Atributos** | `Combatente.__init__` — os sete atributos obrigatórios |
| **Métodos** | `atacar()`, `agir()`, `curar()`, `receber_dano()`, `gastar_mana()` |
| **Herança simples** | `Guerreiro(Personagem)`, `Saci(Monstro)` |
| **Herança em múltiplos níveis** | `Combatente → Personagem → Guerreiro` |
| **Classe abstrata** | `Combatente(ABC)` e `Batalha(ABC)` com `@abstractmethod` |
| **Polimorfismo** | `atacar()` tem 10 implementações diferentes; o motor chama uma linha só |
| **Sobrescrita (override)** | `Capoeirista.receber_dano()` anula o golpe; `Benzedeira.agir()` cura |
| **`super()`** | todos os `__init__` das filhas; `Capoeirista.receber_dano()` e `Benzedeira.agir()` estendem o pai em vez de substituí-lo |
| **Encapsulamento** | `hp` e `mp` são `@property` com setter que trava o valor entre 0 e o máximo |
| **Composição** | `Time` **tem** combatentes (não **é** um combatente) |
| **Métodos mágicos** | `__str__`, `__repr__`, `__len__` e `__iter__` |
| **Método estático** | `Batalha.ordenar_por_velocidade()` |

### O exemplo mais claro de polimorfismo

O motor de batalha inteiro resolve um turno com **uma linha**:

```python
self.narrar(atacante.agir(aliados_time.vivos, inimigos_time.vivos))
```

Essa linha funciona para Guerreiro, Mago, Capoeirista, Benzedeira, Saci,
Curupira, Boitatá, Mula-sem-Cabeça, Cuca e Iara. Cada objeto sabe como é o
próprio turno. Em nenhum momento o motor escreve `if isinstance(...)`.

Consequência prática: para adicionar um Arqueiro ou um Boto ao jogo, basta
criar a classe nova. **Nenhuma linha de `batalha.py` precisa mudar.**

### O segundo exemplo, mais sutil

O `Capoeirista` sobrescreve `receber_dano()` para às vezes devolver `0`, o que
significa "o golpe foi anulado". Quem ataca lê esse zero e narra "escapou
ileso" sozinho. Ou seja: adicionamos uma mecânica de esquiva **sem tocar em uma
linha sequer** do motor de batalha nem das outras nove classes.

---

## Requisitos do enunciado

| # | Requisito | Onde está |
|---|-----------|-----------|
| 1 | 7 atributos obrigatórios em heróis e monstros | `Combatente.__init__` — herdado pelas duas hierarquias |
| 2 | Classes-pai `Personagem` e `Monstro` | `rpg/personagens.py` e `rpg/monstros.py` |
| 3 | `Guerreiro` e `Mago` herdando `Personagem` | `rpg/personagens.py` |
| 4 | Ao menos uma classe jogável inédita | **duas**: `Capoeirista` e `Benzedeira` |
| 5 | Instanciar objetos das duas hierarquias | `rpg/elenco.py` |
| 6 | Batalha 1v1 com `speed` e cálculo de dano | `Batalha1v1` em `rpg/batalha.py` |
| 7 | Batalha 3v3 com alvos e condição de vitória | `Batalha3v3` e `Time` em `rpg/batalha.py` |
| 8 | Conceitos de POO empregados | tabela da seção anterior |
| 9 | Repositório GitHub e README | este arquivo |
| 10 | Criatividade | tema de folclore brasileiro; fúria, combo, esquiva, dreno de mana e cura; balanceamento validado por simulação |

---

## Exemplo de saída

Trecho real de um combate 3v3 (Guardiões do Sertão x Lendas da Noite), rodado
com `--sem-cor`:

```
── RODADA 2 ──────────────────────────────────────────────────────────
   Besouro usou Armada em Iara → -26 de dano físico.  ⚡ CRÍTICO!
   Besouro usou Meia-Lua de Compasso (combo!) em Iara → -5 de dano físico.
   Iara entoa o Canto das Águas sobre si mesma → +18 de vida.
   Curupira usou Golpe de Raiz em Lampião → -15 de dano físico.
   Dona Rosa fez uma Reza Forte em Lampião → +38 de vida.
   Boitatá usou Língua de Fogo em Lampião → -29 de dano mágico.
   Lampião usou Talho de Facão em Curupira → -9 de dano físico.

  Guardiões do Sertão
   Lampião                [█████████░░░░░░░░░]   65/135  [▰▰▰▰▰▰▰▰▰▰]  20/20
   Besouro                [██████████████████]  115/115  [▰▰▰▰▰▰▰▰▰▰]  45/45
   Dona Rosa              [██████████████████]  120/120  [▰▰▰▰▰▰▰▰▱▱]  88/110

  Lendas da Noite
   Curupira               [████████████░░░░░░]   96/140  [▰▰▰▰▰▰▰▰▰▰]  30/30
   Boitatá                [██████████████████]  115/115  [▰▰▰▰▰▰▰▰▰▰]  90/90
   Iara                   [███████████░░░░░░░]   70/110  [▰▰▰▰▰▰▰▰▱▱] 102/120
```

Repare como a rodada mostra várias mecânicas ao mesmo tempo: a ordem por
`speed` (Besouro, o mais rápido, age primeiro), o combo e o crítico do
Capoeirista, a Iara curando a si mesma pela metade (+18 em vez de +36), a
Benzedeira curando um aliado ferido (+38) e o dano mágico do Boitatá ignorando
a defesa física do Guerreiro.
