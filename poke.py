import os
import random
import time
import subprocess
import pickle
import sys
import xml.etree.ElementTree as ET
from getch import getch


# Function to rearrange the caught Pokémon names according to the Pokedex order
def load_dex_numbers():
    dex_numbers = {}
    tree = ET.parse('pokedex.xml')
    root = tree.getroot()
    for pokemon in root.iter('pokemon'):
        species = pokemon.find('species').text.upper()
        dex = int(pokemon.find('dex').text)
        dex_numbers[species] = dex
    return dex_numbers


def rearrange_caught_pokemon():
    caught_pokemon = load_caught_pokemon()
    rearranged_pokemon = sorted(caught_pokemon, key=lambda x: dex_numbers.get(x.upper(), float('inf')))
    save_caught_pokemon(rearranged_pokemon)


# Define the dex_numbers dictionary as a global variable
dex_numbers = load_dex_numbers()


# Define the areas and their corresponding numbers
areas = {
    1: "Town",
    2: "Jungle",
    3: "Forest",
    4: "Volcano",
    5: "Beach",
    6: "Pond",
    7: "Ice cave",
    8: "Rocky cave",
    9: "Grassy field",
    10: "Abandoned mansion",
    11: "Powerplant"
}

# Variable to store the last visited area
last_area = ""


# Clear the terminal screen
def clear_screen():
    subprocess.call('clear', shell=True)


# Display the area selection and prompt the player for input
def display_area_selection(caught_pokemon):
    clear_screen()
    print("Where would you like to go?")
    for number, area in areas.items():
        print(f"{number}. {area}")
    print()

    while True:
        choice = input("Enter the area number (or 'exit' to quit): ").lower()

        if choice in ["exit", "quit"]:
            save_caught_pokemon(caught_pokemon)
            clear_screen()
            sys.exit()

        try:
            choice_int = int(choice)
            if choice_int in areas:
                return choice_int
            else:
                print("Invalid area number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid area number or 'exit' to quit.")


# Display the available options after entering an area
def display_options(area_name, show_options=True):
    clear_screen()
    print(f"You are in the {area_name}")
    if show_options:
        print(f"\nOptions for {area_name}:")
        print("1. Search")
        print("2. Go to another area")
        print("3. Pokédex")
        print("4. Clear data")
        print()
    choice = input("What would you like to do? ")
    return choice


# Get a random Pokemon from the specified area directory
def get_random_pokemon(area_name):
    directory = f"areas/{area_name.lower()}"
    common_dir = os.path.join(directory, "common")
    uncommon_dir = os.path.join(directory, "uncommon")
    rare_dir = os.path.join(directory, "rare")
    very_rare_dir = os.path.join(directory, "very_rare")
    rarest_dir = os.path.join(directory, "rarest")

    choice = random.choices(
        [common_dir, uncommon_dir, rare_dir, very_rare_dir, rarest_dir],
        weights=[0.5, 0.3, 0.15, 0.04, 0.01]
    )[0]

    wordlist = None
    if choice == common_dir:
        wordlist = "4-letter-words.txt"
    elif choice == uncommon_dir:
        wordlist = "5-letter-words.txt"
    elif choice == rare_dir:
        wordlist = "6-letter-words.txt"
    else:
        wordlist = "7-letter-words.txt"

    pokemon_files = os.listdir(choice)
    if pokemon_files:
        random_pokemon_file = random.choice(pokemon_files)
        with open(os.path.join(choice, random_pokemon_file)) as file:
            pokemon_name = os.path.splitext(random_pokemon_file)[0]
            return file.read(), pokemon_name.upper(), wordlist
    else:
        return "No Pokemon found in this area.", "", ""


# Get a random word from the specified word list
def get_random_word(wordlist):
    with open(wordlist) as file:
        word_list = file.read().splitlines()
        return random.choice(word_list)


# Slowly type out a message over the specified duration
def slow_type(message, duration):
    for char in message:
        print(char, end="", flush=True)
        time.sleep(duration / len(message))


# Save the caught Pokemon names to a file
def save_caught_pokemon(caught_pokemon):
    unique_pokemon = list(set(caught_pokemon))  # Remove duplicates
    with open("caught_pokemon.txt", "w") as file:
        for pokemon_name in unique_pokemon:
            dex_number = dex_numbers.get(pokemon_name.upper())
            if dex_number:
                file.write(f"#{dex_number:03d} {pokemon_name}\n")


# Load the caught Pokemon names from a file
def load_caught_pokemon():
    caught_pokemon = []
    if os.path.exists("caught_pokemon.txt"):
        with open("caught_pokemon.txt", "r") as file:
            for line in file:
                if line.strip():
                    pokemon_name = line.strip().split(" ", 1)[1]
                    caught_pokemon.append(pokemon_name)
    return caught_pokemon


