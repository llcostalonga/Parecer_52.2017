# portaldocente_extensão

# Analisa (e pontua) somente a coordenação e participação em ações de extensão
# listadas no relatório de progressão (portal docente). Busca no Lattes informações
# sobre o papel do docente (coordenador ou participante). Pontua somente os itens
# a e b da Tabela 4.1 do Anexo I da resolução.
# Versão: 0.1
# Criado em: 24/04/2020

from parecer52_2017.common.shared_code import Alerta,stringInBetween

from datetime import datetime, timedelta, date
import re

class AcoesExtensao():

    def __init__(self, texto_relatorio_progressao, xml_root, inicio_intersticio: datetime,fim_intersticio: datetime) :
        self.inicio_intersticio = inicio_intersticio
        self.fim_intersticio = fim_intersticio
        self.xml_root = xml_root

        self.__page_content = stringInBetween(("Ações de Extensão", "ProjetosNome:"), texto_relatorio_progressao)

        self.lista_projetos = self.__parse_acoes_extensao()

        self.pontos = self.__conta_pontos()


    # passar datetime (objeto)
    def __parse_acoes_extensao(self):
        dados_lattes = self.xml_root.find('DADOS-GERAIS')
        nome_servidor_lattes = (dados_lattes.attrib['NOME-COMPLETO'])

        # Extraindo do texto os dados sobre as projetos
        projetos = self.__page_content.split('Título:')

        lista_projetos = []
        for projeto in projetos[1:]:
            nome_projeto = re.search(r'(.*?)Data de início:', projeto).group(1)

            data_inicial_projeto_str = re.search(r'Data de início:(.*?)Data de término', projeto).group(1)
            data_inicial_projeto = datetime.strptime(data_inicial_projeto_str, '%d/%m/%Y').date()

            data_finalprojeto_str = re.search(r'Data de término:(.*)', projeto).group(1)
            data_final_projeto = datetime.strptime(data_finalprojeto_str, '%d/%m/%Y').date()

            # Retira da lista projetos antes do início do intersticio
            if (self.inicio_intersticio is not None):
                if (data_final_projeto < self.inicio_intersticio):
                    continue

            str_papel_projeto = "não foi buscado no Lattes"
            if (self.xml_root is not None):
                # Verifica no XML do Lattes se é o coordenador
                str_papel_projeto = "projeto não cadastrado no Lattes"
                strProjeto = re.sub('[^a-z0-9]+', '', nome_projeto.lower())
                for projeto_lattes in (self.xml_root.findall('.//PROJETO-DE-PESQUISA[@NATUREZA="EXTENSAO"]')):
                    nome_projeto_lattes = projeto_lattes.attrib['NOME-DO-PROJETO']
                    nome_projeto_lattes = re.sub('[^a-z0-9]+', '', nome_projeto_lattes.lower())

                    if (strProjeto in nome_projeto_lattes):
                        membro_equipe = projeto_lattes.find('.//INTEGRANTES-DO-PROJETO[@FLAG-RESPONSAVEL="SIM"]')
                        nome = membro_equipe.attrib['NOME-COMPLETO']

                        if (nome == nome_servidor_lattes):
                            str_papel_projeto = "coordenador"
                        else:
                            str_papel_projeto = "participante"
                        break

            tupletProjeto = (nome_projeto, data_inicial_projeto, data_final_projeto, str_papel_projeto)
            lista_projetos.append(tupletProjeto)

        return lista_projetos


    def __conta_pontos(self):
        coord_count = sum(projeto[3] == "coordenador" for projeto in self.lista_projetos)
        pontuacao = (coord_count * 10) + ((len(self.lista_projetos) - coord_count) * 5)
        return pontuacao

