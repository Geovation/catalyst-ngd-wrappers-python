import os
from unittest import TestCase
import requests as r

from .ngd_api_wrappers import items

WKT = """
GEOMETRYCOLLECTION(
    MULTIPOLYGON(
        ((558288 104518, 558288 104528, 558298 104528, 558298 104518, 558288 104518)),
        ((558388 104318, 558388 104328, 558398 104328, 558398 104318, 558388 104318))
    ),
    LINESTRING(
        558288 104518, 558298 104528, 558398 104328, 558398 104318
    )
)"""
KEY = os.environ.get('CLIENT_ID')

class TestNGDWrapper(TestCase):

    items(
        collection = 'bld-fts-building-4',
        params = {
            'filter': "constructionmaterial IN ('Mixed (Masonry And Metal)','Brick Or Block Or Stone')",
            'crs': '3857',
            'datetime': '2025-03-13T00:00:00Z/..'
        },
        filter_params = {
            'description':'Gas Distribution Or Storage Facility',
            'buildinguse':'Utility Or Environmental Protection',
            'constructionmaterial':'Brick Or Block Or Stone'
        },
        hierarchical_output = True,
        use_latest_collection = True,
            headers = {
            'erroneous-header': 'should-be-ignored',
            'key': KEY
        },
    )