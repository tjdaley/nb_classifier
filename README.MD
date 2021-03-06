# nb_classifier
## Suite of Python apps for training and running a restful classifier service.
There are a number of programs in this project archive, each leading toward a trained
classifier that can be run as a web service.

These programs fit together like this:

![presentation1](https://user-images.githubusercontent.com/14339485/28243382-e18e3d28-698c-11e7-9bfe-82faecacb688.png)

# Applications
## sample_analyzer.py
This program goes through a training file, looks for duplicate utterances, and visually illustrates the distribution
of classifications. A poorly balanced training set will lead to a poorly-performing classifier. This program helps
you see whether your training file is balanced as per your expections of how classifications are distributed in the
real world.

For example, let's say you have two class: YES and NO. Let's also say that you expect there to be significantly more
YES than NO. If your training sample has significantly more NO instances, then the P(NO) value will cause the classifier
to improperly "guess" that new observations are more likely to be NO when it can't figure out which class to use.

Here's an example of the output:
![analyzer](https://user-images.githubusercontent.com/14339485/28240482-6b8ada3a-6948-11e7-86ec-9cf4395e9e80.png)

## class_reviewer.py
This program opens a json-formatted training file and runs the user through each observation. The user is presented
with the existing class assignment and given the option to KEEP the existing class assignment, DELETE the record from
the training set, or reassign the observation to a new class. (Classes are loaded from ```labels.py```.)

When the program starts, the user is prompted to select a json file to process:

![fopen](https://user-images.githubusercontent.com/14339485/28240484-9157a5a4-6948-11e7-9c5a-204825f8ec20.png)

The user is then presented with the classification UI. If the user is using a touch-enabled device, this program is
super easy to rip through:

![assign](https://user-images.githubusercontent.com/14339485/28240486-a0a78ef2-6948-11e7-96c1-aa7427ebac87.png)

Note that the user can edit the text that is being analyzed.

The user's options for each record are:

1. Keep the existing text and class assignment.
2. Keep the existing text but assign it to a new class.
3. Change the existing text, but keep the existing class assignment.
4. Remove the record from the training file.

When all the records have been processed, they are written to a file named "REV-" + {input file name} and the program ends:

![done](https://user-images.githubusercontent.com/14339485/28240492-aec61e5e-6948-11e7-8741-7f31bdeb14ee.png)

## nltk_trainer.py
This program takes an input file and trains & saves the classifier. It presents some informational
messages as it processes and also shows some information about the classifier, including its accuracy.

You can train it on your entire input file, or have it automatically divide the input file into
a training set and a testing set by using the ```-s``` command line switch.

When the training process is complete, the classifier is serialized to a pickle file, which by
default is called ```naivebayes.pickle```. You can override that with the ```-O``` switch.

Here is the command help:
```
usage: nltk_trainer.py [-h] [-o OUTPUT] [-s] file

Train and pickle a Naive Bayes classifier

positional arguments:
  file                  File to process

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file to persist classifier to. [naivebayes]
  -s, --separate        Should input files be separated into training and
                        testing sets? [NO]
```

## nltk_classifier_service.py
Finally, there is the classification service. It is a web service that recieves queries, runs
them through the classifier, and sends a json-formatted response indicating which classifiation
the classsifier assigned to the query. The output is compatible with Microsoft's LUIS web output.
output is not identical, but if you have programmed against the LUIS web API, your program
will be able to use this classifier service just fine.

Every time the classifier service gets a request, it logs the request along with the class it
assigned and the confidence score to an output file (```-O``` option). This file can be fed into
the ```class_reviewer.py``` application for refinement. The output from that can be appended to the
training file and the classifier can then be retrained with the benefit of the new information
received from users and their use cases.

### Request syntax
```
http://127.0.0.1/classify?verbose&zeros&q=i+want+a+divorce
```
#### /classify
This indicates which service you are trying to reach. At this time, ```classify``` is the only service available.

#### q
REQUIRED

Provides the query string that is to be classified. Needs to be URL-encoded.

#### verbose
* OPTIONAL
* DEFAULT = False

If present, this argument will cause the classifier to respond with a list of all non-zero classification scores.

#### zeros
* OPTIONAL
* DEFAULT = False

If present with the ```verbose``` flag, then even classifications that have a zero score will be returned in the response.

### Response Format

Query
```http://127.0.0.1:8282/classify?i+want+a+dvorce```

Response
```
{
  "entities": [],
  "query": "i want a divorce",
  "topScoringIntent": {
    "intent": "DIV",
    "score": "0.9851"
  }
}
```

Query
```http://127.0.0.1:8282/classify?i+want+a+divorce&verbose```

Response
```
{
  "entities": [],
  "intents": [
    {
      "intent": "QDRO",
      "score": "0.0147"
    },
    {
      "intent": "DIV",
      "score": "0.9851"
    },
    {
      "intent": "MODS",
      "score": "0.0001"
    }
  ],
  "query": "i want a divorce",
  "topScoringIntent": {
    "intent": "DIV",
    "score": "0.9851"
  },
  "words": [
    "divorc"
  ]
}
```

NOTE: This classifier service does NOT support entity recognition at this time. The entities array is provided in the response for
LUIS compatibility.

NOTE: The words array shows you what words were submitted to the classifier. This is what is left over after stop-words are
eliminated and the query is processed by a stemmer and a bi-grammer.

For example, the query: ```q=baby+daddy+not+paying+child+support``` would result in this words array (subject to change):
```
"words": [
    "child",
    "parent",
    "notpay",
    "childsupport"
  ]
```

Notice how "baby daddy" is transformed to "parent" and "child support" is bi-grammed into "childsupport" so that it's treated as a
single entity. (This is a clue that we're using a Naive Bayes classifier and trying to work around some of the naivete.)

Query
```http://127.0.0.1:8282/classify&q=i+want+a+divorce&verbose&zeros```

Response
```
{
  "entities": [],
  "intents": [
    {
      "intent": "QDRO",
      "score": "0.0147"
    },
    {
      "intent": "DIV",
      "score": "0.9851"
    },
    {
      "intent": "MODS",
      "score": "0.0001"
    },
    {
      "intent": "SAPCR",
      "score": "0.0001"
    },
    {
      "intent": "MODP",
      "score": "0.0000"
    },
    {
      "intent": "$DIV",
      "score": "0.0000"
    },
    {
      "intent": "ENFS",
      "score": "0.0000"
    },
    {
      "intent": "LSEP",
      "score": "0.0000"
    },
    {
      "intent": "ANSW",
      "score": "0.0000"
    },
    {
      "intent": "ANNU",
      "score": "0.0000"
    }
  ],
  "query": "i want a divorce",
  "topScoringIntent": {
    "intent": "DIV",
    "score": "0.9851"
  },
  "words": [
    "divorc"
  ]
}
```


Here is the command help:
```
usage: nltk_classifier_service.py [-h] [-p PICKLE] [-o OUTPUT] [-l LISTEN]

Restore and use an NLTK classifier

optional arguments:
  -h, --help            show this help message and exit
  -p PICKLE, --pickle PICKLE
                        Pickle file to restore classifier from. [naivebayes]
  -o OUTPUT, --output OUTPUT
                        Name of file to log classification responses to for
                        further supervised training
  -l LISTEN, --listen LISTEN
                        TCP port to listen on. [8282].
```

# Author
Thomas J. Daley, J.D. <tjd@powerdaley.com>

# Keywords
python
naive bayes classifier
restful web service