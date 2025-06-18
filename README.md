# CatalyST-NGD-Wrappers

CatalyST_NGD_Wrappers is a package which extends and enhances the flexibility and functionality of Ordnance Survey NGD API - Features.

## Features

1. Wrapping core OS NGD API - Features functionality
    - Calls to the [Features](https://docs.os.uk/osngd/getting-started/access-the-os-ngd-api/os-ngd-api-features/technical-specification/features) and [Collections](https://docs.os.uk/osngd/getting-started/access-the-os-ngd-api/os-ngd-api-features/technical-specification/collections) endpoints can be made through python functions.
2. Limit Extension
     - The default upper limit for the number of features returned can be extended above the default of 100 through automatic pagination.
3. Geometry Extension
    - Multi-geometry search areas can be provided as spatial filters, including Geometry Collections.
    - Each search area is searched in turn.
    - The base NGD API is low-performing when multigeometries are searched and the component geometries are a long way apart. The wrapper resolves this issue.
4. Collection Extension
    - Multiple collections can be searched at once.
    - This is useful when data relevant to a use-case spans multiple collections.
5. Latest Collections
    - Retrieve a simple list of the latest schema versions available for each NGD collection, for for a specified set.
    - The latest schema version for a given collection can be automatically used for a features request.
6. CRS Specification
    - Short/simple versions of CRS codes can be used (eg. 27700, 4326, CRS84) instead of the full URIs.
    - This applies for all crs parameters:
        - crs
        - bbox-crs
        - filter-crs
7. Filter Parameters
    - Rather than writing full CQL filters, filter parameters for equality (=) can be supplied as a dictionary.
    - Rather than writing a full CQL spatial filter, WKT geometries can be supplied as a separate parameter.
8. - Automatic Oauth2 authentication
    - When CLIENT_ID (project api key) and CLIENT_SECRET (project api secret) are provided as environment variables, authentication is processed automatically via 5-minute access tokens.
    - Once these environment variables are supplied, the user does not need to do any further action to authenticate their requests.

## Installation

```
pip install git+https://github.com/Geovation/catalyst-ngd-wrappers-python
```

## Usage

```python
import catalyst_ngd_wrappers

collection = ['bld-fts-building', 'trn-ntwk-road', 'wtr-fts-water']
use_latest_collection = True
wkt = 'GEOMETRYCOLLECTION (POLYGON ((400000 400000, 400090 400050, 400050 400000, 400000 40050, 400000 400000)), LINESTRING(399990 399990, 399000 399000))'
filter_crs = 27700
limit = 300

os.environ['CLIENT_ID'] = '<YOUR_PROJECT_API_KEY>'
os.environ['CLIENT_SECRET'] = '<YOUR_PROJECT_API_SECRET>'

# Returns a hierarchical set of geojsons containing OS data for for latest versions of selected collections, for the set of search areas provided'
data = items_limit_geom_col(
    collection = collection,
    wkt = wkt,
    use_latest_collection = use_latest_collection,
    hierarchical_output = True
    query_params = {
        'filter-crs': filter_crs,
        'limit': limit,
    }
)
```