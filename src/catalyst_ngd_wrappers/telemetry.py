import os

from .utils import flatten_coords

LOG_REQUEST_DETAILS: bool = os.environ.get(
    'LOG_REQUEST_DETAILS', 'True') == 'True'
QUERY_PARAM_TELEMETRY_LENGTH_LIMIT: int = int(
    os.environ.get('QUERY_PARAM_TELEMETRY_LENGTH_LIMIT', '200'))

def prepare_telemetry_custom_dimensions(
        json_response: dict,
        url: str,
        collection: str,
        query_params: dict
    ) -> dict:
    '''
    Prepares custom telemetry dimensions for logging request details.
    Extracts relevant information from the JSON response and query parameters, including bounding box, number of returned features, and request method.
    Returns a dictionary of custom dimensions for telemetry logging.
    '''

    compiled_features = [feature['geometry']['coordinates']
        for feature in json_response['features']]
    flattened_coords = flatten_coords(compiled_features)
    xcoords, ycoords = [], []
    for pair in flattened_coords:
        xcoords.append(pair[0])
        ycoords.append(pair[1])
    bbox = (min(xcoords), min(ycoords), max(xcoords),
            max(ycoords)) if xcoords and ycoords else ''
    custom_dimensions = {
        'method': 'GET',
        'url.path': url,
        'url.path_params.collection': collection,
        'response.bbox': bbox,
        'response.numberReturned': json_response['numberReturned'],
    }

    for k, v in query_params.items():
        value = 'REDACTED due to length' if k == 'filter' and len(
            v) > QUERY_PARAM_TELEMETRY_LENGTH_LIMIT else v
        custom_dimensions[f'url.query_params.{str(k)}'] = value

    return custom_dimensions
