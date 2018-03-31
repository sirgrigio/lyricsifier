# Lyricsifier
Lyricsifier is a python app built with the intent of understanding if a correlation exists between a song genre and its lyrics.

It allows to:
* build a dataset of song lyrics by scraping [metrolyrics.com](http://metrolyrics.com); 
  * see `lyricsifier crawl --help` and `lyricsifier extract --help`;
* retrieve song genres from [last.fm](http://last.fm);
  * see `lyricsifier tag --help`;
* build a training set using song lyrics and genres;
  * see `lyricsifier vectorize --help`;
* clustering the training set using k-means;
  * see `lyricsifier cluster --help`;
* training and testing different machine learning algorithms: perceptron, multi-layered perceptron, multinomial naive bayes, random forest and support vector machine;
  * see `lyricsifier classify --help`;

## Usage
```bash
$ lyricsifier --help
usage: lyricsifier [-h] [--debug] [--quiet]
                   {default,classify,cluster,crawl,extract,tag,vectorize} ...

Attempt to classify songs by their lyrics

optional arguments:
  -h, --help            show this help message and exit
  --debug               toggle debug output
  --quiet               suppress all output

sub-commands:
  {default,classify,cluster,crawl,extract,tag,vectorize}
    classify            classify the testset upon training on the trainset
    cluster             cluster the dataset
    crawl               crawl lyrics URL from metrolyrics.com
    extract             extract lyrics from urls
    tag                 tag the given tracks
    vectorize           create a vectorize dataset
```
