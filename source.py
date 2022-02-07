# Wordle Helper

import numpy as np
import random
from nltk.corpus import words

WORD_LEN = 5
NUM_GUESSES = 6
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
WEIGHTED_STRING = "aaaaeeeeiiiioooouuuuqwrrrtttyppsssddfghjkllzxccvbnnmm"
DICT = words.words()
STARTER_ANALYSIS_TRIAL_COUNT = 500

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


def get_dictionary():
    return list(filter(lambda x : len(x) == WORD_LEN and x == x.lower(), DICT))
    

def get_frequencies():
    frequencies = np.repeat(0, 26)
    for letter in WEIGHTED_STRING:
        pos = ord(letter) - 97
        frequencies[pos] += 1
    return frequencies


def get_indicators(guess, answer):
    res = [0 for i in range(WORD_LEN)]
    for i in range(WORD_LEN):
        letter = guess[i]
        if letter in answer and letter == answer[i]:
            res[i] = 2
        elif letter in answer:
            res[i] = 1
    return res


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
        print(f"\t{ranked_options[i].word} = {ranked_options[i].score}")
        if i == n: break
    
def print_starters(sorted_starters, n):
    for i in range(len(sorted_starters)):
        print(f"\t{i + 1}. {sorted_starters[i].starter} = {sorted_starters[i].efficiency}")
        if i == n - 1 : break
    

def get_path(answer, starter = None):
    information = get_new_information()
    dictionary = get_dictionary()
    frequencies = get_frequencies()
    
    if not valid_input(answer, ALPHABET) or answer not in dictionary:
        return None
        
    path = list()        
    while len(path) == 0 or path[-1] != answer:
        selection = starter if starter is not None and len(path) == 0 else get_ranked_options(information, dictionary, frequencies)[0].word
        path.append(selection)
        indicators = get_indicators(selection, answer)
        update_information(information, selection, indicators)
        dictionary = get_trimmed_dict(information, dictionary)
        
    return path


def test_algo_efficiency(num_trials, print_data = True, starter = None):
    dictionary = get_dictionary()
    total = 0
    for i in range(num_trials):
        answer = random.choice(dictionary)
        length = len(get_path(answer, starter))
        if print_data:
            print(f"'{answer}': {length}")
        total += length
    return total / num_trials


def get_sorted_starters(n, total_trials, print_data = True):
    information = get_new_information()
    dictionary = get_dictionary()
    frequencies = get_frequencies()
    
    res = np.repeat(None, n)
    ranked_options = get_ranked_options(information, dictionary, frequencies)
    for i in range(n):
        word = ranked_options[i].word
        res[i] = Object()
        res[i].starter = word
        res[i].efficiency = test_algo_efficiency(int(total_trials / n), False, word)
        if print_data:
            print(f"\t{res[i].starter} = {res[i].efficiency}")
        
    return sorted(res, key = lambda option : option.efficiency)


def run_starter_analysis():
    n = input("How many starters would you like to sample? ")
    while not n.isnumeric():
        n = input(f"'{n}' is not a number. How many starters would you like to sample? ")
    while int(n) < 1 or int(n) > STARTER_ANALYSIS_TRIAL_COUNT:
        n = input(f"'{n}' out of range [1, {STARTER_ANALYSIS_TRIAL_COUNT}]. How many starters would you like to sample? ")
    c = input("How many trials would you like to conduct in total? (hit Enter for default, N = 500): ")
    while len(c) > 0 and not c.isnumeric():
        c = input(f"'{c}' is not a number. How many trials would you like to conduct? (hit Enter for default): ")
    while len(c) > 0 and int(c) < int(n):
        c = input(f"'{c}' must be at least equal to the number of starters ({n}): ")
        
    total_trials = int(c) if c.isnumeric() else STARTER_ANALYSIS_TRIAL_COUNT
    print(f"\nEach starter is being fed a set of {round(total_trials / int(n))} trials:\n")
    sorted_starters = get_sorted_starters(int(n), total_trials)
    print("\nStrongest starters:\n")
    print_starters(sorted_starters, min(int(n), 5))
    

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
    efficiency = test_algo_efficiency(int(n))
    print(f"Algorithm average number of tries: {efficiency}")


def run_helper():
    information = get_new_information()
    dictionary = get_dictionary()
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
        choice = input("Would you like to:\n\tuse the Wordle Helper [0],\n\ttest a word on our algorithm [1], \n\tcheck the average efficiency of the algorithm [2],\n\tor analyze the strongest starting words? [3] \n\t(e to exit) ")
        while choice not in "0123e":
            choice = input(f"'{choice}' is invalid input. Be sure to enter a number 0-3: ")
        
        if choice == "0":
            run_helper()
        elif choice == "1":
            run_algo_checker()
        elif choice == "2":
            run_algo_efficiency_test()
        elif choice == "3":
            run_starter_analysis()
        elif choice == "e":
            break
    
    
   
main()