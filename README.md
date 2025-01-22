# Local Deployment
1. Create a .env file with OS DataHub account details, as specified in .env.sample
3. Create .venv with _python -m venv .venv_ and activate with _source .venv/bin/activate_
2. Install requirements with _pip install -r requirements.txt_
3. Launch flask application with _flask --app app\_flask/main run_
4. Access the development server on http://127.0.0.1:5000

# CatalyST-NGD-Wrappers

***Chart specifying valid orders to 'chain' different wrapper functions/extensions together***

- _Subtitles specifying the naming convention and ordering for python function names, and the corresponding final component of API paths_

- _Eg. the api url which combines OAuth2, the feature limit exentension, and the multiple collections extension will finish .../items/auth-limit-col?..._

```mermaid
graph TD
    A[OAuth2_manager<br><em>auth</em>]
    --> B[feature_limit_extension<br><em>limit</em>]
    A --> C[multigeometry_search_extension<br><em>geom</em>]
    A --> D[multiple_collections_extension<br><em>col</em>]
    B --> C
    B --> D
    C --> D
```

# API Documentation

- All the Catalyst APIs extend the core functionality of GET request for items using the OS NGD API - Features
    - The endpoint for this API is https://api.os.uk/features/ngd/ofa/v1/collections/{collectionId}/items
    - Documentation for the API can be found on the [OS Data Hub](https://osdatahub.os.uk/docs/ofa/overview) and on the [Gitbook docs for the National Geographic Database (NGD)](https://docs.os.uk/osngd/accessing-os-ngd/access-the-os-ngd-api/os-ngd-api-features)

- items_handler
    - Endpoint
        - http://127.0.0.1:5000/catalyst/features/ngd/ofa/v1/collections/{collectionId}/items
    - Description
        - A basic wrapper which does little more than replicate the functionality of 
    - 
                collection (str) - the feature collection to call from. Feature collection names and details can be found at https://api.os.uk/features/ngd/ofa/v1/collections/
        query_params (dict, optional) - parameters to pass to the query as query parameters, supplied in a dictionary. Supported parameters are: bbox, bbox-crs, crs, datetime, filter, filter-crs, filter-lang, limit, offset
        filter_params (dict, optional) - OS NGD attribute filters to pass to the query within the 'filter' query_param. The can be used instead of or in addition to manually setting the filter in query_params.
            The key-value pairs will appended using the EQUAL TO [ = ] comparator. Any other CQL Operator comparisons must be set manually in query_params.
            Queryable attributes can be found in OS NGD codelists documentation https://docs.os.uk/osngd/code-lists/code-lists-overview, or by inserting the relevant collectionId into the https://api.os.uk/features/ngd/ofa/v1/collections/{{collectionId}}/queryables endpoint.
        filter_wkt (string or shapely geometry object) - A means of searching a geometry for features. The search area(s) must be supplied in wkt, either in a string or as a Shapely geometry object.
            The function automatically composes the full INTERSECTS filter and adds it to the 'filter' query parameter.
            Make sure that 'filter-crs' is set to the appropriate value.