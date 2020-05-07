

import re
import collections
from datetime import datetime, timedelta, date
import xml.etree.ElementTree as ET
from pathlib import Path


from parecer52_2017.portaldocente.disciplinas import Disciplinas, NivelEnsino
from parecer52_2017.portaldocente.orientacoes import Orientacoes
from parecer52_2017.portaldocente.projeto_pesquisa import ProjetosPesquisa
from parecer52_2017.fichafuncional.ficha_funcional import FichaFuncional
from parecer52_2017.portaldocente.iniciacao_cientifica import IniciacoesCientificas
from parecer52_2017.portaldocente.acao_extensao import AcoesExtensao
from parecer52_2017.common.shared_code import extrai_texto_pdf


class PortalDocente:
    def __init__(self, pdf_relatorio_progresso, xml_lattes, ficha_funcional:FichaFuncional):

        # extrai texto do PDF
        page_content = extrai_texto_pdf(pdf_relatorio_progresso)

        # limpa cabeçalho da quebra de página do pdf portal docente
        self.__page_content = re.sub(r'Este doc(.*?)instituição:(\d{2})[/.-](\d{2})[/.-](\d{4})', "", page_content)

        #
        self.ficha_funcional = ficha_funcional #provalvemente vai mudar

        # Parsing XML do Lattes
        tree = ET.parse(xml_lattes)
        self.__xml_root = tree.getroot()

        self.__parse_disciplinas()

        self.orientacoes = Orientacoes(self.__page_content,
                                        ficha_funcional.inicio_intersticio,
                                        ficha_funcional.fim_intersticio)

        self.projetos_pesquisa = ProjetosPesquisa(self.__page_content,
                                                  self.__xml_root,
                                                  ficha_funcional.inicio_intersticio)

        self.acoes_extensao = AcoesExtensao(self.__page_content,
                                            self.__xml_root,
                                            ficha_funcional.inicio_intersticio,
                                            ficha_funcional.fim_intersticio)

        self.iniciacoes_cientificas = IniciacoesCientificas(self.__page_content,
                                        ficha_funcional.inicio_intersticio,
                                        ficha_funcional.fim_intersticio)


    def __parse_disciplinas(self):
        self.filtro_periodo = self.__filtro_periodo(self.ficha_funcional)  # considerar jogar para modulo disciplinas.py

         # self.filtro_periodo.append("2018/1") # Usando para overide manual no período de avaliacao.

        self.disciplinas_grad = Disciplinas(self.__page_content, self.filtro_periodo, NivelEnsino.GRADUACAO)
        self.disciplinas_posgrad = Disciplinas(self.__page_content, self.filtro_periodo, NivelEnsino.POSGRADUACAO)

    def __filtro_periodo(self, ficha_funcional):
        inicio_intersticio = ficha_funcional.inicio_intersticio
        fim_intersticio = ficha_funcional.inicio_intersticio
        filtro_periodo = []
        total =0
        ano = inicio_intersticio.year
        if (inicio_intersticio.month < 6):
            semestre = 1
        elif (inicio_intersticio.month < 11):
            semestre = 2
        else:
            semestre = 3

        while (total < 6):
            while semestre <= 3 and total <6:
                periodo = str(ano) + "/" +str(semestre)
                filtro_periodo.append(periodo)
                semestre+=1
                total+=1
            ano+=1
            semestre = 1
        return filtro_periodo


