from json import JSONDecodeError

from shapely.geometry import Point, LineString, Polygon
from shapely.geometry.base import BaseGeometry


def flatten_coords(list_of_lists: list) -> list:
    '''Flattens the coordinates of geojson features into a flattened list of coordinate pairs.'''
    result = []
    for item in list_of_lists:
        if isinstance(item[0], list):
            flattened = flatten_coords(item)
            result.extend(flattened)
        else:
            result.append(item)
    return result


def wkt_to_spatial_filter(wkt: str, predicate: str = 'INTERSECTS') -> str:
    '''Constructs a full spatial filter in conformance with the OGC API - Features standard from well-known-text (wkt)
    Currently, only 'Simple CQL' conformance is supported, therefore INTERSECTS is the only supported spatial predicate: https://portal.ogc.org/files/96288#rc_simple-cql'''
    return f'({predicate}(geometry,{wkt}))'


def construct_filter_param(**params) -> str:
    '''Constructs a set of key=value parameters into a filter string for an API query'''
    for k, v in params.items():
        if isinstance(str, v):
            params[k] = f"'{v}'"
    filter_list = [f"({k}={v})" for k, v in params.items()]
    return 'and'.join(filter_list)


def prepare_parameters(
    query_params: dict = None,
    filter_params: dict = None,
    wkt: str = None,
    **kwargs
) -> dict:
    '''
    Enables simpler implementation of query parameters for OS NGD API - Features requests in the following ways:
        - Simple equality (=) CQL filter parameters can be supplied as a dictionary - the CQL filter will be constructed automatically.
        - Well-known-text (wkt) geometries can be supplied as a string or Shapely geometry object, and the full CQL INTERSECTS filter will be constructed automatically.
        - Coordinate reference systems (CRS) can be supplied as EPSG numeric codes, and will be converted to the full OGC CRS URI format.
    '''

    if filter_params:
        filters = construct_filter_param(**filter_params)
        current_filters = query_params.get('filter')
        query_params['filter'] = f'({current_filters})and{filters}' if current_filters else filters

    if wkt:
        spatial_filter = wkt_to_spatial_filter(wkt)
        current_filters = query_params.get('filter')
        query_params['filter'] = f'({current_filters})and{spatial_filter}' if current_filters else spatial_filter

    for attr, val in query_params.items():
        if 'crs' not in attr:
            continue
        if val.isnumeric():
            authority_and_version = 'EPSG/0'
        elif val.startswith('CRS'):
            authority_and_version = 'OGC/1.3'
        else:
            continue
        query_params[attr] = f'http://www.opengis.net/def/crs/{authority_and_version}/{val}'
    return query_params


def multilevel_explode(shape: BaseGeometry) -> list[Polygon | LineString | Point]:
    '''
    Explode a geometry into its constituent parts.
    Where multigeometries contain other multigeometries, the layers are flattened into a single list, such that the results lists contains only single geomtries.
    '''

    if isinstance(shape, (Point, LineString, Polygon)):
        return [shape]

    lower_shapes = shape.geoms
    result_list = []
    for lshape in lower_shapes:
        lower_shape_exploded = multilevel_explode(lshape)
        result_list.extend(lower_shape_exploded)
    return result_list


def handle_decode_error(error: JSONDecodeError, status_code: int = 500) -> dict:
    '''Handles JSONDecodeError exceptions by extracting the error message and returning a structured error response.'''
    error_string = str(error)
    if error_string.startswith('Expecting value'):
        status_code = 414
        error_string = {
            'Error Text': error_string,
            'Help (Catalyst)': 'This could be due to a request URI which is too long or an input geometry which is too complex.'
        }
    return {
        "code": status_code,
        "description": error_string,
        "errorSource": "OS NGD API"
    }
