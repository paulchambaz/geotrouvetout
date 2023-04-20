# Tools

Many tools we made for this project, we wanted to avoid as much as possible network requests, so a lot of data has been downloaded and processed so it can be used offline.

## `get_country_labels`

This script compiles extra information about countries, this allows for not using geopy in real time, which requires network requests.

## `get_gsv_img`

This script is used to download Google Street View image in a bulk. It was used to get datasets. To use it, you will need an API Key from Google.

## `stat_colors`

This script is used to compute histograms for HSV for zones in an image for a dataset and produces a json that can then be used to compute national or even regional averages.

## `stat_colors_country`

This script is used to compute national averages from the resulting json of `stat_colors`

## `train`

This script can be used to automate the download, formatting and training of weight for YOLO. First, it will download necessary files, then download a dataset from the keyword given to it (eg. Car), then format the dataset to YOLO specification and finally train the model with YOLO. This means that you may do :

```bash
sh train.sh 'Tree'
```

And you will get a file `tree.pt` that corresponds to weights detecting bounding boxes of tree in an image.
