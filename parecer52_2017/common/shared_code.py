import collections
import PyPDF2

class Alerta:
    lista_alertas = set()

    @staticmethod
    def addAlerta(texto):
        Alerta.lista_alertas.add(texto)

    @staticmethod
    def texto_formatado():
        texto = "\n"
        i = 1
        for alerta in Alerta.lista_alertas:
            texto += "   " + str(i) + ". " + alerta + "\n"
            i += 1
        return texto

    @staticmethod
    def print():
        print(Alerta.texto_formatado())
    #def getString(self):


def formataPrint(identacao, cabecalho, lista):
    texto = ""
    for item in lista:
        if isinstance(item, collections.abc.Sequence) and not isinstance(item, str):
            texto += ""  # numeracao
            texto_retornado = formataPrint(identacao + "    ", "", item)
            texto += " " + texto_retornado
        else:
            texto += " " + str(item) + " "

    if (identacao == ""):  # Primeiro nível
        return (cabecalho + texto)
    return (cabecalho + "\n" + identacao + texto)

# tutletTag(<substring anterior>,<substring posterior>, <key>)
def stringInBetween (tupletTag, text):
    startIndex = text.find(str(tupletTag[0])) + len(tupletTag[0])
    if(tupletTag[1]!=""):
        endIndex = text.find(str(tupletTag[1]), startIndex)
        return(text[startIndex:endIndex]).strip()
    else:
        return(text[startIndex:]).strip()


# tutletSet (<tupletTag1>, ...,tupletTagn>,textp)
def extractData (tupletSet, text):
    dictData = dict()

    for tupletTags in tupletSet:
        dictData[tupletTags[2]] =   stringInBetween(tupletTags,text)

    return dictData

def extrai_texto_pdf(pdf_file):
    # Extraindo texto do PDF (docentes.ufes.br)
    pdf_file = open(pdf_file, 'rb')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = read_pdf.getNumPages()
    c = collections.Counter(range(number_of_pages))
    page_content = ""
    for i in c:
        page = read_pdf.getPage(i)
        page_content += page.extractText()
    pdf_file.close()

    return page_content