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

remover_disciplinas_grad_duplicatas = False

calcular_filtro_periodo = False # Se for falso, usa os valores informados manualmente aqui.
filtro_periodo_manual = ["2019/3","2019/2", "2019/1", "2018/3"]

