# Wordle Helper


# Online Python - IDE, Editor, Compiler, Interpreter
import numpy as np
import nltk
# from nltk.corpus import words

'''
@params data: an object that accounts for all information already given
info: array of length 5, each element an list of all the possible letters
get_options takes in data and returns,
from within the list of 5-letter words in the dictionary,
all the words that fit the informations
'''

# information: {possibles: ('a-z', 'a-z', 'a-z', 'a-z', 'a-z'), misplaced: ""}
class Object(object):
    pass

information = Object()
information.possibles = np.repeat("abcdefghijklmnopqrstuvwxyz", 5)
information.misplaced = ""
WORD_LEN = 5
NUM_GUESSES = 6

with open('./short_dict.txt') as short_dict:
    book = short_dict.split('\n')
  
book = ["yummy", "funny"]
    
# indicators: array of 5, 0 = absent, 1 = incorrectly placed, 2 = correctly placed
def incorporate_information(word, indicators):
    for i in range(len(indicators)):
        letter = word[i]
        if (indicators[i] == 0):
            information.possibles = list(map(lambda possible : possible.replace(letter, ""), information.possibles))
        elif (indicators[i] == 1):
            information.misplaced += letter
            information.possibles[i] = information.possibles[i].replace(letter, "")
        else:
            information.misplaced = information.misplaced.replace(letter, "")
            information.possibles[i] = letter

def get_options():
    options = []
    dictionary = book
    dict = list(filter(lambda x : len(x) == WORD_LEN, dictionary))
    for word in dict:
        if passes_criteria(word):
            options.append(word)
    return options

frequencies = np.repeat(0, 26)
for word in book:
    for letter in word.lower():
        pos = ord(letter) - 97
        if pos >= 0 and pos < 26: 
            frequencies[pos] += 1
    
def get_ranked_options():
    options = get_options()
    option_map = np.repeat(None, len(options))
    for i in range(len(options)):
        score = 0
        for letter in ''.join(set(options[i])):
            score += frequencies[ord(letter) - 97]
        option_map[i] = Object()
        option_map[i].word = options[i]
        option_map[i].score = score / WORD_LEN
    option_map = sorted(option_map, key=lambda option : -option.score)
    for option in option_map:
        print(f"{option.word}={option.score}")
    return option_map
    
def passes_criteria(word):
    for i in range(WORD_LEN):
        if word[i] not in information.possibles[i]:
            return False
    misplaced = information.misplaced
    for misplaced_letter in misplaced:
        if misplaced_letter not in word:
            return False
        word.replace(misplaced_letter, '')
    return True
    
def is_solved():
    if len(information.misplaced) > 0:
        return False
    for i in range(5):
        if len(information.possibles[i]) != 1:
            return False
    return True
    
guesses = np.repeat("", NUM_GUESSES)
for x in range(NUM_GUESSES):
    guess = input(f"Enter guess #{x + 1}: ")
    print(f"How did {guess} do? For each letter, enter:")
    print("\t0 if it's NOT in the word")
    print("\t1 if it's in the word but in the wrong place")
    print("\t2 if it's in its proper place")
    indicators = input(f"'{guess}': ")
    incorporate_information(guess, list(map(int, list(indicators))))
    guesses[x] = guess
    if (is_solved()):
        print("Congrats! You got it.")
        break
    else:
        print("Options for next guess:")
        get_ranked_options()