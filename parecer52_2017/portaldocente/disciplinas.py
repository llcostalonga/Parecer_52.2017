import re
import collections
from enum import Enum
from parecer52_2017.common.shared_code import Alerta,stringInBetween

class NivelEnsino(Enum):
    GRADUACAO = 1
    POSGRADUACAO=2

class Disciplinas:
    # @todo remover TCC e Estagio
    filtro_disciplina = ["DCE11947 - Trabalho de Conclusão de Curso I",  # C. da Computação
                         "DCE11949 - Trabalho de Conclusão de Curso II",  # C. da. Comp.
                         "DCE08352 - Projeto de Graduação I",  # Eng. da Comp.
                         "DCE08355 - Projeto de Graduação II",  # Eng. da Comp.
                         "ECH12751 - Trabalho de Conclusão de Curso (TCC)",  # Pedagogia
                         ]

    # Max 4 horas semanais (Art. 35)
    filtro_estagio_direta = ["DCS07308 - Estágio Curricular I"]

    # Max 4 horas semanais (Art. 35)
    filtro_estagio_semidireta = ["ECH12748 - Estágio Sup em gestão escolar"]  # ? Pedagogia?

    # Max 1 hora semanal (Art. 35)
    filtro_estagio_indireta = ["DCE11948 - Estágio Supervisionado",  # C. Comp DCE11948 - Estágio Supervisionado
                               "DCE08169 - Estágio Supervisionado"]  # Eng. Comp

    def __init__(self, texto_relatorio_progressao, filtro_periodo, nivel_ensino:NivelEnsino = NivelEnsino.GRADUACAO, remove_duplicatas = True):
        # A ordem das chamadas das funções ´ relevante. Não mudar sem a devida verificação.
        self.nivel_ensino = nivel_ensino
        self.filtro_periodo = filtro_periodo

        if(nivel_ensino == NivelEnsino.POSGRADUACAO):
            self.page_content = stringInBetween(("Turmas de Pós-Graduação", "Iniciações Científicas"), texto_relatorio_progressao)
            self.lista_disciplinas = self.__busca_disciplinas_posgrad()
        else:
            self.page_content = stringInBetween(("Turmas de Graduação", "Turmas de Pós-Graduação"),texto_relatorio_progressao)
            self.lista_disciplinas = self.__busca_disciplinas_grad(remove_duplicatas)

        self.dic_encargo_didatico = self.__contagem_encargo_didatico()
        self.pontos_semestre = self.__calcula_pontuacao()
        self.pontos = self.__soma_pontos_semestres()


    def __busca_disciplinas_grad(self, remove_duplicatas = True):
        # Extraindo do texto os dados sobre as disciplinas
        disciplinas = re.findall(r'Disciplina:(.*?)Vagas ocupadas:', self.page_content)
        lista_disciplinas = list()

        # somatório disciplinas de estágio
        sum_estagio_indireto = 0
        sum_estagio_semidireto = 0

        for disciplina in disciplinas:
            nome_disciplina = re.search(r'(.*?)Código', disciplina).group(1)
            nome_disciplina= nome_disciplina.upper()

            periodo = re.search(r'Período:(.*?)Curso', disciplina).group(1)

            if (nome_disciplina in self.filtro_disciplina):  # remove as disciplinas de TCC (Art4,3)
                Alerta.addAlerta("Disciplina removida (Art 4, §3): " + nome_disciplina)
                continue  # @todo dúvida para CPAD

            if (periodo in self.filtro_periodo):
                try:
                    encargo_didatico = float(re.search(r'Encargo didático:(\d+.\d)', disciplina).group(1))
                except:
                    continue  # encargo_didatico = 0
            else:
                continue

            # Verificação dos estágios - somente graduação? @cpad dúvida.
            if any(nome_disciplina[0:8] in s for s in self.filtro_estagio_semidireta):
                Alerta.addAlerta("Pontuado com o estágio semi-direto (Art 35)." + nome_disciplina)
                if (float(encargo_didatico) > 60):
                    if (sum_estagio_semidireto >= 60.0):
                        encargo_didatico = 0
                        Alerta.addAlerta(" Encargo didático ZERADO (Art. 35, § 10): Máximo permitido atingido.")
                    else:
                        dif = abs(sum_estagio_semidireto - encargo_didatico)
                        encargo_didatico = dif
                        sum_estagio_semidireto += dif
                        Alerta.addAlerta(" Encargo didático LIMITADO (Art. 35, § 10): Máximo permitido atingido.")
            elif any(nome_disciplina[0:8] in s for s in self.filtro_estagio_indireta):
                Alerta.addAlerta(nome_disciplina + "(" + periodo + "):" + "Pontuado com o estágio indireto (Art 35).")
                if (float(encargo_didatico) > 15.0):
                    if (sum_estagio_indireto >= 15.0):
                        encargo_didatico = 0
                        Alerta.addAlerta(" Encargo didático ZERADO (Art. 35, § 10): Máximo permitido atingido.")
                    else:
                        dif = abs(sum_estagio_indireto - encargo_didatico)
                        encargo_didatico = dif
                        sum_estagio_indireto += dif
                        Alerta.addAlerta(
                            nome_disciplina + "(" + periodo + "):" + " estágio indireto (LIMITADO) (Art. 35, § 10).")
                        Alerta.addAlerta(" Maximo atingido! Encargo didático LIMITADO (Art. 35, § 10).")
            elif any(nome_disciplina[0:8] in s for s in self.filtro_estagio_direta):
                Alerta.addAlerta(nome_disciplina + "(" + periodo + "):" + "pontuado como estágio direto (Art 35).")

            elif (nome_disciplina.lower().find("estágio") != -1):
                Alerta.addAlerta(
                    "INFORMAÇÃO NECESSÁRIA: " + nome_disciplina + "(" + periodo + "): possívelmente pontuada erroneamente como orientação direta.")


            retorno_busca = [(x, y, z) for x, y, z in lista_disciplinas if ((x == periodo) and (y == nome_disciplina))]

            if(len(retorno_busca) > 0):
                if (remove_duplicatas):
                    Alerta.addAlerta(
                        "Atenção: a disciplina " + nome_disciplina + " aparece  duplicada  no semestre " + periodo +
                        "\n      e NÃO FOI computada (Obs. 4 Anexo I). Solicitar a chefia a documentação comprobatória de que"
                        "\n      a disciplina foi ministrada em turmas com horários diferentes e, se comprovado, SOMAR "
                        "n      " + str(encargo_didatico) + " de encargo didático no semestre." )
                    continue
                else:
                    Alerta.addAlerta(
                        "Atenção: a disciplina " + nome_disciplina + " aparece  duplicada  no semestre " + periodo +
                        "\n      e mas FOI computada (Obs. 4 Anexo I). Solicitar a chefia documentação que realmente comprove"
                        "\n      que a disciplina foi ministrada em turmas com horários diferentes e, se for o caso, REMOVER "
                        "\n      " + str(encargo_didatico) + " de encargo didático no semestre." )


            tupletDisciplina = (periodo, nome_disciplina, encargo_didatico)
            lista_disciplinas.append(tupletDisciplina)

        lista_disciplinas.sort(key=lambda tup: tup[0])  # sorts in place

        return lista_disciplinas



    def __busca_disciplinas_posgrad(self):
        # Extraindo do texto os dados sobre as disciplinas
        disciplinas = re.findall(r'Disciplina:(.*?)Programa:', self.page_content)
        set_disciplinas = set()
        for disciplina in disciplinas:
            nome_disciplina = re.search(r'(.*?)Nome', disciplina).group(1)
            periodo = re.search(r'Período:(.*?)Carga horária', disciplina).group(1)

            try:
                # Erro da UFES...encardo didárico no PORTAL DOCENTE! DiDÁrico
                encargo_didatico = re.search(r'Encargo didárico:(.*?)Vagas oferecidas:', disciplina).group(1)
            except:
                encargo_didatico = 0

            tupletDisciplina = (periodo, nome_disciplina.upper(), encargo_didatico)
            set_disciplinas.add(tupletDisciplina)

        if (self.filtro_periodo == None):
            return list(set_disciplinas)

            # Filtrando conjunto para os períodos do intertício
        # filtro_periodo = ["2020/1","2019/3","2019/2", "2019/1"]
        lista_disciplinas = [tup for tup in set_disciplinas if any(i in tup for i in self.filtro_periodo)]
        lista_disciplinas = [(x, y, z) for x, y, z in lista_disciplinas if float(z) > 0]

        lista_disciplinas.sort(key=lambda tup: tup[0])  # sorts in place


        return lista_disciplinas

    def __contagem_encargo_didatico(self):
        dic_carga_horaria = dict()
        # dic_area1 = dict()
        for t in self.lista_disciplinas:

            periodo = t[0]
            encargo_didatico = t[2]

            if periodo in dic_carga_horaria:
                dic_carga_horaria[periodo] += float(encargo_didatico)
            else:
                dic_carga_horaria[periodo] = float(encargo_didatico)
        return dic_carga_horaria

    # No momento, está limitando a pontuação  120 por semestre (16) somando graduação e pós.
    # @todo CPAD isso deve ser reavaliado.
    def __calcula_pontuacao(self):
        dic_pontuacao = dict()
        keys = self.dic_encargo_didatico.keys()
        if(self.nivel_ensino == NivelEnsino.POSGRADUACAO):
            for k in keys:
                dic_pontuacao[k] = (self.dic_encargo_didatico[k] / 15) * 5
            return dic_pontuacao
        else:
            for k in keys:
                if (self.dic_encargo_didatico[
                    k] <= 120):  # Até 8 horas semanais (2 disciplinas de 60 horas), fator de mult. é 5
                    dic_pontuacao[k] = (self.dic_encargo_didatico[k] / 15) * 5
                else:
                    dif = self.dic_encargo_didatico[k] - 120
                    dic_pontuacao[k] = (((120 / 15) * 5) + ((dif / 15) * 10))
                    if (dic_pontuacao[k] > 120):  # limita a 16 horas somente para graduação? @todo duvida cpad
                        dic_pontuacao[k] = 120
                        Alerta.addAlerta("Teto de encargo de ensino atingido em " + str(k))

            return dic_pontuacao

    def __soma_pontos_semestres(self):
        keys = self.pontos_semestre.keys()
        total = 0
        for k in keys:
            total += self.pontos_semestre[k]

        return total



    def encargo_docente_anual_grad(self):
        encargo_grad_ano =  dict()
        keys = self.dic_encargo_didatico.keys()
        for k in keys:
            ano = k[0:4]
            encargo = self.dic_encargo_didatico[k]
            if(ano in encargo_grad_ano):
                valor_atual = encargo_grad_ano[ano]
            else:
               valor_atual = 0

            encargo_grad_ano[ano] = valor_atual + encargo
        return encargo_grad_ano

    def __str__(self):
        return str(self.lista_disciplinas)
