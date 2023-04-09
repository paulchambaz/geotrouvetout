# geotrouvetout

This program is a geoguessr assistant, giving it a google street view image, it will return best guesses for the country in which the picture has been taken.
There is a command line tool, which can be used to gather best guesses, a REST API containerized and a browser extension to get an assistant from the browser.

This project uses various image analysis techniques, from color analysis, to object detection with yolo, ocr with pytesseract, various statistical analysis and geoguessr specific "quick" strategies.
It was developed as part of a supervised project course by Armand Sylvain and the Université Paris Cité. Four students worked on this project for a period of 3 months : David Bret, Paul Chambaz, Fériel Cheggour and Marion Mazaud.
This program is free software, and all data associated with this project has been posted online with a free software license : GPLv3.

- The source code is available on [this Github page](https://github.com/paulchambaz/geotrouvetout).
- The docker container is available on [docker-hub](https://hub.docker.com/r/paulchambaz/geotrouvetout) for easy deployment.
- The dataset used for statistics and training is available on [kaggle](https://kaggle.com/paulchambaz/google-street-view).
- The python package is available on [pip](https://pypi.org/project/geotrouvetout).
- The extension is available on the [firefox](https://) and [google](https://) extension stores.

## Installation

### Browser extension

If you want to install this project on your web browser, just navigate on the [store](https://) or [google store](https://) and you can simply download it from there.

### Docker container on server

If you want to get the docker container and use it on your server, please follow this guide.

You most likely want to run these commands with sudo or as root.

```bash
docker pull paulchambaz/geotrouvetout:latest
# to get a executable for starting the program from the command line
curl -o /usr/bin/geotrouvetout https://raw.githubusercontent.com/paulchambaz/geotrouvetout/master/target/geotrouvetout
chmod +x /usr/bin/geotrouvetout
# to get a systemctl service to manage the program as a daemon
curl -o /etc/systemd/system/geotrouvetout.service https://raw.githubusercontent.com/paulchambaz/geotrouvetout/master/target/geotrouvetout.service
systemctl daemon-reload
# to get a nginx reverse proxy - YOU WILL NEED TO CONFIGURE YOUR DOMAIN NAME
curl -o /etc/nginx/conf.d/geotrouvetout.conf https://raw.githubusercontent.com/paulchambaz/geotrouvetout/master/target/geotrouvetout.conf
nginx -t
# to get https for the reverse proxy
certbot --nginx
```

### Command line tool

Finally you can get the program to work with it from pip or github :

```
pip install geotrouvetout
git clone https://github.com/paulchambaz/geotrouvetout.git
```

## Usage

### Docker container on server

Once you have the program installed on your server, you will want to start it, first run this command to check that there are no errors: 

```
geotrouvetout -d
```

To automate this command as a service, you can simply run :

```
systemctl start geotrouvetout.service
systemctl enable geotrouvetout.service
```

### Command line tool

If you have gotten the project from pip or from github, you can use this project as a simple command line tool :

```
# direct path to image
geotrouvetout -i path/to/image.jpg
# start a daemon for the rest api
geotrouvetout -d
```

## Tests

This project has been unit tested, if you want to run all tests, you can simply run : 

```
make test
```

This project has also been linted for style, if you want to lint the program, you can run :


```
make lint
```

If you want to do both, you can just do :


```
make full-test
```

## Tools

A number of tools have been created for this project :

- `get_country_labels` : which creates metadata for each each country.
- `get_gsv_img` : which allows for bulk download of google street view images with an api key.
- `stat_colors` : which does histogram color analysis for a bulk of images.
- `stat_colors_country` : which uses the result of stat colors to produce histogram color analysis for countries
- `train` : which automates the process of gathering Open Image Dataset data, labelizing it for YOLO training and training a YOLO model

## Todo

There were things we did not have the time to do for this program, if one wants to expand it, they can start here:

- Implement more quick strategies specific to geoguessr (car analysis, picture quality analysis, etc)
- A overpass, with auto caching has been implemented, but currently it is not used, one could try to use the connection with overpass to pin point the exact coordinates.
- Level of helps could be added if the program gives better result (1 could give the country, 2 could give the city and 3 could give the exact coordinates)
- [Similar projects](https://github.com/Stelath/geoguessr-ai) use complex convolution network to estimate the exact data, they have seen good result, but the dataset is only for us country. If one was able to construct a bigger and more diverse dataset, they could make use this technique to gather a new very powerful method to guess the country.
- A lot of other strategies can be used, such as using color analysis methods or object recognition methods to give a rural-urban index and use overpass to better guess the exact geolocation.

