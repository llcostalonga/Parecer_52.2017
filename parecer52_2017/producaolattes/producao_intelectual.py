from parecer52_2017.config import settings
from parecer52_2017.fichafuncional.ficha_funcional import FichaFuncional
from parecer52_2017.common.shared_code import Alerta
import xml.etree.ElementTree as ET
from parecer52_2017.producaolattes.producao_bibliografica import ProducaoBibliografica

class ProducaoIntelectual:

    def __init__(self,  xml_lattes, ficha_funcional:FichaFuncional):
        self.xml_root = xml_lattes
        self.ano_inicial = ficha_funcional.inicio_intersticio.year
        self.ano_final = ficha_funcional.fim_intersticio.year

        self.producao_bibliografica = ProducaoBibliografica(self.xml_root,
                                                            self.ano_inicial,
                                                            self.ano_final)

        self.pontos = self.producao_bibliografica.pontos
