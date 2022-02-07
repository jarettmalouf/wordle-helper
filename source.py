# Wordle Helper

import numpy as np
import random
from nltk.corpus import words

WORD_LEN = 5
NUM_GUESSES = 6
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
WEIGHTED_STRING = "aaaaeeeeiiiioooouuuuqwrrrtttyppsssddfghjkllzxccvbnnmm"

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
    # print_info(information)
    option_map = np.repeat(None, len(dictionary))
    for i in range(len(dictionary)):
        score = 0
        for letter in ''.join(set(dictionary[i])):
            score += frequencies[ord(letter) - 97]
        option_map[i] = Object()
        option_map[i].word = dictionary[i]
        option_map[i].score = score / WORD_LEN
    return sorted(option_map, key=lambda option : -option.score)
    

def is_solved(information):
    if len(information.misplaced) > 0:
        return False
    for i in range(WORD_LEN):
        if len(information.possibles[i]) != 1:
            return False
    return True


def valid_input(user_input, criteria):
    if len(user_input) != WORD_LEN:
        return False
    for char in user_input:
        if char not in criteria:
            return False
    return True 


def get_new_information():
    information = Object()
    information.possibles = np.repeat(ALPHABET, WORD_LEN)
    information.misplaced = ""
    return information


def get_frequencies():
    frequencies = np.repeat(0, 26)
    for letter in WEIGHTED_STRING:
        pos = ord(letter) - 97
        frequencies[pos] += 1
    return frequencies


def print_info(information):
    for x in range(WORD_LEN):
        print(f"Letter {x}: ")
        print(f"\tAvailable letters: {information.possibles[x]}")
    print(f"Misplaced letters: '{information.misplaced}'")
    
    
def print_path(guesses):
    for i in range(len(guesses)):
        print(f"\t{i+1}: {guesses[i]}")
        
        
def print_indicator_instructions(guess):
    print(f"How did {guess} do? For each letter, enter:")
    print("\t0 if it's NOT in the word")
    print("\t1 if it's in the word but in the wrong place")
    print("\t2 if it's in its proper place")
    
    
def print_ranked_options(ranked_options, n):
    for i in range(len(ranked_options)):
        print(f"\t{ranked_options[i].word}={ranked_options[i].score}")
        if i == n: break
    
    
def get_indicators(guess, answer):
    res = [0 for i in range(WORD_LEN)]
    for i in range(WORD_LEN):
        letter = guess[i]
        if letter in answer and letter == answer[i]:
            res[i] = 2
        elif letter in answer:
            res[i] = 1
    return res
    

def get_path(answer):
    information = get_new_information()
    dictionary = list(filter(lambda x : len(x) == WORD_LEN and x == x.lower(), words.words()))
    frequencies = get_frequencies()
    
    if not valid_input(answer, ALPHABET) or answer not in dictionary:
        return None
    
    
    path = list()
    while len(path) == 0 or path[-1] != answer:
        selection = get_ranked_options(information, dictionary, frequencies)[0].word
        path.append(selection)
        indicators = get_indicators(selection, answer)
        update_information(information, selection, indicators)
        dictionary = get_trimmed_dict(information, dictionary)
    return path

def test_algo_efficiency(n, print_examples = False):
    dictionary = list(filter(lambda x : len(x) == WORD_LEN and x == x.lower(), words.words()))
    total = 0
    for i in range(n):
        answer = random.choice(dictionary)
        length = len(get_path(answer))
        if print_examples:
            print(f"'{answer}': {length}")
        total += length
    return total / n


def run_algo_checker():
    answer = input("Enter Wordle: ")
    path = get_path(answer)
    if path is None:
        print(f"'{answer}' is either not in the dictionary or impossible given the constraints.")
    else:
        print(f"\nThe algorithm got '{answer}' in {len(path)}:")
        print_path(path)
        
def run_algo_efficiency_test():
    n = input("How many random words would you like to sample? ")
    while not n.isnumeric():
        n = input(f"'{n}' is not a number. How many random words would you like to sample? ")
    efficiency = test_algo_efficiency(int(n), True)
    print(f"Algorithm average number of tries: {efficiency}")


def run_helper():
    information = get_new_information()
    dictionary = list(filter(lambda x : len(x) == WORD_LEN and x == x.lower(), words.words()))
    frequencies = get_frequencies()
    guess = ""
    guesses = list()
    solved = False
    for x in range(NUM_GUESSES):
        if (is_solved(information)):
            solved = True
            print(f"Congrats! You got it in {x}.")
            print_path(guesses)
            break
        else:
            print("Suggestions:")
            if x > 0:
                dictionary = get_trimmed_dict(information, dictionary)
            ranked_options = get_ranked_options(information, dictionary, frequencies)
            print_ranked_options(ranked_options, 10)
            
        guess = input(f"Enter guess #{x + 1}: ")
        while not valid_input(guess, ALPHABET) or guess not in dictionary:
            print(f"'{guess}' is either not in the dictionary or impossible given the constraints.")
            guess = input(f"Enter guess #{x + 1}: ")
            
        print_indicator_instructions(guess)
        indicators = input(f"'{guess}': ")
        while not valid_input(indicators, "012"):
            print(f"'{indicators}' is invalid input. Be sure to type 5 indicators, 0-2.")
            indicators = input(f"'{guess}': ")
        
        update_information(information, guess, list(map(int, list(indicators))))
        guesses.append(guess)
    if not solved:
        print("You've used up all {NUM_GUESSES} of your guesses!")
        print_path(guesses)
        

def main():
    exited = False
    while not exited:
        print("\nLet's play Wordle!\n")
        choice = input("Would you like to use the Wordle Helper [0], test a word on our algorithm [1], or check the average efficiency of the algorithm [2]? (e to exit) ")
        while choice not in "012e":
            choice = input(f"'{choice}' is invalid input. Be sure to enter a number 0-2: ")
        
        if choice == "0":
            run_helper()
        elif choice == "1":
            run_algo_checker()
        elif choice == "2":
            run_algo_efficiency_test()
        elif choice == "e":
            break
    
    
   
main()