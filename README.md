# NGD Wrappers python 

This is a python package which extends and enhances the flexibility and functionality of Ordnance Survey NGD API - Features.

## Features

1. Wrapping core [OS NGD API - Features](https://docs.os.uk/osngd/getting-started/access-the-os-ngd-api/os-ngd-api-features) functionality
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
8. Automatic Oauth2 authentication
   - When CLIENT_ID (project api key) and CLIENT_SECRET (project api secret) are provided as environment variables, authentication is processed automatically via 5-minute access tokens.
   - Once these environment variables are supplied, the user does not need to do any further action to authenticate their requests.

## Documentation

### catalyst_ngd_wrappers.items

ngd_items_request(collection: str, params: dict = None, headers: dict = None, use_latest_collection: bool = False, authenticate: bool = True, log_request_details: bool = True, wkt: str = None, filter_params: dict = None, **kwargs)

A wrapper for the [OS NGD API - Features](https://docs.os.uk/osngd/getting-started/access-the-os-ngd-api/os-ngd-api-features). Some additional tools beyond the core API functionality are provided:
- Automatic OAuth2 authentication handling through environment variables. 
- Automatic construction of simple 'description' filter parameters.
- Automatic construction of spatial filters from well-known-text.
- Automatic use of latest versions of OS collections.

**Parameters:**
   - **collection** (str) - The OS NGD feature collection to call from. Feature collection names and details can be found at https://api.os.uk/features/ngd/ofa/v1/collections/.
   - **params** (dict, optional) - Parameters to pass to the API request as query parameters, supplied in a dictionary. Supported parameters are: key, bbox, bbox-crs, crs, datetime, filter, filter-crs, filter-lang, limit, offset. Find details of these API parameters on the [OS technical docs](https://docs.os.uk/osngd/getting-started/access-the-os-ngd-api/os-ngd-api-features/technical-specification/features#get-collections-collectionid-items).
   - **filter_params** (dict, optional) - OS NGD attribute filters to pass to the query within the 'filter' query_param. The can be used instead of or in addition to manually setting the filter in params.
      The key-value pairs will appended using the EQUAL TO [ = ] comparator. Any other CQL Operator comparisons must be set manually in params. Queryable attributes can be found in OS NGD codelists documentation https://docs.os.uk/osngd/code-lists/code-lists-overview, or by inserting the relevant collectionId into the [https://api.os.uk/features/ngd/ofa/v1/collections/{{collectionId}}/queryables](https://docs.os.uk/osngd/getting-started/access-the-os-ngd-api/os-ngd-api-features/technical-specification/queryables) endpoint.
   - **wkt** (string or shapely geometry object, optional) - A means of searching a geometry for features. The search area(s) must be supplied in wkt, either in a string or as a Shapely geometry object. The function automatically composes the full INTERSECTS filter and adds it to the 'filter' query parameter. Make sure that 'filter-crs' is set to the appropriate value.
   - **use_latest_collection** (boolean, default False) - If True, it ensures that if a specific version of a collection is not supplied (eg. bld-fts-building[-2]), the latest version is used. If 'collection' does specify a version, the specified version is always used regardless of use_latest_collection.
   - **authenticate** (boolean, default True) - If True, the request is authenticated using OAuth2. This requires the CLIENT_ID and CLIENT_SECRET environment variables to be set. If False, no authentication is used, and an API key must be supplied in either the headers or params.
   - **log_request_details**: bool, default True - If True, adds extra telemetry metadata to the request, which can be used for logging when deployed as an API.
   - **\**kwargs** - Other parameters to be passed to the [request.Session.request get method](https://requests.readthedocs.io/en/latest/api/#requests.Session.request) eg. headers, timeout.

### limit extension

This extension serves to extend the maximum number of features returned above the default maximum 100 by looping through multiple requests.

**Parameters:**
   - **limit** (int, optional) - The maximum number of features to be returned by looping through multiple NGD requests. With the limit extension, this paramater must be supplied as a direct function parameter, rather than as a key-value pair in params.
   - **request_limit** (int, default 50) - An alternative means of limiting the response; by number of requests rather than features. Each OS NGD Feature request returns a maximum of 100 features.
   - **\**kwargs** - Other parameters passed to `catalyst_ngd_wrappers.items`.

**IMPORTANT**: When the limit extension is used alongside the geom and/or col extensions, the limit and request_limit constraints apply _per search area, per collection_. Consider [pricing](https://osdatahub.os.uk/plans).

To prevent indefinite requests and high costs, **at least one of limit or request_limit must be provided**, although there is no limit to the upper value these can be. The function will make multiple requests to the function to compile all features from the specified collection, returning a dictionary with the features and metadata. When both limit and request_limit are applied, the lower constraint is applied.

Returns the features as a geojson, as per the OS NGD API.

### geom extension

An alternative means of returning OS NGD features for a search area which is GeometryCollection or a multi-geometry (MultiPoint, MultiLinestring, MultiPolygon). This will in some cases improve speed, performance, and prevent the call from timing out.

**Parameters:**
   - **wkt** (string or shapely geometry object, optional) - A means of searching a geometry for features. The search area(s) must be supplied in wkt, either in a string or as a Shapely geometry object. Multi-geometries and Geometry Collections may be supplied, and any hierarchical geometries will first be flattened into a list of single-geometry search areas. The function automatically composes the full INTERSECTS filter and adds it to the 'filter' query parameter. Make sure that 'filter-crs' is set to the appropriate value.
   - **hierarchical_output** (bool, default False) - If True, then results are returned in a hierarchical structure of GeoJSONs according to search area (and collection if applicable). If False, results are returned as a single GeoJSON.
   - **\**kwargs** - Other parameters passed to `catalyst_ngd_wrappers.items`, or the limit extension if applied.

Each component shape of the multi-geometry will be searched in turn. When a hierarchical multi-geometry is supplied (eg. a GeometryCollection containing MultiPolygons), it is flattened into a single set of its component single-geometry shapes.

The results are returned in a quasi-GeoJSON format, with features returned under 'searchAreas' in a list, where each item is a json object of results from one search area.
The search areas are labelled numerically, with the number stored under 'searchAreaNumber'.

NOTE: If a limit is supplied for the maximum number of features to be returned or requests to be made, this will apply to _each search area individually_, not to the overall number of results.

### col extension

**Parameters:**
   - **collection** (list of str) - A list of [OS NGD features collections](https://docs.os.uk/osngd/getting-started/access-the-os-ngd-api/os-ngd-api-features/technical-specification/features#get-collections-collectionid-items) to call from.
   - **hierarchical_output** (bool, default False) - If True, then results are returned in a hierarchical structure of GeoJSONs according to collection (and search area if applicable). If False, results are returned as a single GeoJSON.
   - **\**kwargs** - Other parameters passed to `catalyst_ngd_wrappers.items`, or the limit/geom extension if applied.

## Output Specifications
- **Format**
    GeoJSON by default. If the _hierarchical-output=True_, a hierarchical json containing separate GeoJSONs according to collection and/or search area number. For failed requests, see 'Failed request response format' below.
- **Response Metadata**:
    - Attributes from OS NGD API - Features items request (refer to docs above for details)
        - **type**: str
        - **timeStamp**: str (date-time) - Format "YYYY-MM-DDTHH:MM:SS.sssssssZ"
        - **numberReturned**: int
        - **features**: array of Feature (object)
        - **links** - This is absent if either _limit_ extension is applied, or if _hierarchical-output=False_ (if this attribute applies).
        This is because in these cases the GeoJSON(s) comprising the response do not represent a single NGD feature request.
    - Additional Catalyst attributes
        - **numberOfReqeusts**: int - The number of NGD items requests from which the final response is compiled
        - **numberOfRequestsByCollection**: dict[str: int] - The number of NGD items requests made, split by collection. Only included when _col_ extension applied and _hierarchical-output=False_.
        - **numberReturnedByCollection**: dict[str: int] - The number of features returned, split by collection.
        - **telemetryData**: dict - Only applies for the base wrapper. Contains a record of the telemetry data which has been logged.
            - Method
            - URL Path
            - Path parameters
            - Query Parameters
            - Spatial bounding box of the response
            - Number returned
- **Feature-Level Attributes**
    - **id**: str (uuid) - OSID of the feature
    - **collection**: str - Collection the feature belongs to. This is an additional attribute supplied by catalyst
    - **geometry**: dict - List-like representation of the feature's geometry, and the geometry type
    - **searchAreaNumber**: int | list - The number of the search area where the feature is found. If a feature intersects multiple search areas, the numbers are given in a list. Only inclded when _geom_ extension applied and _hierarchical-output=False_. 
    - **properties**: dict - Non-spatial attribution associated with the feature
        - OS NGD attribution for each theme, collection, and feature type [here](https://docs.os.uk/osngd/data-structure)
        - The collection name is added by catalyst
        - When the _geom_ extension is applied, the searchAreaNumber value is also included
    - **type**: str - object type ("Feature")
- **Failed Response Format**
   Json object specifying error metadata.  As the wrapper mimics the behaviour of an API and is designed for [API deployment](https://github.com/Geovation/catalyst-ngd-wrappers-azure).
   - **code**: int - The error code, either from the OS NGD API or from the wrapper.
   - **description**: str
   - **help**: str - Where appropriate, a link to relevant documentation.
   - **errorSource**: str - either 'OS NGD API' or 'Catalyst Wrapper', specifying whether the error arose within the NGD API or in the wrapper code.

## Install

The library can be installed using `pip`. It is not currently published to a repository such as PyPI but it can be installed by direct link to the latest version tag on GitHub.

```console
$ pip install git+https://github.com/Geovation/catalyst-ngd-wrappers-python@0.2.0
```

Replace the version tag with the latest version. To upgrade, reinstall with the latest tag (or whichever tag you choose).

## Usage

### Latest Collections Wrapper
```python
from catalyst_ngd_wrappers.ngd_api_wrappers import get_latest_collection_versions

# Returns a mapper between base collections names and their latest versions
latest_collections_data = get_latest_collection_versions()

# ...with updates in the last month flagged
latest_collections_with_updates_flagged = get_latest_collection_versions(recent_update_days = 31)
```

### Features Wraper
```python
from catalyst_ngd_wrappers.ngd_api_wrappers import items_limit_geom_col

collection = ['bld-fts-building', 'trn-ntwk-road', 'wtr-fts-water']

wkt = 'GEOMETRYCOLLECTION (POLYGON ((400000 400000, 400090 400050, 400050 400000, 400000 40050, 400000 400000)), LINESTRING(399990 399990, 399000 399000))'
universal_crs = 27700
limit = 300

os.environ['CLIENT_ID'] = '<YOUR_PROJECT_API_KEY>'
os.environ['CLIENT_SECRET'] = '<YOUR_PROJECT_API_SECRET>'

# Returns a hierarchical set of geojsons containing OS data for for latest versions of selected collections, for the set of search areas provided'
data = items_limit_geom_col(
    collection = collection,
    wkt = wkt,
    use_latest_collection = True,
    hierarchical_output = True
    query_params = {
        'wkt': universal_crs,
        'filter-crs': universal_crs,
        'limit': limit,
    }
)
```
