
# Esse script está buscando orientações somente o relatório para progressão
# obitido do portal docente (interno da UFES). Idealmente, deveria-se buscar as orientações
# também do Lattes se o max (40 pontos) não for atingido. Em 23/04/02 v.0.1


import re
from datetime import datetime, timedelta

from parecer52_2017.common.shared_code import stringInBetween,Alerta

class Orientacoes:

    # Tipo de orientação, pontuação/mes orientação, pontuação/mes CO-orientatação, limite (meses)
    tabela_pontuacao = {"TCC": (0.5, 0, 6),
                        "Especialização": (1.0, 0.5, 6),
                        "Mestrado": (1.5, 0.5, 24),
                        "Doutorado": (2.0, 1.0, 48),
                        "Não detectado": (0, 0, 0)
                        }

    def __init__(self, texto_relatorio_progressao, inicio_intersticio:datetime, fim_intersticio:datetime):
        self.inicio_intersticio = inicio_intersticio
        self.fim_intersticio = fim_intersticio

        self.__page_content = stringInBetween(("Orientações",""),texto_relatorio_progressao)

        self.lista_orientacoes = self.__parse_orientacoes()

        self.pontos = self.__conta_pontos()


    def __parse_orientacoes(self):
        # Extraindo do texto os dados sobre orientacoes
        orientacoes = lista = self.__page_content.split('Tipo:')
        lista_orientacoes = []

        for orientacao in orientacoes[1:]:  # começa no segundo elemento

            data_inicio_str = re.search(r'Data de início:(.*?)Data de término:', orientacao).group(1)
            data_inicio_orientacao = datetime.strptime(data_inicio_str, '%d/%m/%Y').date()

            if (self.fim_intersticio is not None):
                if (data_inicio_orientacao > self.fim_intersticio):  # orientação começou depois do fim do intertício.
                    continue

            data_termino_str = re.search(r'Data de término:(.*?)Nome do aluno:', orientacao).group(1)
            if (data_termino_str != ""):
                data_termino_orientacao = datetime.strptime(data_termino_str, '%d/%m/%Y').date()
                if (self.inicio_intersticio != None):  # Errado!
                    if (data_termino_orientacao < self.inicio_intersticio):  # orientação terminou depois do intertício.
                        continue
            else:
                data_termino_orientacao = None

            papel_docente = re.search(r'(.*?)Data de início:', orientacao).group(1)
            nome_orientando = re.search(r'Nome do aluno:(.*?)Curso:', orientacao).group(1)
            curso = re.search(r'Curso:(.*)', orientacao).group(1)

            if ("Mestrado" in curso):
                nivel = "Mestrado"
            elif "Doutorado" in curso:  # chute...sem teste ainda.
                nivel = "Doutorado"
            elif "Especialização" in curso:  # chute..sem dados para testar ainda.
                nivel = "Especialização"
            elif "Conclusão" in curso:  # chute..sem dados para testar ainda.
                nivel = "TCC"
            else:
                nivel = "Não detectado"

            tupletOrientacao = (nivel, papel_docente, nome_orientando, data_inicio_orientacao, data_termino_orientacao)
            lista_orientacoes.append(tupletOrientacao)

        return lista_orientacoes


    def __conta_pontos(self):
        pontuacao = 0
        for orientacao in self.lista_orientacoes:
            pontos = self.tabela_pontuacao.get(orientacao[0])

            data_inicio_orientacao = orientacao[3]
            data_termino_orientacao = orientacao[4]
            # Ajuste relativo aos itens 9 e 10 da observação da Area 2 no Anexo I
            if (data_termino_orientacao is None):
                data_termino_orientacao = self.fim_intersticio
            # else:
            #     data_termino_orientacao = datetime.strptime(orientacao[4], '%d/%m/%Y').date()

            data_limite_orientacao = data_inicio_orientacao + timedelta(days=(pontos[2] * (365 / 12)))
            if (data_termino_orientacao > data_limite_orientacao):
                data_termino_orientacao = data_limite_orientacao

                Alerta.addAlerta("A orientação de " + str(orientacao[2]) + " foi pontuada somente até o seu prazo limite (" +
                                 str(data_limite_orientacao) + " ou o fim do interstício).")

            # Calculo em mess (aproximado) do tempo de orientacao
            if (data_inicio_orientacao > self.inicio_intersticio):
                date_diff = data_termino_orientacao - data_inicio_orientacao
            else:
                date_diff = data_termino_orientacao - self.inicio_intersticio

            qtd_meses = (date_diff.days // (365 / 12))  # meses arredondado para baixo
            if qtd_meses > pontos[2]:  # Limites impostos pela resolução em meses
                qtd_meses = pontos[2]

            if (orientacao[1] == "Orientador"):
                pontuacao += qtd_meses * pontos[0]
            else:
                pontuacao += qtd_meses * pontos[1]

            if (pontuacao > 40):  # Limite da resolução para Área 2 (Orientações)
                Alerta.addAlerta("Nota: a pontuacão relativa a orientação foi limitada ao máximo de 40 pontos, conforme"
                                 + " indicado no Anexo I (Area 2) da resolução.")
                return 40
        return pontuacao

