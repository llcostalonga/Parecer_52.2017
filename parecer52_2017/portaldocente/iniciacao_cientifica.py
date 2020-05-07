# portaldocente_orientacoes.py

# Esse script está buscando orientações somente o relatório para progressão
# obitido do portal docente (interno da UFES). Idealmente, deveria-se buscar as orientações
# também do Lattes se o max (40 pontos) não for atingido. Em 23/04/02 v.0.1


import re
from datetime import datetime
from parecer52_2017.common.shared_code import Alerta,stringInBetween

class IniciacoesCientificas():

    def __init__(self, texto_relatorio_progressao,  inicio_intersticio: datetime,fim_intersticio: datetime) :
        self.inicio_intersticio = inicio_intersticio
        self.fim_intersticio = fim_intersticio

        self.__page_content = stringInBetween(("Iniciações Científicas","Ações de Extensão"), texto_relatorio_progressao)

        self.lista_iniciacoes_cientificas = self.__parse_iniciacoes_cientificas()

        self.pontos = self.__conta_pontos()

    def __parse_iniciacoes_cientificas(self):
        # Extraindo do texto os dados sobre orientacoes
        # orientacoes = page_content.split('Título:') Resumo:

        orientacoes = re.findall(r'Título:(.*?)Resumo:', self.__page_content)

        lista_orientacoes = []
        for orientacao in orientacoes:
            # if(orientacao == ""):
            #     continue

            titulo = re.search(r'(.*?)Data de início:', orientacao).group(1)
            data_inicio_str = re.search(r'Data de início:(.*?)Data de término:', orientacao).group(1)

            if (data_inicio_str == ""):
                Alerta.addAlerta("Iniciação Científica '" + titulo + "'não computada por não ter data de início definida.")
                continue

            data_inicio_ic = datetime.strptime(data_inicio_str, '%d/%m/%Y').date()

            if (self.fim_intersticio is not None):
                if (data_inicio_ic > self.fim_intersticio):  # IC começou depois do fim do intertício.
                    continue

            data_termino_str = re.search(r'Data de término:(.*)', orientacao).group(1)
            if (data_termino_str != ""):
                data_termino = datetime.strptime(data_termino_str, '%d/%m/%Y').date()
                if (self.inicio_intersticio != None):  # Errado!
                    if (data_termino < self.inicio_intersticio):  # orientação terminou depois do intertício.
                        continue
            else:
                data_termino = None

            tupletOrientacao = (titulo, data_inicio_ic, data_termino)
            lista_orientacoes.append(tupletOrientacao)

        return lista_orientacoes

    def __conta_pontos(self):
        pontuacao = 0
        for orientacao in self.lista_iniciacoes_cientificas:

            data_inicio_orientacao = orientacao[1]
            data_termino_orientacao = orientacao[2]

            if (data_termino_orientacao is None):
                data_termino_orientacao = self.fim_intersticio
            else:
                data_termino_orientacao = orientacao[2]

            # Calculo em meses (aproximado) do tempo de orientacao
            if (data_inicio_orientacao > self.inicio_intersticio):
                date_diff = data_termino_orientacao - data_inicio_orientacao
            else:
                date_diff = data_termino_orientacao - self.inicio_intersticio

            qtd_meses = (date_diff.days // (365 / 12))  # meses arredondado para baixo

            pontuacao += qtd_meses * 0.3

        return pontuacao

