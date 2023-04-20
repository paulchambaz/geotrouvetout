# Methods

This program uses many methods to identify the location of the image.

## Combination

This is the "meta-method", while not an identification method itself, the combination is key to combining the different result of the different methods.

Combination uses bayesian probabilies, as such the probability can be updated from new information after a given result. It starts with the a-priori knowledge of the area of each country. It then uses bayesian updating to update with all other methods.

## Area

The most simple method we implemented is area, which returns the probability that we are in a country from its area. The idea is all things being equal, there is a much higher probability to end up in Russia than in the Vatican, being respectively the largest and smallest countries on earth. However, because this method has been "watered down", and each area is overestimated because it did not provide a good discrimination for a given image.

## Color analysis

This method consists of evaluating the probability of being in a given country from how close the colors are to a country average. To be more precise, each country has an average for five zones of each image. The top one representing the sky, the middle top one, for buildings or vegetation, the middle bottom one, for the buildings, houses, appliances, the bottom center one for the roads and the bottom side one for pavement, dirt or grass. For each of these zone, a histogram for the hue, saturation and value of 10 bins has been computed from a dataset of 10k images. The program computes these for the given image and uses a distance computation to estimate the probability of being in the country from how similair the result is for from a given country average.

## Language detection

This method is the most complex in the program. First we use YOLO to get bounding box of traffic signs in the image, from which we get new imgages of traffic sign in the image. This YOLO model has been trained on a large dataset of traffic sign to get better result. Then we use a combination of image processing to get black on white, perspective corrected text from the traffic sign images. After that we use the OCR library `pytesseract` to extract the text from the image. Finally we use `langdetect` to estimate the languages from the text. That gives us a list of languages, which we can use to estimate in which country we are.

## Car brand detection

Different brands are not always popular in every country. This was the idea that sparked the idea for this method. We trained a YOLO model to detect cars, and another to detect car brands from a given image. Finally we compiled geographic information about which car brand is popular in each country. The program then gets the car image from the given image, classifies its brand and returns the probability that we are in a given country from the geographic dataset.
