### tvorba GeoDataFrame (knihovna geopandas - pandas) přímo ve skriptu z data z QGIS vrstvy

import geopandas as gpd
import pandas as pd
import pygeoda
import shapely
import utils
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsMemoryProviderUtils,
    QgsVectorFileWriter,
)
from qgis.PyQt.QtCore import QMetaType

qgis = QgsApplication([], False)
qgis.initQgis()

project = utils.load_project(utils.test_project_path())

layer = utils.vector_layer_by_name(project, "okresy")

sloupec_hodnot_vrstva = "hodnota_1"
geom_colum_name = "geometry"
sloupec_hodnot_pandas = "hodnota"
sloupec_id = "kod"

field_kod = layer.fields().field(sloupec_id)
field_hodnota = layer.fields().field(sloupec_hodnot_vrstva)

pd_series_kod = pd.Series(dtype="string")

if field_hodnota.type() == QMetaType.Type.Int:
    pd_series_hodnota = pd.Series(dtype="int64")
else:
    pd_series_hodnota = pd.Series(dtype="float64")

gdf = gpd.GeoDataFrame(
    {
        sloupec_id: pd_series_kod,
        sloupec_hodnot_pandas: pd_series_hodnota,
        geom_colum_name: pd.Series(dtype="geometry"),
    },
    geometry=geom_colum_name,
    crs=layer.crs().authid(),
)

rows = []
feature: QgsFeature

for feature in layer.getFeatures():
    feature_geom_wkb = feature.geometry().asWkb().data()
    new_row = {
        sloupec_id: feature.attribute(sloupec_id),
        sloupec_hodnot_pandas: feature.attribute(sloupec_hodnot_vrstva),
        geom_colum_name: shapely.wkb.loads(feature_geom_wkb),
    }
    rows.append(new_row)


gdf = pd.concat([gdf, pd.DataFrame(rows)], ignore_index=True)

### potud shodné s příkladem 2

### Výpočet LOCAL LISA knihovnou geoda (modul pygeoda)

# konverze geometrie geoda object
gda_geometries = pygeoda.open(gdf)

# použití váhové matice typu Rook
weights = pygeoda.weights.rook_weights(gda_geometries)

# výpočet Local Moran's I
local_moran = pygeoda.local_moran(weights, gdf[sloupec_hodnot_pandas])

# zápis výsledků do datové vrstvy pomocí QGIS API

# příprava atributů tabulky
fields = QgsFields()
fields.append(QgsField(sloupec_id, QMetaType.Type.QString))
fields.append(QgsField("moran value", QMetaType.Type.Double))
fields.append(QgsField("moran p-value", QMetaType.Type.Double))
fields.append(QgsField("moran cluster", QMetaType.Type.Int))
fields.append(QgsField("moran cluster label", QMetaType.Type.QString))

# vytvoření paměťové vrstvy
memory_layer = QgsMemoryProviderUtils.createMemoryLayer(
    "local_moran_values",
    fields,
    Qgis.WkbType.NoGeometry,
    QgsCoordinateReferenceSystem(),
)

# přidání prvků do vrstvy
for i in range(len(gdf)):
    # řádek z GeoDataFrame
    row = gdf.loc[i]
    # nový prvek
    feature = QgsFeature(fields)
    # hodnota cluster
    cluster = local_moran.lisa_clusters()[i]
    # hodnoty atributů - pořadí musí být stejné jako v fields výše
    values = [
        row[sloupec_id],
        local_moran.lisa_values()[i],
        local_moran.lisa_pvalues()[i],
        cluster,
        local_moran.lisa_labels()[cluster],
    ]
    # nastavení atributů pro prvek
    feature.setAttributes(values)

    # přidání prvku do vrstvy
    memory_layer.dataProvider().addFeature(feature)

# nastavení zápisu do vrstvy/CSV souboru
options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "CSV"
options.fileEncoding = "UTF-8"
options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile

# zápis do CSV souboru
QgsVectorFileWriter.writeAsVectorFormatV3(
    memory_layer,
    utils.file_in_data_path("local_moran_values.csv").as_posix(),
    QgsCoordinateTransformContext(),
    options,
)
