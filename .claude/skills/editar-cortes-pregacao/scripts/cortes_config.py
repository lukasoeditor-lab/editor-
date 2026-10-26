"""Configuração editorial dos cortes. Os tempos são segundos do clipe bruto (raw_X.mp4).

trechos : partes do clipe que ficam (o resto é descartado; pausas longas dentro delas também)
hits    : textos gigantes em momentos-chave. `fala` é a sequência de palavras faladas que dispara
          o texto (achada em ordem na transcrição); `texto` usa "/" para quebrar linha.
          modo "frente" cobre o pastor, "atras" fica atrás dele (efeito de profundidade).
          recorte: True troca o fundo da igreja por um fundo novo durante o texto (use em poucos
          destaques; no resto do vídeo vale a filmagem original).
enfase  : palavras que viram palavra de emoção (serifada, grande) nas legendas.
"""

COMUM = {
    "rotulo_topo": "PR. ERIC MELO",
    "rotulo_sub": "CONFERÊNCIA CONECTADOS",
}

CORTES = {
    # ---- E: "Em mim termina, em mim começa" (clímax) ----
    "E": {
        "musica": {"arquivo": "interstellar.mp3", "inicio": 38.0, "modo": "continuo"},
        "paleta": {"fundo1": "#12040a", "fundo2": "#2c0b12", "luz": "#ff5a2a", "destaque": "#ffb02e"},
        "trechos": [(4.9, 26.4), (28.1, 42.6), (45.2, 50.9), (57.1, 72.5), (73.0, 84.8)],
        "enfase": ["romper", "mentiu", "separa", "escravo", "termina", "começa", "promessa", "chamado", "abençoado"],
        "hits": [
            {"fala": ["você", "será"], "texto": "VOCÊ SERÁ/O QUE OS/SEUS NÃO FORAM", "modo": "frente", "dur": 1.9},
            {"fala": ["pai", "mentiu"], "texto": "O PAI/MENTIU", "modo": "atras", "dur": 1.1},
            {"fala": ["avô", "mentiu"], "texto": "O AVÔ/MENTIU", "modo": "atras", "dur": 1.1},
            {"fala": ["bisavô", "mentiu"], "texto": "O BISAVÔ/MENTIU", "modo": "atras", "dur": 1.2},
            {"fala": ["você", "você", "não"], "texto": "E VOCÊ/NÃO", "modo": "frente", "dur": 1.3},
            {"fala": ["escravo", "do", "alcoolismo"], "texto": "NÃO SERÁ/ESCRAVO", "modo": "atras", "dur": 1.5},
            {"fala": ["chamado", "pra", "romper"], "texto": "CHAMADO/PRA ROMPER", "modo": "frente", "dur": 1.7},
            {"fala": ["mim", "termina"], "texto": "EM MIM/TERMINA", "modo": "frente", "dur": 1.5},
            {"fala": ["mim", "começa"], "texto": "E EM MIM/COMEÇA", "modo": "frente", "dur": 1.6},
            {"fala": ["só", "dependo", "da", "promessa"], "texto": "SÓ DEPENDO/DA PROMESSA/DE DEUS", "modo": "atras", "dur": 2.2},
            {"fala": ["em", "mim", "termina"], "texto": "EM MIM/TERMINA", "modo": "frente", "dur": 1.3},
            {"fala": ["em", "mim", "começa"], "texto": "E EM MIM/COMEÇA", "modo": "frente", "dur": 1.8, "riser": True},
        ],
        "marquee_padrao": "ROMPER",
    },
    # ---- C: "Você viverá o que os seus não viveram" (profecia) ----
    # Só os trechos em que o pastor aparece longe da borda da imagem da transmissão.
    "C": {
        "musica": {"arquivo": "cantforget.mp3", "inicio": 0.0, "modo": "loop", "corte_em": 35.0},
        "paleta": {"fundo1": "#040b1f", "fundo2": "#0a1a44", "luz": "#2a7bff", "destaque": "#4de1ff"},
        "trechos": [(14.7, 24.9), (49.3, 63.95), (72.7, 84.0)],
        # a voz isolada foi gerada sobre a primeira versão do corte; este mapa permite fatiá-la
        "iso_antigo": {"trechos": [(0.6, 63.95), (72.7, 84.0)]},
        "enfase": ["romper", "chega", "chegarão", "viverá", "capacito", "levanto", "nações", "passaporte", "língua", "processos", "liberar"],
        "hits": [
            {"fala": ["vim", "liberar"], "texto": "EU VIM/LIBERAR", "modo": "frente", "dur": 1.5},
            {"fala": ["viverá", "o", "que"], "texto": "VOCÊ VIVERÁ/O QUE OS SEUS/PAIS NÃO VIVERAM", "modo": "frente", "dur": 2.1, "recorte": True},
            {"fala": ["já", "tá", "na", "faculdade"], "texto": "JÁ TÁ NA/FACULDADE", "modo": "atras", "dur": 1.6},
            {"fala": ["organiza", "passaporte"], "texto": "ORGANIZA/PASSAPORTE", "modo": "atras", "dur": 1.5},
            {"fala": ["estuda", "outra", "língua"], "texto": "ESTUDA/OUTRA LÍNGUA", "modo": "frente", "dur": 1.5, "recorte": True},
            {"fala": ["nações"], "texto": "NAÇÕES", "modo": "atras", "dur": 1.3},
            {"fala": ["acelerar", "os", "processos"], "texto": "EU IREI/ACELERAR/OS PROCESSOS", "modo": "frente", "dur": 2.0, "riser": True},
            {"fala": ["romper", "romper"], "texto": "ROMPER/ROMPER", "modo": "frente", "dur": 1.6, "recorte": True},
            {"fala": ["romper", "o", "que"], "texto": "ROMPER O QUE/OS SEUS NÃO/ROMPERAM", "modo": "frente", "dur": 2.4, "recorte": True},
        ],
        "marquee_padrao": "ROMPER",
    },
    # ---- A: "Eu tinha tudo para dar errado, mas Deus me chamou para dar certo" ----
    # Gancho (frase final antecipada) + contexto + virada + desfecho. ~77 s.
    # Entre 31 s e 42 s do bruto o pastor sai do quadro da transmissão: esse pedaço é descartado.
    "A": {
        "musica": {"arquivo": "lovely.mp3", "inicio": 0.0, "modo": "continuo"},
        "paleta": {"fundo1": "#160f03", "fundo2": "#2d1f06", "luz": "#ffb52a", "destaque": "#ffd86b"},
        "trechos": [(77.0, 81.56), (0.0, 31.0), (42.0, 84.5)],
        "correcoes": {"pontou": "apontou", "dEle": "Dele"},
        "enfase": ["errado", "certo", "casa", "família", "geografia", "chegou", "chamei", "maldição", "propósito", "palavra"],
        "hits": [
            {"fala": ["tinha", "tudo", "para", "dar", "errado"], "texto": "VOCÊ TINHA/TUDO PARA/DAR ERRADO", "modo": "frente", "dur": 1.9},
            {"fala": ["eu", "te", "chamei"], "texto": "MAS EU TE CHAMEI/PARA DAR CERTO", "modo": "frente", "dur": 1.2, "recorte": True},
            {"fala": ["pela", "casa"], "texto": "PELA CASA", "modo": "atras", "dur": 1.0},
            {"fala": ["pela", "família"], "texto": "PELA FAMÍLIA", "modo": "atras", "dur": 1.0},
            {"fala": ["pela", "geografia"], "texto": "PELA/GEOGRAFIA", "modo": "atras", "dur": 1.3},
            {"fala": ["tudo", "para", "dar", "errado"], "texto": "TUDO PARA/DAR ERRADO", "modo": "frente", "dur": 2.0, "recorte": True},
            {"fala": ["deus", "chegou", "dizendo"], "texto": "MAS DEUS/CHEGOU", "modo": "frente", "dur": 1.6, "recorte": True},
            {"fala": ["não", "é", "o", "que", "a", "vida", "quer"], "texto": "NÃO É O QUE/A VIDA QUER", "modo": "atras", "dur": 1.8},
            {"fala": ["chegou", "primeiro"], "texto": "DEUS CHEGOU/PRIMEIRO", "modo": "frente", "dur": 1.5},
            {"fala": ["égide", "de", "uma", "maldição"], "texto": "SEM MALDIÇÃO/FAMILIAR", "modo": "atras", "dur": 1.8},
            {"fala": ["soberania", "e", "propósito"], "texto": "SOBERANIA/E PROPÓSITO", "modo": "atras", "dur": 1.5},
            {"fala": ["pregando", "para", "jovens"], "texto": "EU ESTOU/PREGANDO", "modo": "atras", "dur": 1.4},
            {"fala": ["eu", "te", "chamei"], "texto": "EU TE CHAMEI/PARA DAR CERTO", "modo": "frente", "dur": 2.6, "riser": True, "recorte": True},
        ],
        "marquee_padrao": "CERTO",
    },
}
