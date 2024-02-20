import requests
from PIL import Image
import PySimpleGUI as sg
import os
import re


def pokemon_func(pokemon_name):
    pokemon = pokemon_image_url(pokemon_name)
    # pokemon > return img, pokemon_data(name, ID)

    if pokemon is not None:
        pokemon_identity = f'{pokemon[1][1]} {pokemon[1][0]} {values["graphic"]}'
        pokemon_identity += " shiny" if values["shiny"] else ''
        pokemon_identity += " who" if values["who"] else ''

        pokemon[0].save(f'pokemons/{pokemon_identity}.png', "PNG")
        img = Image.open(f'pokemons/{pokemon_identity}.png')
        img = img.resize((500, 500))
        img.save(f'pokemons/{pokemon_identity}.png')

        if values["who"]:
            pokemon_who(pokemon_identity)

        return pokemon[1], pokemon_identity


def pokemon_image_url(pokemon_name):
    try:
        pokeapi = requests.get(
            f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower() and pokemon_name.replace(' ', '-')}"
        )
        pokemon = pokeapi.json()

        if values["graphic"] == "Pixel Art" and values["shiny"] is True:
            url = pokemon["sprites"]["front_shiny"]
        elif values["graphic"] == "Art Work" and values["shiny"] is False:
            url = pokemon["sprites"]["other"]["official-artwork"]["front_default"]
        elif values["graphic"] == "Art Work" and values["shiny"] is True:
            url = pokemon["sprites"]["other"]["official-artwork"]["front_shiny"]
        elif values["graphic"] == "3D" and values["shiny"] is False:
            url = pokemon["sprites"]["other"]["home"]["front_default"]
        elif values["graphic"] == "3D" and values["shiny"] is True:
            url = pokemon["sprites"]["other"]["home"]["front_shiny"]
        else:
            url = pokemon["sprites"]["front_default"]

        img = Image.open(requests.get(url, stream=True).raw)
        pokemon_data = pokemon["forms"][0]["name"], pokemon["id"]

        return img, pokemon_data
    except:
        return None


def pokemon_who(pokemon_identity):
    black_and_white = []
    transparent = []
    img = Image.open(f'pokemons/{pokemon_identity}.png').convert("RGBA")
    data = img.getdata()
    for item in data:
        if item[0] > 0 and item[1] > 0 and item[2] > 0:
            black_and_white.append((0, 0, 0, 255))
        else:
            black_and_white.append((255, 255, 255, 255))
    for item in black_and_white:
        if item[:3] == (255, 255, 255):
            transparent.append((255, 255, 255, 0))
        else:
            transparent.append(item)
    img.putdata(transparent)
    if 'who' in pokemon_identity:
        img.save(f'pokemons/{pokemon_identity}.png', "PNG")
    else:
        img.save(f'pokemons/{pokemon_identity} who.png', "PNG")


def pokemon_find(pokemon_name):
    pokemon_pattern = f'[^ ]* {values["graphic"]}'
    if values["shiny"]:
        pokemon_pattern += ' shiny'
    if values["who"]:
        pokemon_pattern += ' who'
    if pokemon_name.isdigit():
        pokemon_pattern = f'_-_{pokemon_name} {pokemon_pattern}.png'
    else:
        pokemon_pattern = f' {pokemon_name} {pokemon_pattern}.png'
    pokemons_list = [pokemon for pokemon in os.listdir('pokemons')]
    pokemon_identity = re.findall(pokemon_pattern, ' _-_'.join(pokemons_list))

    # if Pokémon 'who' image not exist, but Pokémon images exist make 'who' of it
    if not pokemon_identity:
        if values['who']:
            pokemon_pattern = f'[^ ]* {values["graphic"]}'
            if values["shiny"]:
                pokemon_pattern += ' shiny'
            if pokemon_name.isdigit():
                pokemon_pattern = f'_-_{pokemon_name} {pokemon_pattern}.png'
            else:
                pokemon_pattern = f' {pokemon_name} {pokemon_pattern}.png'
            pokemons_list = [pokemon for pokemon in os.listdir('pokemons')]
            pokemon_identity = re.findall(pokemon_pattern, ' _-_'.join(pokemons_list))

            if pokemon_identity:
                pokemon_who(str(pokemon_identity)[5::][:-6])
                pokemon_identity[0] = pokemon_identity[0][:-4] + ' who.png'


    if not pokemon_identity:
        # Make pokemon image, name and ID
        pokemon_data = pokemon_func(pokemon_name)
        # pokemon_func > return (name, ID), pokemon_identity

    else:
        pokemon_data = []
        pokemon_identity = str(pokemon_identity)[5::][:-6]
        pokemon_name = re.findall('^[0-9]* [^ ]*', str(pokemon_identity))[0]
        pokemon_id = int(''.join(filter(lambda x: x.isdigit(), str(pokemon_name))))
        pokemon_data.extend([[pokemon_name[len(str(pokemon_id)):], pokemon_id], pokemon_identity])
    return pokemon_data


