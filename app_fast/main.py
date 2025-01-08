from typing import Union

from fastapi import FastAPI

from pydantic import BaseModel
from typing import Optional

from NGD_API_Wrappers import *

app = FastAPI()


class NGDQueryParams(BaseModel):
    crs: Optional[str] = None
    bbox: Optional[str] = None
    bbox_crs: Optional[str] = None
    datetime: Optional[str] = None
    filter: Optional[str] = None
    filter_crs: Optional[str] = None
    filter_lang: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

@app.get("/catalyst/features/ngd/ofa/v1/collections/{collection}/items/items-auth-limit")
def read_item(collection: str, params: NGDQueryParams):
    kwargs = params.model_dump()
    result = multigeometry_search_extension(collection = collection, **kwargs)
    return result

@app.get("/test/")
async def read_items(**kwargs):
    return kwargs