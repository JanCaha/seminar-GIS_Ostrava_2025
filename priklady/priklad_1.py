### Načtení QGIS Projektu a získání vrstvy dle názvu

import utils
from qgis.core import QgsApplication

qgis = QgsApplication([], False)
qgis.initQgis()

project = utils.load_project(utils.test_project_path())

# # získání projektu dle názvu v projektu
layer = utils.vector_layer_by_name(project, "okresy")

# výpis názvů sloupců vrstvy - včetně joinů a virtuálních polí
print(layer.fields().names())

qgis.exitQgis()