layout = [
    [sg.Text("Enter Pokemon Name or ID:"), sg.InputText(key="pokemon name")],
    [
        sg.Text("Graphics type:"),
        sg.Combo(
            ["Pixel Art", "Art Work", "3D"], key="graphic", default_value="Pixel Art"
        ),
        sg.Text("Shiny:"),
        sg.Checkbox("", key="shiny"),
    ],
    [sg.Text("Who's that Pokemon:"), sg.Checkbox("work in progress", key="who")],
    [
        sg.Button("Previous", disabled=True),
        sg.Text(key="pokemon data"),
        sg.Button("Next", disabled=True),
    ],
    [sg.Button("OK"), sg.Button("Save", disabled=True), sg.Button("Cancel")],
    [sg.Image(key="pokemon img"), sg.Text("", key="pokemon not found")],
]

window = sg.Window("Pokemon", layout, size=(550, 650), finalize=True)
window["pokemon name"].bind("<Return>", "_Enter")

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Cancel":
        break

    # Make pokemon image
    if event == "OK" or event == "pokemon name" + "_Enter":
        if not os.path.exists('pokemons'):
            os.makedirs('pokemons')

        # Check Pokémon image exists, if not create it
        pokemon_data = pokemon_find(values['pokemon name'])

        # Correct data
        if os.path.exists(f'pokemons/{pokemon_data[1]}.png'):
            window["pokemon img"].update(filename=f'pokemons/{pokemon_data[1]}.png')
            window["pokemon not found"].update("")
            window["pokemon data"].update(
                f"Name: {pokemon_data[0][0]}, ID: {pokemon_data[0][1]}"
            )
            window["Save"].update(disabled=False)
            window["Previous"].update(disabled=False)
            window["Next"].update(disabled=False)

        # Incorrect data
        else:
            window["pokemon not found"].update("Pokemon not found")
            window["pokemon img"].update()

    # Save
    if event == "Save" and os.path.exists(f'pokemons/{pokemon_data[1]}.png'):
        desktop = os.path.join(
            "c:\\Users", os.getlogin(), f"Desktop\\{pokemon_data[1]}.png"
        )
        file_path = sg.popup_get_file(
            "Path", save_as=True, default_path=desktop, default_extension=".png"
        )
        pokemon = Image.open(f'pokemons/{pokemon_data[1]}.png')
        if file_path is not None:
            pokemon.save(file_path)

    # Previous Next
    if event in ["Previous", "Next"] and os.path.exists(f'pokemons/{pokemon_data[1]}.png'):
        pokemon_id = pokemon_data[0][1] + (-1 if event == "Previous" else 1)

        # If it is the first Pokémon, jump to the last Pokémon using the previous button
        if pokemon_id == 0:
            pokemon_id = 1025
        # If it is the last Pokémon, jump to the first Pokémon using the previous button
        elif pokemon_id == 1026:
            pokemon_id = 1

        # Make new pokemon_data
        pokemon_data = pokemon_find(str(pokemon_id))

        # Make new Pokémon.png
        if os.path.exists(f'pokemons/{pokemon_data[1]}.png'):
            window["pokemon img"].update(filename=f'pokemons/{pokemon_data[1]}.png')
            window["pokemon not found"].update("")
            window["pokemon data"].update(f"Name: {pokemon_data[0][0]}, ID: {pokemon_data[0][1]}")

            # Change value "Pokémon name" with ID
            if values["pokemon name"].isdigit():
                window["pokemon name"].update(pokemon_data[0][1])

            # Change value "Pokémon name" with name
            else:
                window["pokemon name"].update(pokemon_data[0][0])

window.close()