# Load the Pokedex data from the XML file
def load_pokedex():
    pokedex = {}
    tree = ET.parse("pokedex.xml")
    root = tree.getroot()
    for pokemon in root.findall("pokemon"):
        species = pokemon.find("species").text.upper()
        dex = int(pokemon.find("dex").text)
        pokedex[dex] = species
    return pokedex


# Display the Pokedex with caught Pokemon
def display_pokedex(caught_pokemon):
    clear_screen()
    print("Pokedéx\n")

    if len(caught_pokemon) >= 151:
        print("You have completed the Pokédex and won the game. Congratulations!")
        print()

    if not caught_pokemon:
        print("You have not yet caught any Pokémon")
        return

    sorted_pokemon = sorted(caught_pokemon, key=lambda p: dex_numbers.get(p.upper(), float('inf')))
    num_columns = 6

    for index, pokemon_name in enumerate(sorted_pokemon, start=1):
        dex_number = dex_numbers.get(pokemon_name.upper())
        if dex_number:
            print(f"#{dex_number:03d} {pokemon_name.upper():<15}", end="")
            if index % num_columns == 0:
                print()

    if index % num_columns != 0:
        print()


# Delete the save file
def delete_save_file():
    if os.path.exists("caught_pokemon.txt"):
        os.remove("caught_pokemon.txt")
        print("Save data has been deleted.")
    else:
        print("No save data found.")


# Game loop
def game_loop():
    caught_pokemon = load_caught_pokemon()
    pokedex = load_pokedex()

    while True:
        area_choice = display_area_selection(caught_pokemon)
        if area_choice in ["exit", "quit"]:
            save_caught_pokemon(caught_pokemon)
            clear_screen()
            sys.exit()

        area_name = areas.get(int(area_choice), "")
        if area_name:
            while True:
                option_choice = display_options(area_name)
                if option_choice in ["exit", "quit"]:
                    save_caught_pokemon(caught_pokemon)
                    clear_screen()
                    sys.exit()

                if option_choice == "1":
                    clear_screen()
                    pokemon, pokemon_name, wordlist = get_random_pokemon(area_name)
                    clear_screen()
                    print(f"A wild {pokemon_name} appeared!")
                    print()
                    print(pokemon)
                    print("\n1. Catch")
                    print("2. Run away")
                    catch_choice = input("What would you like to do? ")

                    if catch_choice.lower() in ["exit", "quit"]:
                        save_caught_pokemon(caught_pokemon)
                        clear_screen()
                        sys.exit()

                    if catch_choice == "1":
                        clear_screen()
                        print(f"A wild {pokemon_name} appeared!")
                        print()
                        print(pokemon)
                        print("\n1. Catch")
                        print("2. Run away")
                        slow_type("Ready. Set. Go!\n", 0.2)
                        time.sleep(1)
                        random_word = get_random_word(wordlist)
                        slow_type(random_word + "\n", 0.2)
                        start_time = time.time()
                        player_input = input("\nEnter the word: ")
                        end_time = time.time()

                        if (
                            player_input.lower() == random_word.lower()
                            and end_time - start_time <= 1.5
                        ):
                            if pokemon_name not in caught_pokemon:
                                caught_pokemon.append(pokemon_name)
                                save_caught_pokemon(caught_pokemon)
                                rearrange_caught_pokemon()
                                clear_screen()
                                print(f"\n#{dex_numbers[pokemon_name.upper()]:03d} {pokemon_name.upper()} has been added to your Pokédex!")
                                time.sleep(1.5)

                            else:
                                clear_screen()
                                print(f"\n#{dex_numbers[pokemon_name.upper()]:03d} {pokemon_name.upper()} has already been registered to your Pokédex!")
                                time.sleep(1.5)
                        else:
                            clear_screen()
                            print(f"\n{pokemon_name.upper()} ran away!")
                            time.sleep(0.5)

                    else:
                        clear_screen()
                        print("\nYou ran away.")
                        time.sleep(0.5)

                elif option_choice == "2":
                    clear_screen()
                    break

                elif option_choice == "3":
                    display_pokedex(caught_pokemon)
                    getch()  # Wait for user input
                    clear_screen()

                elif option_choice == "4":
                    clear_screen()
                    confirm = input("Are you sure you want to clear the save data? (yes/no) ")
                    if confirm.lower() == "yes":
                        delete_save_file()
                        caught_pokemon = []
                        clear_screen()
                        print("Save data cleared.")
                        time.sleep(1.5)
                    else:
                        clear_screen()
                        print("Save data not cleared.")
                        time.sleep(1.5)

        else:
            clear_screen()
            print("Invalid choice. Please try again.")
            time.sleep(0.5)


# Start the game
game_loop()
