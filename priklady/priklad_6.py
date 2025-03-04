### Práce s layoutem a export do PDF

import typing

import utils
from qgis.core import (
    QgsApplication,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsPrintLayout,
)

qgis = QgsApplication([], False)
qgis.initQgis()

updated_project_filename = utils.file_in_data_path("updated_project.qgz")

project = utils.load_project(updated_project_filename)

# layout manager pro práci s layouty
layout_manager = project.layoutManager()

# extrakce layout podle jeho názvu
layout = layout_manager.layoutByName("Example Layout")
assert layout is not None
# přetypování na konkrétní typ - často důležité, protože se vrací obecné rozhraní (rodičovská třída)
layout = typing.cast(QgsPrintLayout, layout)


# extrakce komponenty layout podle jejího ID
scale_bar = layout.itemById("ScaleBar")
assert scale_bar is not None
scale_bar = typing.cast(QgsLayoutItemScaleBar, scale_bar)

# změna nastavení prvku
scale_bar.setUnitsPerSegment(100)
scale_bar.setNumberOfSegments(3)

title = layout.itemById("Title")
assert title is not None
title = typing.cast(QgsLayoutItemLabel, title)
title.setText("Mapa okresů")

picture = layout.itemById("Picture")
assert picture is not None
picture = typing.cast(QgsLayoutItemPicture, picture)
picture.setPicturePath(utils.file_in_data_path("histogram.png").as_posix())

project.write()

pdf_settings = QgsLayoutExporter.PdfExportSettings()
pdf_settings.dpi = 300
pdf_settings.forceVectorOutput = True


exporter = QgsLayoutExporter(layout)
exporter.exportToPdf(utils.file_in_data_path("layout.pdf").as_posix(), pdf_settings)

qgis.exitQgis()
