# REST API Documentation

The REST API has four endpoints that can be accessed at runtime. To start the REST API, please use the installation guide.

## `/version`

This endpoint returns the current version of the program.

## `/geo`

This endpoint returns the geolocation information gathered from an image, here is a small example on how this endpoint might be used.

```bash
curl -X 'POST' --data-binary '@image.jpg' 'https://geotrouvetout.chambaz.xyz/geo'
```

You may also check the web extension program from this repository for an example of how to access this endpoint from a browser in `typescript`.


## `/docs`

This endpoint returns the list of endpoints and their functions.

## `/cache`

This endpoint returns the list of hashes for the overpass api.

## `/cache/{hash}`

This endpoint returns the value returned from a hash from the overpass api.
