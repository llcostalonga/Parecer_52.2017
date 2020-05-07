
# importing required modules
from datetime import datetime, timedelta,date
from parecer52_2017.common.shared_code import extractData,extrai_texto_pdf,stringInBetween
from parecer52_2017.config import settings


class FichaFuncional:
    fields = {
        ("Servidor:", " - ", "siape"),
        ("Nível: ", "Situação", "nivel"),
        ("PessoasData:", "Hora:", "dtEmissao"),
        ("Trabalho:", "Cargo:", "regimeTrabalho"),
        ("Ultima Progressão:", "Forma Ingresso:", "dtUltimaProgressao"),
        ("Servidor:", "Matrícula", "servidor"),
        ("Admissão Cargo:", "Grau de Instrução:", "dtAdmissao"),
        ("Lotação Oficial:", "InícioTérminoÚltimas", "lotacaoOficial"),
        ("Grau de Instrução:","Data de Desligamento:","grauInstrucao"),
        ("Data de Nascimento:", "Sexo:", "dtNascimento"),
        ("Sexo:","Servidor:","sexo"),
        ("Lotação do Exercício:","Lotação Oficial:","lotacaoExercicio"),
        ("Matrícula UFES: ", "Lotação do Exercício:","matricula")

    }

    def __init__(self, pdf_fichafuncional):

        texto = extrai_texto_pdf(pdf_fichafuncional)
        self.data = extractData(self.fields,texto)

        #carrega os principais campos para os atributos

        nome_servidor = self.data.get("servidor")
        self.data["servidor"] = stringInBetween((" - ",""),nome_servidor)
        self.nome_servidor = self.data["servidor"]

        self.nivel = self.data.get("nivel")

        self.inicio_intersticio = self.__inicio_intersticio()
        self.fim_intersticio = self.__fim_intersticio()




    def is_valid(self):
        dtEmissao= datetime.strptime(self.data.get("dtEmissao"), '%d/%m/%Y').date()
        prazo = dtEmissao + timedelta(days=60)
        if (date.today() <= prazo):
            return True
        return False

    def __inicio_intersticio(self):
        dtUltimaProgressao = self.data.get("dtUltimaProgressao")
        if (dtUltimaProgressao ==""):
            dtUltimaProgressao = self.data.get("dtAdmissao")

        dtUltimaProgressao = datetime.strptime(dtUltimaProgressao, '%d/%m/%Y').date()
        return (dtUltimaProgressao)

    def __fim_intersticio(self):
        dtUltimaProgressao = self.data.get("dtUltimaProgressao")
        if (dtUltimaProgressao == ""):
            dtUltimaProgressao = self.data.get("dtAdmissao")

        dtUltimaProgressao = datetime.strptime(dtUltimaProgressao, '%d/%m/%Y').date()
        dtFimIntersticio = dtUltimaProgressao + timedelta(days=(365*2))
        return (dtFimIntersticio)


if __name__ == "__main__":

    ficha = FichaFuncional(settings.path_ficha_funcional)

    print(ficha.is_valid())
    print(ficha.inicio_intersticio)
    print(ficha.fim_intersticio)

    print(ficha.data)


# closing the pdf file object
