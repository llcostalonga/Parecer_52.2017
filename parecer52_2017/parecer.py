from enum import Enum

from parecer52_2017.config import settings
from parecer52_2017.fichafuncional.ficha_funcional import FichaFuncional
from parecer52_2017.portaldocente.portal_docente import PortalDocente
from parecer52_2017.common.shared_code import Alerta
from parecer52_2017.common.shared_code import formataPrint
from parecer52_2017.producaolattes.producao_intelectual import ProducaoIntelectual

from docxtpl import DocxTemplate
from datetime import date, timedelta,datetime

class StatusParecer(Enum):
    CONTRARIO=-1
    INCONCLUSIVO = 0
    FAVORAVEL = 1


class AnexoIII (Enum):
    ENSINO = "pt_ensino"
    ORIENTACAO = "pt_orientacao"
    PESQUISA_EXTENSAO = "pt_projeto"
    PRODUCAO_INTELECTUAL = "pt_producao"
    QUALIFICACAO_DOCENTE = "pt_qualificacao"
    ADMINISTRATIVO = "pt_administrativo"
    OUTRAS_ATIVIDADES = "pt_outras"
    SITUACOES_SESPECIAIS = "pt_especial"


class Parecer:
    quadro_pontuacao = dict()


    def __init__(self, portal_docente:PortalDocente, ficha_funcional: FichaFuncional, producao_intelectual : ProducaoIntelectual):

        #Limpa os alertas preparando para o próximo parecer.
        Alerta.lista_alertas.clear()

        self.portal_docente = portal_docente
        self.ficha_funcional = ficha_funcional
        self.producao_intelectual_lattes = producao_intelectual
        self.lista_aquivos =list()

        self.status_parecer = StatusParecer.FAVORAVEL

        if (not ficha_funcional.is_valid()):
            Alerta.addAlerta("Importante: Ficha funcional vencida. Solicitar nova ao interessado")

        dt_permitida_processo = ficha_funcional.fim_intersticio - timedelta(days=60)
        if (date.today() < dt_permitida_processo):
            Alerta.addAlerta(
                "Verificar: Possível processo prematuro de progressão. Se verificado, devolver ao interessado (Art. 26, § 1).")


    def emitir_parecer_aceleracao(self, is_favoravel= True):
        doc = DocxTemplate(settings.file_parecer_aceleracao)
        context = {'servidor': self.ficha_funcional.nome_servidor,
                    "num_processo" : "XXXXX.XXXX",
                    "parecer" : "favorável",
                    "classe_atual" : self.ficha_funcional.nivel,
                    "classe_alvo": "Adjunot B"}

        doc.render(context)
        file_name = "Parecer - "+ self.ficha_funcional.nome_servidor + ".docx"
        doc.save(file_name)
        self.lista_aquivos.append(file_name)

    def emitir_parecer_progressao(self, gravar_log= True):
        self.quadro_pontuacao[AnexoIII.ENSINO.value] = self.__verifica_retricoes_ensino(self.portal_docente)
        self.quadro_pontuacao[AnexoIII.ORIENTACAO.value] = self.portal_docente.orientacoes.pontos

        pontos_projeto_pesquisa = self.portal_docente.projetos_pesquisa.pontos
        pontos_acoes_extensao = self.portal_docente.acoes_extensao.pontos
        pontos_pesquisa_extensao = pontos_projeto_pesquisa+pontos_acoes_extensao
        self.quadro_pontuacao[AnexoIII.PESQUISA_EXTENSAO.value] = pontos_pesquisa_extensao

        pontos_ic = self.portal_docente.iniciacoes_cientificas.pontos
        self.quadro_pontuacao[AnexoIII.OUTRAS_ATIVIDADES.value] = pontos_ic # + ....incluir outros no futuro.

        self.quadro_pontuacao[AnexoIII.PRODUCAO_INTELECTUAL.value] = self.producao_intelectual_lattes.pontos

        if(self.__pontuacao_total() < 240):
            self.status_parecer = StatusParecer.INCONCLUSIVO
            Alerta.addAlerta("Importante: é necessário verificar outras produções do docente para atingir o mínimo de "
                             "240 pontos.")

        self.__preencher_docx_anexo3()
        if (gravar_log):
            self.gravar_log()

    def __preencher_docx_anexo3(self):
        doc = DocxTemplate(settings.file_parecer_anexoIII)

        context = {'servidor': self.ficha_funcional.nome_servidor,
                    "matricula": self.ficha_funcional.data["matricula"],
                    "lotacao_exercicio": self.ficha_funcional.data["lotacaoExercicio"], #provisorio
                    "lotacao_oficial": self.ficha_funcional.data["lotacaoOficial"],
                    "classe_atual": self.ficha_funcional.nivel,
                    "dt_nasc": self.ficha_funcional.data["dtNascimento"],
                    "sexo":self.ficha_funcional.data["sexo"],
                    "dt_adm":self.ficha_funcional.data["dtAdmissao"],
                    "dt_prog":self.ficha_funcional.data["dtUltimaProgressao"],
                    "grau_instrucao":self.ficha_funcional.data["grauInstrucao"],
                    "reg": self.ficha_funcional.data["regimeTrabalho"],
                    "pt_total":round(self.__pontuacao_total(),2),
                    "aval_disc_sim": " ", # fazer condicional
                    "aval_disc_nao": " ",
                    "favoravel": ("X" if (self.status_parecer==StatusParecer.FAVORAVEL) else " "), #condicional
                    "desfavoravel": ("X" if (self.status_parecer==StatusParecer.CONTRARIO) else " "), #condicional,
                    "data_corrente":date.today().strftime('%d-%m-%Y')}

        for tag in AnexoIII:
            key = AnexoIII(tag).value
            if key in self.quadro_pontuacao:
                context[key] = round(self.quadro_pontuacao[key],2)
            else:
                context[key] = " - "

        doc.render(context)
        file_name = "Anexo III - " + self.ficha_funcional.nome_servidor + ".docx"
        file_path = settings.data_folder / file_name
        doc.save(file_path)
        self.lista_aquivos.append(file_path)

    def __pontuacao_total(self):
        total = 0
        for p in self.quadro_pontuacao.values():
            total+=float(p)

        return total


    def __verifica_retricoes_ensino(self, portal_docente:PortalDocente):
        #Verifica o mínimo de 120 horas por ano na graduação (Art 4 §2)
        encargo_anual = portal_docente.disciplinas_grad.encargo_docente_anual_grad()
        keys = encargo_anual.keys()
        for k in keys:
            if(encargo_anual[k] < 120):
                Alerta.addAlerta("Importante: em "+ str(k) + " não foi atingido o mínimo de 120 horas na graduacão (Art 4 §2)."
                                                             "\n      Verifique se o servidor ocupava cargo administrativo "
                                                             ", se ficou afastado, ou se admissão foi atemporal. ")
                self.status_parecer = StatusParecer.INCONCLUSIVO

        #Verifica o mínimo de 40 pontos semestre (Art 35 §3)
        pontuacao_grad = portal_docente.disciplinas_grad.pontos_semestre
        pontuacao_posgrad = portal_docente.disciplinas_posgrad.pontos_semestre

        pontos_somados_periodos = {k: pontuacao_grad.get(k, 0) + pontuacao_posgrad.get(k, 0) for k in set(pontuacao_grad)}
        keys = portal_docente.disciplinas_grad.dic_encargo_didatico.keys()
        for k in keys:
            if ((pontos_somados_periodos[k] < 40) and (k[-1] != '3')):
                Alerta.addAlerta("Importante: não foi atingido o mínimo de 40 pontos de ensino (graduação + pós) no semestre "+ str(k) + "(Art 4 §2)."
                                "\n      Verificar se o servidor ocupava cargo administrativo ou encontrava-se afastado em " + str(k))
                self.status_parecer = StatusParecer.INCONCLUSIVO

        total_pontos_ensino = portal_docente.disciplinas_grad.pontos + portal_docente.disciplinas_posgrad.pontos
        if(settings.aplicar_art52):
            fator_mult_media = 4 - settings.periodos_concluido_art52 # 4 periodos são previstos para chegar nos 160 pontos.
            total_pontos_ensino += (portal_docente.disciplinas_grad.media_pontos + portal_docente.disciplinas_posgrad.media_pontos) * fator_mult_media

            Alerta.addAlerta("Importante: Art. 52 aplicado. A pontuação da Área 1 é a média dos semestres concluídos indicados "
                             "manualmente no filtro de configurações do sistema.")


        # Verifica a pontuação mínima de 160 pontos  (Art. 37, § 1
        if(total_pontos_ensino < 160):
            Alerta.addAlerta("Importante: não foi atingido o mínimo de 160 pontos no interstício para a área de ensino. (Art. 37, §1) "
                             "\n      Verifique se o servidor ocupava cargo administrativo ou encontrava-se ou estava "
                             "afastado do período do insterstício")
            self.status_parecer = StatusParecer.INCONCLUSIVO

        return total_pontos_ensino



    def __get_detalhamento(self):
        output = self.__str__()  # resultado do parecer

        output += "== DETALHAMENTO DA PONTUAÇÃO == \n"
        output += "===== 1. Turmas de Graduação =====" "\n"
        output += formataPrint("", "Disciplinas da Graduação (Semestre, Código, Disciplina, Encargo didático)",
                               self.portal_docente.disciplinas_grad.lista_disciplinas) + "\n"

        output += (formataPrint("", "Encargo didático Graduação (média: " +
                                str(self.portal_docente.disciplinas_grad.media_encago_didatico) + ")",
                                self.portal_docente.disciplinas_grad.dic_encargo_didatico.items())) + "\n"

        output += (formataPrint("", "Pontuação Graduação (média: " +
                                str(self.portal_docente.disciplinas_grad.media_pontos) + ")",
                                self.portal_docente.disciplinas_grad.pontos_semestre.items())) + "\n"


        output += "===== 2. Turmas de Pós-Graduação =====" "\n"
        output += (formataPrint("", "Disciplinas da Pós-graduação (Semestre, Código, Disciplina, Encargo didático)",
                                self.portal_docente.disciplinas_posgrad.lista_disciplinas)) + "\n"
        output += (formataPrint("", "Encargo didático Pós-Graduação(média: " +
                                str(self.portal_docente.disciplinas_posgrad.media_encago_didatico) + ")",
                                self.portal_docente.disciplinas_posgrad.dic_encargo_didatico.items())) + "\n"
        output += (formataPrint("", "Pontuação Pós-graduação (média: " +
                                str(self.portal_docente.disciplinas_posgrad.media_pontos) + ")",
                                self.portal_docente.disciplinas_posgrad.pontos_semestre.items())) + "\n"


        output += "===== 3. Iniciações Científicas =====" "\n"
        output += formataPrint("", "Iniciações Científica (Título, Data Início, Data Término)",
                               self.portal_docente.iniciacoes_cientificas.lista_iniciacoes_cientificas) + "\n"

        output += "===== 4. Ações de Extensão =====" "\n"
        output += (formataPrint("",
                                "Ações de Extensão(Título, Data de Início, Data de Término, Papel do Docente (Lattes)",
                                self.portal_docente.acoes_extensao.lista_projetos)) + "\n"

        output += "===== 5. Projetos de Pesquisa =====" "\n"
        output += (formataPrint("",
                                "Projetos de Pesquisa (Título, Data de Início, Data de Término, Papel do Docente (Lattes))",
                                self.portal_docente.projetos_pesquisa.lista_projetos)) + "\n"
        output += ("Pontuação de Projetos de Pesquisa:" +
                   str(self.portal_docente.projetos_pesquisa.pontos)) + "\n"

        output += "===== 5. Orientações =====" "\n"
        output += (formataPrint("", "Orientações (Nível, Papel do Docente, Orientando, Data Início, Data Término",
                                self.portal_docente.orientacoes.lista_orientacoes)) + "\n"

        output += ("Pontuação de orientações (somente) do portal docente:" + str(self.portal_docente.orientacoes.pontos)) + "\n"

        output += "===== 6. Produção Bibliográfica =====" "\n"
        output += (formataPrint("", "Livros ()",
                                self.producao_intelectual_lattes.producao_bibliografica.lista_livros)) + "\n"

        output += (formataPrint("", "Capítulos de Livros ()",
                                self.producao_intelectual_lattes.producao_bibliografica.capitulos_livro)) + "\n"

        output += (formataPrint("", "Artigos em Periódicos()",
                                self.producao_intelectual_lattes.producao_bibliografica.artigos_periodicos)) + "\n"

        output += (formataPrint("", "Artigos em Eventos()",
                                self.producao_intelectual_lattes.producao_bibliografica.lista_artigos_eventos)) + "\n"

        output += ("Alertas:" + str(Alerta.texto_formatado()) + "\n")

        output += "\n Observação: análise automatizada buscando informações da: \n a) ficha funcional de progressão, " + \
                  "\n b) relatório funcional para progressão (portal docente.ufes.br), \n c) Currículo Lattes na data corrente."

        return output

    def gravar_log(self):
        output = self.__get_detalhamento()
        output+= "\n Documento gerado em: " + str(datetime.now())
        file_name = "Log - " + self.ficha_funcional.nome_servidor +" " +str(date.today()) + ".txt"
        file_path = settings.data_folder / file_name
        f = open(file_path, "w", encoding='utf-8')
        f.write(output)
        f.close()
        self.lista_aquivos.append(file_path)

    def __str__(self):
        retorno = "Parecer: " + StatusParecer(self.status_parecer).name + "\n"
        retorno += "   Servidor: " + self.ficha_funcional.nome_servidor + "\n"
        retorno +="   Interstício: " + self.ficha_funcional.inicio_intersticio.strftime('%d-%m-%Y') + \
                  " - " + self.ficha_funcional.fim_intersticio.strftime('%d-%m-%Y') +"\n"
        retorno+= "   Ensino (Area 1): " + str(round(self.quadro_pontuacao[AnexoIII.ENSINO.value],2)) + "\n"
        retorno +="   Orientações (Area 2): " + str(self.quadro_pontuacao[AnexoIII.ORIENTACAO.value]) + "\n"
        retorno +="   Produção intelectual (Area 3):"+ str(self.quadro_pontuacao[AnexoIII.PRODUCAO_INTELECTUAL.value]) + "\n"
        retorno +="   Pesquisa & Extensão (Area 4): " + str(self.quadro_pontuacao[AnexoIII.PESQUISA_EXTENSAO.value]) + "\n"
        retorno +="   Qualificação docente (Area 5): Necessária verificação manual da documentação." + "\n"
        retorno +="   Atividades Administrativas (Area 6): Necessária verificação manual da documentação." + "\n"
        retorno +="   Outras Atividades (Area 7): " + str(
            round(self.quadro_pontuacao[AnexoIII.OUTRAS_ATIVIDADES.value],2)) + "\n"
        retorno +="   Situações especiais (Area 8): Necessária verificação manual da documentação" + "\n"

        retorno += "Pontuação total: " + str(round(self.__pontuacao_total(),2)) + "\n"
        return retorno

    @staticmethod
    def run():
        ficha_progressao = FichaFuncional(settings.path_ficha_funcional)

        portal_docente = PortalDocente(settings.path_portal_docente,
                                       settings.path_xml_lattes,
                                       ficha_progressao)

        producao_intelectual_lattes = ProducaoIntelectual(settings.path_xml_lattes,
                                                          ficha_progressao)

        parecer = Parecer(portal_docente, ficha_progressao, producao_intelectual_lattes)

        parecer.emitir_parecer_progressao()

        return  parecer

if __name__ == "__main__":

    ficha_progressao = FichaFuncional(settings.path_ficha_funcional)

    portal_docente = PortalDocente(settings.path_portal_docente,
                                   settings.path_xml_lattes,
                                   ficha_progressao)

    producao_intelectual_lattes = ProducaoIntelectual(settings.path_xml_lattes,
                                                      ficha_progressao)

    parecer = Parecer(portal_docente, ficha_progressao, producao_intelectual_lattes)

    parecer.emitir_parecer_progressao()
    parecer.gravar_log()
    print(parecer)
    Alerta.print()

