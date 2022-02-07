# Wordle Helper

import numpy as np
from nltk.corpus import words

WORD_LEN = 5
NUM_GUESSES = 6
alphabet = "abcdefghijklmnopqrstuvwxyz"

class Object(object):
    pass

# information: {possibles: ('a-z', 'a-z', 'a-z', 'a-z', 'a-z'), misplaced: ""}
def passes_criteria(word, information):
    copy = word
    for i in range(WORD_LEN):
        if copy[i] not in information.possibles[i]:
            return False
    for misplaced_letter in information.misplaced:
        if misplaced_letter not in copy:
            return False
        copy.replace(misplaced_letter, '')
    return True


# indicators: array of 5, 0 = absent, 1 = incorrectly placed, 2 = correctly placed
def update_information(information, word, indicators):
    for i in range(WORD_LEN):
        letter = word[i]
        if (indicators[i] == 0):
            information.possibles = list(map(lambda possible : possible.replace(letter, ""), information.possibles))
        elif (indicators[i] == 1):
            information.misplaced += letter
            information.possibles[i] = information.possibles[i].replace(letter, "")
        else:
            information.misplaced = information.misplaced.replace(letter, "")
            information.possibles[i] = letter
    

def get_trimmed_dict(information, dictionary):
    return list(filter(lambda word : passes_criteria(word, information), dictionary))

    
def get_ranked_options(information, dictionary, frequencies):
    print_info(information)
    option_map = np.repeat(None, len(dictionary))
    for i in range(len(dictionary)):
        score = 0
        for letter in ''.join(set(dictionary[i])):
            score += frequencies[ord(letter) - 97]
        option_map[i] = Object()
        option_map[i].word = dictionary[i]
        option_map[i].score = score / WORD_LEN
    option_map = sorted(option_map, key=lambda option : -option.score)
    for i in range(len(option_map)):
        print(f"{option_map[i].word}={option_map[i].score}")
        if i == 10: break
    return option_map
    

def is_solved(information):
    if len(information.misplaced) > 0:
        return False
    for i in range(WORD_LEN):
        if len(information.possibles[i]) != 1:
            return False
    return True


def print_info(information):
    for x in range(WORD_LEN):
        print(f"Letter {x}: ")
        print(f"\tAvailable letters: {information.possibles[x]}")
    print(f"Misplaced letters: '{information.misplaced}'")
    
    
def print_guesses(guesses):
    for i in range(len(guesses)):
        print(f"\t{i+1}: {guesses[i]}")
        
        
def print_indicator_instructions(guess):
    print(f"How did {guess} do? For each letter, enter:")
    print("\t0 if it's NOT in the word")
    print("\t1 if it's in the word but in the wrong place")
    print("\t2 if it's in its proper place")


def main():
    dictionary = list(filter(lambda x : len(x) == WORD_LEN and x == x.lower(), words.words()))

    information = Object()
    information.possibles = np.repeat(alphabet, 5)
    information.misplaced = ""

    frequencies = np.repeat(0, 26)
    weighted_string = "aaaeeeiiiooouuuqwrrttyppssddfghjkllzxccvbnnm"
    for letter in weighted_string:
        pos = ord(letter) - 97
        frequencies[pos] += 1
        
    guesses = list()
    
    for x in range(NUM_GUESSES):
        if (is_solved(information)):
            print(f"Congrats! You got it in {x}.")
            print_guesses(guesses)
            break
        else:
            print("Suggestions for guess:")
            if x > 0:
                dictionary = get_trimmed_dict(information, dictionary)
            get_ranked_options(information, dictionary, frequencies)
            
        guess = input(f"Enter guess #{x + 1}: ")
        print_indicator_instructions(guess)
        indicators = input(f"'{guess}': ")
        
        update_information(information, guess, list(map(int, list(indicators))))
        guesses.append(guess)
   
main()