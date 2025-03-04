### tvorba GeoDataFrame (knihovna geopandas - pandas) přímo ve skriptu z data z QGIS vrstvy

import geopandas as gpd
import pandas as pd
import shapely
import utils
from qgis.core import QgsApplication, QgsFeature
from qgis.PyQt.QtCore import QMetaType

qgis = QgsApplication([], False)
qgis.initQgis()

project = utils.load_project(utils.test_project_path())

layer = utils.vector_layer_by_name(project, "okresy")

# zájmová pole
field_kod = layer.fields().field("kod")
field_hodnota = layer.fields().field("hodnota_1")

# tvorba typu sloupců pro GeoDataFrame
pd_series_kod = pd.Series(dtype="string")

if field_hodnota.type() == QMetaType.Type.Int:
    pd_series_hodnota = pd.Series(dtype="int64")
else:
    pd_series_hodnota = pd.Series(dtype="float64")

geom_colum_name = "geometry"

# tvorba prázdného GeoDataFrame - geopandas
gdf = gpd.GeoDataFrame(
    {
        "kod": pd_series_kod,
        "hodnota": pd_series_hodnota,
        geom_colum_name: pd.Series(dtype="geometry"),
    },
    geometry=geom_colum_name,
    crs=layer.crs().authid(),  # Nastavení CRS z vrstvy
)

# extrakce zájmových dat - geometrie musí být konvertovány přes WKB a knihovnu shapely
rows = []
feature: QgsFeature

for feature in layer.getFeatures():
    feature_geom_wkb = feature.geometry().asWkb().data()
    new_row = {
        "kod": feature.attribute("kod"),
        "hodnota": feature.attribute("hodnota_1"),
        geom_colum_name: shapely.wkb.loads(feature_geom_wkb),
    }
    rows.append(new_row)

# přidání řádků do GeoDataFrame
gdf = pd.concat([gdf, pd.DataFrame(rows)], ignore_index=True)

# výpis GeoDataFrame
print(gdf)

qgis.exitQgis()
