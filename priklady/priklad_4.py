### tvorba matplotlib grafu (histogram) z dat z QGIS vrstvy

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import utils
from qgis.core import QgsApplication

matplotlib.use("Agg")

qgis = QgsApplication([], False)
qgis.initQgis()

project = utils.load_project(utils.test_project_path())

layer = utils.vector_layer_by_name(project, "okresy")

sloupec_id = "kod"
sloupec_hodnota = "join_data_hodnota_2"

df = utils.fields_as_dataframe(layer, sloupec_id, ["hodnota_1", sloupec_hodnota])

# vytvoření grafu
fig, ax = plt.subplots(figsize=(10, 6))

# tvorba samotného histogramu
df[sloupec_hodnota].hist(bins=30, edgecolor="black", alpha=0.7)

# Popisky os a titulek grafu
ax.set_xlabel("Hodnota")
ax.set_ylabel("Četnost")
ax.set_title(f"Histogram hodnot {sloupec_hodnota}")

# hodnotové popisky osy X (ve výchozím stavu jich je příliš)
min_val = df[sloupec_hodnota].min()
max_val = df[sloupec_hodnota].max()
ax.set_xticks(np.linspace(min_val, max_val, 5))

# grid pod daty
ax.grid(True, alpha=0.3)

# uložení obrázku
plt.savefig(utils.file_in_data_path("histogram.png"), dpi=300, bbox_inches="tight")

# zavření obrázku
plt.close("all")

qgis.exitQgis()
