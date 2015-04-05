# Expressive performance

This repository contains an implementation of a performance rendering system proposed [here](http://staff.science.uva.nl/~bredeweg/pdf/BSc/20102011/VanDerWeij.pdf).

Also included are a bunch of tools for manipulating midi and musicxml files and loading and parsing files form the CrestMusePEDB expressive performance database.

This repository was used for the project that concluded my Bachelor in Artificial Intelligence at the University of Amsterdam.

### Method

#### Preprocessing

Extract the melody from the full score of the work.

### Generative model of expressive performance

* Segment the score into phrases
* Extract features for each phrase (a lot of these are relative ratios, take the log of these)
* Discretise features nonlinearly using a sigmoid function
* Align phrases with their performance
* Determine performance per phrase
* Extract performance features per phrase

### Future work

* Plug in a more reliable melody extractor
* Plug in a more sensible (hierarchical) phrase segmentation system
* Include expressivity notation in the score
* Extend performance features to capure more subtleties (such as accellerandos, riterdandos, crescendos and diminuendos)

