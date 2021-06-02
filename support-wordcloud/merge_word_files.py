words = []
fileObj = open("ignore_words.txt", "r")  # opens the file in read mode
words += fileObj.read().splitlines()  # puts the file into an array
fileObj.close()
fileObj = open("common_ignore.txt", "r")  # opens the file in read mode
words += fileObj.read().splitlines()  # puts the file into an array
fileObj.close()

words = set(words)
words = list(words)
words = sorted(words, key=str.lower)

words = "\n".join(words)
fileObj = open("my_full_ignore.txt", "w")  # opens the file in read mode
fileObj.write(words)  # puts the file into an array
fileObj.close()
