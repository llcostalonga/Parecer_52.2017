from pathlib import Path

version = 1.0

data_folder = Path.cwd() / "docs"
#data_folder = Path("docs/")

filename_ficha_funcional = "ficha_qualificacao_progressao.pdf"
filename_portal_docente = "ProgressaoDocente.pdf"
filename_xml_lattes = "curriculo.xml"

path_ficha_funcional = data_folder / filename_ficha_funcional
path_portal_docente = data_folder / filename_portal_docente
path_xml_lattes = data_folder / filename_xml_lattes

resources_folder = Path("resources/")
file_parecer_aceleracao = resources_folder / "parecer_aceleracao.docx"
file_parecer_anexoIII = resources_folder / "anexoIII.docx"

remover_disciplinas_grad_duplicatas = True

calcular_filtro_periodo = False # Se for falso, usa os valores informados manualmente aqui.
filtro_periodo_manual = ["2020/1","2019/3","2019/2", "2019/1"]


#  Art. 52. Nos casos em que houver interrupção do semestre letivo, por motivos que
#  independam da iniciativa ou vontade do docente avaliado, e recaia sobre a Instituição
# o ônus da interrupção, o cálculo da pontuação da Área 1 deverá considerar a soma de
# toda a carga horária dividida pela quantidade de períodos concluídos pelo docente
# durante o interstício solicitado

aplicar_art52 = True;  #Fazer o cálculo na mão já que existe substancial chance de erro.
periodos_concluido_art52 = 3; #Periodos regulares, excluindo verão. Para atingir o mínimo de 160 pontos (Art. 37, § 1)
# são necessários ao menos 4 periodos regulares no interstício, ou seja, se 3 periodos foram conluidos será preciso
# somar a média deles UMA vez ao total da área 1. Se 2 períodos foram conluídos, então será preciso soma DUAS vezes a
# média,e assim por diante.