import argparse
import os.path
from datetime import datetime
from typing import final
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
import matplotlib.pyplot as plt
from operator import itemgetter, sub

# parse arguments
parser = argparse.ArgumentParser(
    description="Create wordclouds from Zendesk ticket data exports. Currently only csv format is supported."
)

parser.add_argument(
    "-f", "--file_path", help="Data file path. Defaults to data.csv", default="data.csv"
)
parser.add_argument(
    "-i",
    "--ignore_words",
    help="File containing the words to be ignored. Defaults to ignore_words.txt. If file is not found it will default to a list of commonly ignored words for English language.",
    default="ignore_words.txt",
)
parser.add_argument(
    "--start_date",
    help="Start date for data filtering. Format is YYYY-MM-DD",
    type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
)
parser.add_argument(
    "--end_date",
    help="End date for data filtering. Format is YYYY-MM-DD",
    type=lambda s: datetime.strptime(s, "%Y-%m-%d"),
)
parser.add_argument(
    "--field",
    help="Which column the text for worcloud will be taken from. Defaults to 'Subject'",
    default="Subject",
)
parser.add_argument(
    "-o",
    "--output",
    help="Output file name. Worcloud will be saved with that name as a PNG, and a TXT with the same name will be created with the report.",
)
parser.add_argument(
    "--svg",
    help="Save SVG version of wordcloud. Only works if output is specified.",
    action="store_true",
)
parser.add_argument(
    "--show_wordcloud",
    help="Choose wether to show the wordcloud when running the script. If no output file is defined this falg will be overridden and will always show it.",
    action="store_true",
)
parser.add_argument(
    "--show_top_words", help="Log top words to console", action="store_true"
)
parser.add_argument(
    "--show_ignore_words", help="Log ignored words to console", action="store_true"
)
parser.add_argument(
    "--top_words",
    help="Amount of top words to be displayed in report. Default is 20",
    type=int,
    default=20,
)

args = parser.parse_args()

# Read data file. Should be csv export from zendesk
data = pd.read_csv(args.file_path, index_col="Created at", parse_dates=True)
if args.start_date is not None:
    startDate = args.start_date
else:
    startDate = data.index[0]
if args.end_date is not None:
    endDate = args.end_date
else:
    endDate = data.index[-1]
if startDate > endDate:
    print(
        "Error: start date ({:s}) is later than end date ({:s}). Specified file contains data from {:s} to {:s}".format(
            startDate.strftime("%Y-%m-%d"),
            endDate.strftime("%Y-%m-%d"),
            data.index[0].strftime("%Y-%m-%d"),
            data.index[-1].strftime("%Y-%m-%d"),
        )
    )
    exit()
if args.start_date is not None or args.end_date is not None:
    data = data.loc[startDate:endDate]

# Iterate through data
dataWords = ""
for i in data[args.field]:
    i = str(i)
    separate = i.split()
    for j in range(len(separate)):
        separate[j] = separate[j].lower()
    dataWords += " ".join(separate) + " "

# Read ignore_words file
myStopWords = [
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "aren't",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can't",
    "cannot",
    "could",
    "couldn't",
    "did",
    "didn't",
    "do",
    "does",
    "doesn't",
    "doing",
    "don't",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "hadn't",
    "has",
    "hasn't",
    "have",
    "haven't",
    "having",
    "he",
    "he'd",
    "he'll",
    "he's",
    "her",
    "here",
    "here's",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "how's",
    "i",
    "i'd",
    "i'll",
    "i'm",
    "i've",
    "if",
    "in",
    "into",
    "is",
    "isn't",
    "it",
    "it's",
    "its",
    "itself",
    "let's",
    "me",
    "more",
    "most",
    "mustn't",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "ought",
    "our",
    "ours",
]
if os.path.isfile(args.ignore_words):
    fileObj = open(args.ignore_words, "r")  # opens the file in read mode
    myStopWords = fileObj.read().splitlines()  # puts the file into an array
    fileObj.close()
if args.show_ignore_words:
    print("Ignored words:")
    print("\n".join(myStopWords))

# Generate wordcloud
finalWordcloud = WordCloud(
    width=800,
    height=800,
    background_color="black",
    stopwords=myStopWords,
    min_font_size=10,
).generate(dataWords)

# Show wordcloud
if args.show_wordcloud or args.output is None:
    plt.figure(figsize=(10, 10), facecolor=None)
    plt.imshow(finalWordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.draw()  # this should prevent it from stopping the script

# Most repeated words report
if args.output is not None or args.show_top_words:
    dataWordsArr = dataWords.split()
    uniqueWords = set(dataWordsArr)
    for word in myStopWords:
        uniqueWords.discard(word)
    dataWordsFreq = []
    for word in uniqueWords:
        dataWordsFreq.append([word, dataWordsArr.count(word)])
    numOfTopWords = args.top_words
    if numOfTopWords > len(dataWordsFreq):
        print(
            "WARN: amount of top words to report ({:d}) is larger than total amount of words ({:d}). Showing all available words".format(
                args.top_words, len(dataWordsFreq)
            )
        )
        numOfTopWords = len(dataWordsFreq)
    dataWordsFreq = sorted(dataWordsFreq, key=itemgetter(1), reverse=True)
    topWordRep = ""
    dashSep = "-" * 35
    topWordRep += "Worcloud generated from file: {:s} for field: {:s} in tickets from {:s} to {:s}".format(
        args.file_path,
        args.field,
        startDate.strftime("%Y-%m-%d"),
        endDate.strftime("%Y-%m-%d"),
    )
    topWordRep += "\n"
    topWordRep += "\n"
    topWordRep += "Top " + str(numOfTopWords) + " words:"
    topWordRep += "\n"
    topWordRep += dashSep
    topWordRep += "\n"
    topWordRep += "{:<20s}{:<4s}{:>8s}".format("Word", "Freq", "%")
    topWordRep += "\n"
    topWordRep += dashSep
    for entry in dataWordsFreq[0:numOfTopWords]:
        topWordRep += "\n"
        topWordRep += "{:<20s}{:>4d}{:>8.1f}".format(
            entry[0], entry[1], entry[1] / data[args.field].size * 100
        )
    if args.show_top_words:
        print(topWordRep)

# Save files
if args.output is not None:
    finalWordcloud.to_file(args.output + ".png")
    if args.svg:
        with open(args.output + ".svg", "w") as f:
            f.write(finalWordcloud.to_svg())
            f.close()
    with open(args.output + "_report.txt", "w") as f:
        dashSep = "-" * 35
        f.write(topWordRep)
        f.write("\n")
        f.write(dashSep)
        f.write("\n")
        f.write("\n")
        f.write("Ignored words:")
        f.write("\n")
        f.write("\n".join(myStopWords))
        f.close()

if args.show_wordcloud or args.output is None:
    plt.show()  # this should prevent python from closing the plot window
