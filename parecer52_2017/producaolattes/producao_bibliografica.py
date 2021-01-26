from parecer52_2017.config import settings
from parecer52_2017.fichafuncional.ficha_funcional import FichaFuncional
from parecer52_2017.common.shared_code import Alerta
import xml.etree.ElementTree as ET

#from parecer52_2017.producaolattes.producao_intelectual import ProducaoIntelectual


class ProducaoBibliografica:

    def __init__(self,  xml_lattes, ano_incial, ano_final):

        self.ano_inicial = ano_incial
        self.ano_final = ano_final

        tree = ET.parse(xml_lattes)
        self.xml_root = tree.getroot()


        Alerta.addAlerta("Aviso: para efeito de pontuação da produção bibliogáfica são contados os dois ultimo anos"
                         " desprezando o ano corrente.")

        artigos_periodicos =  self.__artigos()
        self.artigos_periodicos = artigos_periodicos[0]
        self.pontos = artigos_periodicos[1]

        trabalhos_eventos = self.__trabalho_eventos()
        self.lista_artigos_eventos = trabalhos_eventos[0]
        self.pontos += trabalhos_eventos[1]

        capitulos = self.__capitulo_livro()
        self.capitulos_livro = capitulos[0]
        self.pontos += capitulos[1]

        livros = self.__livro()
        self.lista_livros = livros[0]
        self.pontos += livros[1]



    def __trabalho_eventos(self):
        # Verifica no XML do Lattes se é o coordenador. Caso não seja, é considerado integrante.
        lista_trabalhos = []
        pontos = 0;
        for trabalho in (self.xml_root.findall('.//TRABALHO-EM-EVENTOS')):
            dados = trabalho.find("DADOS-BASICOS-DO-TRABALHO")
            ano = int(dados.attrib["ANO-DO-TRABALHO"])

            if((ano >= self.ano_inicial) and (ano < self.ano_final)):
                titulo_trabalho = dados.attrib["TITULO-DO-TRABALHO"]
                natureza = dados.attrib["NATUREZA"]

                detalhes = trabalho.find("DETALHAMENTO-DO-TRABALHO")
                classificacao = detalhes.get("CLASSIFICACAO-DO-EVENTO")
                if (natureza == "RESUMO"):
                    if (classificacao == "REGIONAL"):
                        pontos+=2
                    else:
                        pontos+=5 # Nacional ou internacional é a mesma pontuação
                elif (natureza == "COMPLETO"):
                    if (classificacao == "REGIONAL"):
                        pontos += 5
                    else:
                        pontos += 10  # Nacional ou internacional é a mesma pontuação
                lista_trabalhos.append((titulo_trabalho,natureza,classificacao,ano))

            # detalhes = trabalho.find('.//DETALHAMENTO-DO-TRABALHO[@CLASSIFICACAO-DO-EVENTO="NACIONAL"]')
            # lista_trabalho.append((titulo_trabalho, ano))
        return (lista_trabalhos,pontos)

    def __artigos(self):
        # Verifica no XML do Lattes se é o coordenador. Caso não seja, é considerado integrante.
        lista_trabalhos = []
        pontos = 0;
        artigos_lattes = self.xml_root.findall('.//ARTIGO-PUBLICADO')
        for trabalho in artigos_lattes:
            dados = trabalho.find("DADOS-BASICOS-DO-ARTIGO")
            ano = int(dados.attrib["ANO-DO-ARTIGO"])

            if((ano >= self.ano_inicial) and (ano < self.ano_final)):
                titulo_trabalho = dados.attrib["TITULO-DO-ARTIGO"]

                natureza = dados.attrib["NATUREZA"]

                detalhes = trabalho.find("DETALHAMENTO-DO-ARTIGO")
                periodico = detalhes.get("TITULO-DO-PERIODICO-OU-REVISTA")

                # local_publicacao = str(detalhes.get("LOCAL-DE-PUBLICACAO"))
                if (natureza == "COMPLETO"):
                        pontos += 30  # Nacional ou internacional é a mesma pontuação

                lista_trabalhos.append((titulo_trabalho,natureza,periodico,ano))

            # detalhes = trabalho.find('.//DETALHAMENTO-DO-TRABALHO[@CLASSIFICACAO-DO-EVENTO="NACIONAL"]')
            # lista_trabalho.append((titulo_trabalho, ano))
        return (lista_trabalhos,pontos)

    def __capitulo_livro(self):
        # Verifica no XML do Lattes se é o coordenador. Caso não seja, é considerado integrante.
        lista_trabalhos = []
        pontos = 0;
        capitulos = self.xml_root.findall('.//CAPITULO-DE-LIVRO-PUBLICADO')
        for trabalho in capitulos:
            dados = trabalho.find("DADOS-BASICOS-DO-CAPITULO")
            ano = int(dados.attrib["ANO"])

            if((ano >= self.ano_inicial) and (ano < self.ano_final)):
                titulo_trabalho = dados.attrib["TITULO-DO-CAPITULO-DO-LIVRO"]
                pontos += 15  # Nacional ou internacional é a mesma pontuação
                lista_trabalhos.append((titulo_trabalho,ano))

        return(lista_trabalhos,pontos)

    def __livro(self):
        # Verifica no XML do Lattes se é o coordenador. Caso não seja, é considerado integrante.
        lista_trabalhos = []
        pontos = 0;
        livros = self.xml_root.findall('.//LIVRO-PUBLICADO-OU-ORGANIZADO')
        for trabalho in livros:
            dados = trabalho.find("DADOS-BASICOS-DO-LIVRO")
            ano = int(dados.attrib["ANO"])

            if((ano >= self.ano_inicial) and (ano < self.ano_final)):
                titulo_trabalho = dados.attrib["TITULO-DO-LIVRO"]
                pontos += 40  # Nacional ou internacional é a mesma pontuação
                lista_trabalhos.append((titulo_trabalho,ano))

        return(lista_trabalhos,pontos)

if __name__ == "__main__":
    # Parsing XML do Lattes
    tree = ET.parse("/Users/LeandroHD/Desenvolvimento/Parecer_52.2017/parecer52_2017/docs/curriculo.xml")
    xml_root = tree.getroot()

    ficha_progressao = FichaFuncional("/Users/LeandroHD/Desenvolvimento/Parecer_52.2017/parecer52_2017/docs/ficha_qualificacao_progressao.pdf")

    p = ProducaoIntelectual(xml_root,ficha_progressao )
    print(p.pontos)