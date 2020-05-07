# Inserir descrição


from datetime import datetime

from parecer52_2017.common.shared_code import stringInBetween, Alerta
import re

class ProjetosPesquisa():

    def __init__(self, texto_relatorio_progressao, xml_root, inicio_intersticio: datetime):
        self.inicio_intersticio = inicio_intersticio
        self.xml_root = xml_root

        self.__page_content = stringInBetween(("Projetos", "Orientações"), texto_relatorio_progressao)

        self.lista_projetos = self.__parse_projetos()

        self.pontos = self.__conta_pontos()

    # retorna o conjunto de projetos do PDF removendo duplicadas (mesmo código)
    def __parse_projetos(self):
        dados_lattes = self.xml_root.find('DADOS-GERAIS')
        nome_servidor_lattes = (dados_lattes.attrib['NOME-COMPLETO'])

        # Extraindo do texto os dados sobre as projetos
        projetos = re.findall(r'Nome:(.*?)Descrição:', self.__page_content)
        lista_projetos = []
        for projeto in projetos:
            nome_projeto = re.search(r'(.*?)Data de início:', projeto).group(1)

            data_inicial_str = re.search(r'Data de início:(.*?)Data de término', projeto).group(1)
            data_inicial_projeto = datetime.strptime(data_inicial_str, '%d/%m/%Y').date()

            # Só irá computar projetos que iniciaram depois do início do interício devido a uma falha no portal docente
            # que não indica o término dos projetos.
            if (self.inicio_intersticio > data_inicial_projeto):  # todo verificar CPAD
                continue

            data_final_str = re.search(r'Data de término:(.*?)Carga horária', projeto).group(1)
            if (data_final_str != ""):
                data_final = datetime.strptime(data_final_str, '%d/%m/%Y').date()
                # if(active_from_date != None) and (active_from_date > data_final):
                #     continue #todo verificar CPAD
            else:
                data_final = None

            # Verifica no XML do Lattes se é o coordenador. Caso não seja, é considerado integrante.
            str_papel_projeto = ""
            strProjeto = re.sub('[^a-z0-9]+', '', nome_projeto.lower())
            for projeto in (self.xml_root.findall('.//PROJETO-DE-PESQUISA[@NATUREZA="PESQUISA"]')):
                nome_projeto_lattes = projeto.attrib['NOME-DO-PROJETO']
                nome_projeto_lattes = re.sub('[^a-z0-9]+', '', nome_projeto_lattes.lower())

                if (nome_projeto_lattes == strProjeto):
                    membro_equipe = projeto.find('.//INTEGRANTES-DO-PROJETO[@FLAG-RESPONSAVEL="SIM"]')
                    nome = membro_equipe.attrib['NOME-COMPLETO']

                    if (nome == nome_servidor_lattes):
                        str_papel_projeto = "coordenador"
                    else:
                        str_papel_projeto = "integrante"
                    break

            if(str_papel_projeto==""):
                str_papel_projeto = "não determinado"
                Alerta.addAlerta("Aviso: projeto de pesquisa '"+ nome_projeto + "' não está registrado no Lattes. "
                                "\n      O docente será considerando um participante (não coordenador) para efeito de pontuação. "
                                "\n      Se necessário, solicite documentação comprobatória e pontue manualmente.")



            tupletProjeto = (nome_projeto, data_inicial_projeto, data_final, str_papel_projeto)
            lista_projetos.append(tupletProjeto)

        if(len(lista_projetos) < len(projetos)):
            Alerta.addAlerta("Aviso: Foram encontrados projetos iniciados antes do início do interstício que "
                             " ainda estão em aberto no portal docente por falha do sistema da UFES. "
                             "\n      Se necessário, solicite documentação comprobatória e pontue manualmente.")
        return lista_projetos

    def __conta_pontos(self):

        coord_count = sum(projeto[3] == "coordenador" for projeto in self.lista_projetos)
        pontuacao = (coord_count * 10) + ((len(self.lista_projetos) - coord_count) * 5)
        return pontuacao

