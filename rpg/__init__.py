# -*- coding: utf-8 -*-
"""
Pacote `rpg` — sistema de batalha por turnos com Programação Orientada a Objetos.

CP2 de Python — FIAP.
Tema: folclore brasileiro.

Módulos:
    utils       -> apresentação no terminal (cores, barras, entrada de dados)
    combatente  -> classe abstrata base com os 7 atributos obrigatórios
    personagens -> Personagem + Guerreiro, Mago, Capoeirista, Benzedeira
    monstros    -> Monstro + Saci, Curupira, Boitatá, Mula-sem-Cabeça, Cuca, Iara
    batalha     -> Time, Batalha (abstrata), Batalha1v1, Batalha3v3
    elenco      -> fábricas que instanciam os objetos do jogo
"""

__version__ = "1.0.0"
