import pathlib
import typing
from pathlib import Path

import pandas as pd
from qgis.core import Qgis, QgsFeature, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QMetaType


def data_path() -> Path:
    """Vrací cestu k adresáři s daty"""
    return pathlib.Path(__file__).parent.parent / "data"


def test_project_path() -> Path:
    """Vrací cestu k testovacímu projektu"""
    return data_path() / "projekt.qgz"


def file_in_data_path(filename: str) -> Path:
    """Vrací cestu k souboru v adresáři data"""
    return data_path() / filename


def load_project(project_path: Path) -> QgsProject:
    """Vrací načtený QGIS projekt"""

    # tvorba projektu
    project = QgsProject.instance()

    # některé funkce mohou vracet objekt či None, proto je vhodné to ošetřit
    # pokud by projekt byl None, tak se zde vyhodí chyba
    assert project is not None

    project.read(project_path.as_posix())

    return project


def vector_layer_by_name(project: QgsProject, layer_name: str, layer_order: int = 0) -> QgsVectorLayer:
    """Vrací vrstvu dle názvu"""

    # získání vrstvy dle názvu
    layer = project.mapLayersByName(layer_name)[layer_order]

    if not layer:
        raise ValueError(f"Vrstva {layer_name} nebyla nalezena.")

    # kontrola, zda se jedná o vektorovou vrstvu
    if not layer.type() == Qgis.LayerType.Vector:
        raise ValueError(f"Vrstva {layer_name} není vektorová vrstva.")

    layer = typing.cast(QgsVectorLayer, layer)

    # kontrola, zda je vrstva validní
    if not layer.isValid():
        raise ValueError(f"Vrstva {layer_name} není validní.")

    # kontrola, zda má vrstva nějaké prvky
    if layer.dataProvider().featureCount() < 1:
        raise ValueError(f"Vrstva {layer_name} neobsahuje žádné prvky.")

    return layer


def fields_as_dataframe(layer: QgsVectorLayer, id_field: str, fields_names: typing.List[str]) -> pd.DataFrame:
    """Vrací DataFrame s hodnotami z vrstvy"""

    # sloupce vrstvy
    fields = layer.fields()

    # fields pro pandas
    pandas_fields = {}

    # extrahovat sloupce
    field_id = fields.field(id_field)
    assert field_id is not None

    # typ id sloupce
    if field_id.type() == QMetaType.QString:
        field_id_type = "string"
    elif field_id.type() == QMetaType.Int:
        field_id_type = "int64"
    else:
        raise ValueError(f"Neznámý typ sloupce {id_field}.")

    # přidání id sloupce
    pandas_fields["id"] = pd.Series(dtype=field_id_type)

    # iterace přes zájmové sloupce
    for field_name in fields_names:
        field = fields.field(field_name)
        assert field_name is not None

        if field.type() == QMetaType.QString:
            field_type = "string"
        elif field.type() == QMetaType.Int:
            field_type = "int64"
        elif field.type() == QMetaType.Double:
            field_type = "float64"
        else:
            raise ValueError(f"Neznámý typ sloupce {field_name}.")

        pandas_fields[field_name] = pd.Series(dtype=field_type)

    # vytvoření prázdného DataFrame
    df = pd.DataFrame(columns=pandas_fields)

    # iterace přes prvky
    rows = []
    feature: QgsFeature

    for feature in layer.getFeatures():
        row = {
            "id": feature.attribute(id_field),
        }

        for field_name in fields_names:
            row[field_name] = feature.attribute(field_name)

        rows.append(row)

    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

    return df
