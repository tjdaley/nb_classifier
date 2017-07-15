# nb_classifier
## Suite of Python apps for training and running a restful classifier service.
There are a number of programs in this project archive, each leading toward a trained
classifier that can be run as a web service.

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