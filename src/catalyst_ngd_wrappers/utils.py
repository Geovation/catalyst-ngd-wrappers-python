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


def construct_bbox_filter(
        bbox_tuple: tuple[float | int] | str = None,
        xmin: float | int = None,
        ymin: float | int = None,
        xmax: float | int = None,
        ymax: float | int = None
) -> str:
    '''Constructs a bounding box filter for an API query.'''
    if bbox_tuple:
        return str(bbox_tuple)[1:-1].replace(' ', '')
    list_ = []
    for z in [xmin, ymin, xmax, ymax]:
        if z is None:
            raise AttributeError(
                'You must provide either bbox_tuple or all of [xmin, ymin, xmax, ymax]')
        list_.append(str(z))
    if xmin > xmax:
        raise ValueError('xmax must be greater than xmin')
    if ymin > ymax:
        raise ValueError('ymax must be greater than ymin')
    return ','.join(list_)


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
