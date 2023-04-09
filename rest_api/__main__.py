"""! @brief REST API for geotrouvetout."""

from PIL import Image
import io
import base64
from fastapi import FastAPI, File, Body, Request
from pydantic import BaseModel

import geotrouvetout

app = FastAPI()


@app.post("/locate")
async def locate_image(request: Request):
    """! Endpoint for the geoguessr REST API.
    @param image The image sent to the REST API
    @return A json containing information about the image
    """
    # we need to convert the image
    contents = await request.body()
    image = Image.open(io.BytesIO(contents))

    json = geotrouvetout.get_country(image)

    return json
