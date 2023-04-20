## Command line interface

Geotrouvetout can be accessed through a command line interface or a REST API, here is a description of all arguments you may use and their function.

## `geotrouvetout --version`

This argument returns the current version of the program.

## `geotrouvetout -i image --image image

This argument returns a list of likely candidates from the image file. Here is an example of how you may use this argument.

```bash
geotrouvetout -i image.jpg
```

With this argument the program will perform the complete identification of the image and return a list of candidates that have a confidence over 1%. Countries that have a confidence percentage for their guess under are not displayed.

## `goetrouvetout -d --daemon`

This argument will start the program in daemon mode, in this mode the REST API will start and be accessible. This is the argument used for within the container for the `systemd` service.


## `geotrouvetout -h --help`

This argument retuns the list of arguments you may use with the program.

## `geotrouvetout -v -vv -vvv`

This argument allows for a more verbose logging.
