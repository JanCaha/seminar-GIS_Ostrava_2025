### Přidání nových dat do QGIS projektu, tvorba joinu a nastavení rendereru

import utils
from qgis.core import (
    QgsApplication,
    QgsCategorizedSymbolRenderer,
    QgsFillSymbol,
    QgsRendererCategory,
    QgsVectorLayer,
    QgsVectorLayerJoinInfo,
)
from qgis.PyQt.QtGui import QColor

qgis = QgsApplication([], False)
qgis.initQgis()

updated_project_filename = utils.file_in_data_path("updated_project.qgz")

project = utils.load_project(utils.test_project_path())

# vytvoříme novou vrstvu
new_layer = QgsVectorLayer(utils.file_in_data_path("local_moran_values.csv").as_posix(), "Moran Values", "ogr")

# přidáme vrstvu do projektu
project.addMapLayer(new_layer)

# nalezení vrstvy okresy
layer_okresy = utils.vector_layer_by_name(project, "okresy")

# tvorba joinu
prefix = "moran_"
join_info = QgsVectorLayerJoinInfo()
join_info.setJoinLayer(new_layer)
join_info.setJoinFieldName("kod")
join_info.setTargetFieldName("kod")
join_info.setPrefix(prefix)

# přidání joinu do vrstvy okresy
layer_okresy.addJoin(join_info)

# zápis upraveného projektu
project.write(updated_project_filename.as_posix())

# výchozí symbol
symbol = QgsFillSymbol()

# nastavení barvy symbolu a následně kategorie pro 4 existující kategorie
symbol.setColor(QColor("#e94c4c"))
category_1 = QgsRendererCategory("High-High", symbol.clone(), "High-High")
symbol.setColor(QColor("#4c5fe9"))
category_2 = QgsRendererCategory("Low-Low", symbol.clone(), "Low-Low")
symbol.setColor(QColor("#7c89e9"))
category_3 = QgsRendererCategory("Low-High", symbol.clone(), "Low-High")
symbol.setColor(QColor("#b3b4bb"))
category_4 = QgsRendererCategory("Not significant", symbol.clone(), "Not significant")

# tvorba rendereru
renderer = QgsCategorizedSymbolRenderer(
    f"{prefix}moran cluster label", [category_1, category_2, category_3, category_4]
)

# nastavení rendereru vrstvě okresy
layer_okresy.setRenderer(renderer)

# zápis upraveného projektu
project.write(updated_project_filename.as_posix())

qgis.exitQgis()
