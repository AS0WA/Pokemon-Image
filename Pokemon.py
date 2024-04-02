import requests
from PIL import Image
import PySimpleGUI as sg
import os
import re
import json


def pokemon_func(pokemon_name, graphic, shiny, who):
    pokemon = pokemon_image_url(pokemon_name, graphic, shiny)
    # pokemon > return img, pokemon_data(name, ID)

    if pokemon is not None:
        pokemon_identity = f'{pokemon[1][1]} {pokemon[1][0]} {graphic}'
        pokemon_identity += " shiny" if shiny else ''
        pokemon_identity += " who" if who else ''

        pokemon[0].save(f'pokemons/{pokemon_identity}.png', "PNG")
        img = Image.open(f'pokemons/{pokemon_identity}.png')
        img = img.resize((500, 500))
        img.save(f'pokemons/{pokemon_identity}.png')

        if who:
            pokemon_who(pokemon_identity)

        return pokemon_identity


def pokemon_image_url(pokemon_name, graphic, shiny):
    try:
        pokeapi = requests.get(
            f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower() and pokemon_name.replace(' ', '-')}"
        )
        pokemon = pokeapi.json()

        if graphic == "Pixel Art" and shiny is True:
            url = pokemon["sprites"]["front_shiny"]
        elif graphic == "Art Work" and shiny is False:
            url = pokemon["sprites"]["other"]["official-artwork"]["front_default"]
        elif graphic == "Art Work" and shiny is True:
            url = pokemon["sprites"]["other"]["official-artwork"]["front_shiny"]
        elif graphic == "3D" and shiny is False:
            url = pokemon["sprites"]["other"]["home"]["front_default"]
        elif graphic == "3D" and shiny is True:
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


def pokemon_find(pokemon_name, graphic, shiny, who):
    pokemon_pattern = f'{graphic}'
    if shiny:
        pokemon_pattern += ' shiny'
    if who:
        pokemon_pattern += ' who'
    if pokemon_name.isdigit():
        pokemon_pattern = f'_-_{pokemon_name} [^ ]* {pokemon_pattern}.png'
    else:
        pokemon_pattern = f'_-_[0-9]+ {pokemon_name} {pokemon_pattern}.png'
    pokemons_list = [pokemon for pokemon in os.listdir('pokemons')]
    pokemon_identity = re.findall(pokemon_pattern, ' _-_'.join(pokemons_list))
    # pokemon1pokemon2 > pokemon1_-_pokemon2

    # if Pokémon 'who' image not exist, but Pokémon images exist make 'who' of it
    if not pokemon_identity and who:
        pokemon_pattern = f'[^ ]* {graphic}'
        if shiny:
            pokemon_pattern += ' shiny'
        if pokemon_name.isdigit():
            pokemon_pattern = f'_-_{pokemon_name} {pokemon_pattern}.png'
        else:
            pokemon_pattern = f'_-_[0-9]+ {pokemon_name} {pokemon_pattern}.png'
        pokemons_list = [pokemon for pokemon in os.listdir('pokemons')]
        pokemon_identity = re.findall(pokemon_pattern, ' _-_'.join(pokemons_list))

        if pokemon_identity:
            pokemon_who(str(pokemon_identity)[5::][:-6])
            pokemon_identity[0] = pokemon_identity[0][:-4] + ' who.png'


    if not pokemon_identity:
        # Make pokemon image, name and ID
        pokemon_data = [pokemon_func(pokemon_name, graphic, shiny, who)]
        # pokemon_func > return (name, ID), pokemon_identity

    else:
        pokemon_data = [str(pokemon_identity)[5::][:-6]]

    return pokemon_data


# Make pokemons directory
if not os.path.exists('pokemons'):
    os.makedirs('pokemons')

# Make .pokemons.json in pokemons directory
if not os.path.exists('pokemons/.pokemons.json'):
    pokemons_dict = requests.get('https://pokeapi.co/api/v2/pokemon/?limit=99999')
    pokemons_dict = pokemons_dict.json()
    pokemons_list = []
    with open('pokemons/.pokemons.json', 'x') as pokemons_json:
        for pokemon in pokemons_dict['results']:
            pokemon_id = re.findall('/[0-9]+/', pokemon['url'])
            pokemons_list.append({'name': f'{pokemon['name']}', 'id': pokemon_id[0].replace('/', '')})
        json.dump(pokemons_list, pokemons_json, indent=4)

choices = []
with open('pokemons/.pokemons.json', 'r') as pokemons_json:
    pokemons = json.load(pokemons_json)
    for pokemon_dict in pokemons:
        for pokemon in pokemon_dict.values():
            if pokemon.isdigit() is False:
                choices.append(pokemon)


# Layout
layout = [
    [sg.Text("Enter Pokemon Name or ID:"), sg.InputText(key='pokemon name', enable_events=True)],
    [sg.Push(), sg.pin(sg.Col([[sg.Listbox(values=[], size=(47, 5), enable_events=True, key='box',
                                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)]],
                   key='pokemon box', pad=(0, 0), visible=False))],
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
        sg.Button('Previous', disabled=True),
        sg.Push(), sg.Text(key='pokemon data'),
        sg.Push(), sg.Button('Next', disabled=True),
    ],
    [sg.Button("OK"), sg.Button('Save', disabled=True), sg.Push(), sg.Button("Cancel")],
    [sg.Image(key='pokemon img'), sg.Text("", key='pokemon not found')],
]


# Window
window = sg.Window("Pokemon", layout, size=(550, 750), finalize=True, return_keyboard_events=True)
window['pokemon name'].bind("<Return>", "_Enter")


# Pokemon Box
list_element: sg.Listbox = window.Element('box')
prediction_list, input_text, sel_item = [], "", 0


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Cancel":
        break

    # Pokemon Box
    elif event.startswith('Escape'):
        window['pokemon name'].update('')
        window['pokemon box'].update(visible=False)
    elif event.startswith('Down') and len(prediction_list):
        sel_item = (sel_item + 1) % len(prediction_list)
        list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
    elif event.startswith('Up') and len(prediction_list):
        sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
        list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
    elif event == '\r':
        if len(values['box']) > 0:
            window['pokemon name'].update(value=values['box'][0])
            window['pokemon box'].update(visible=False)
    elif event == 'pokemon name':
        text = values['pokemon name'].lower()
        if text == input_text:
            continue
        else:
            input_text = text
        prediction_list = []
        if text:
            prediction_list = [item for item in choices if item.lower().startswith(text)]

        list_element.update(values=prediction_list)
        sel_item = 0
        list_element.update(set_to_index=sel_item)

        if len(prediction_list) > 0:
            window['pokemon box'].update(visible=True)
        else:
            window['pokemon box'].update(visible=False)
    elif event == 'box':
        window['pokemon name'].update(value=values['box'][0])
        window['pokemon box'].update(visible=False)


# True application
    with open('pokemons/.pokemons.json', 'r') as pokemons_json:
        pokemons_dict = json.load(pokemons_json)

        try:
            if event == "OK" or (event == 'pokemon name' + "_Enter" and values['pokemon name'] == values['box'][0]):

                # Check Pokémon exists in .pokemons.json
                for pokemon_dict in pokemons_dict:
                    if values['pokemon name'] == pokemon_dict['name'] or values['pokemon name'] == pokemon_dict['id']:
                        # Check Pokémon image exists, if not create it
                        pokemon_data = [[pokemon_dict['name'], int(pokemon_dict['id'])],
                                        pokemon_find(values['pokemon name'], values['graphic'], values['shiny'], values['who'])]
                        # pokemon_data = [[name, id], [pokemon_identity]

                try:
                    pokemon_data
                except NameError:
                    pokemon_data = [False, False]

                print(pokemon_data)
                # Correct data
                if os.path.exists(f'pokemons/{pokemon_data[1][0]}.png'):
                    window['pokemon img'].update(filename=f'pokemons/{pokemon_data[1][0]}.png')
                    window['pokemon not found'].update("")
                    window['pokemon data'].update(
                        f'Name: {pokemon_data[0][0]}, ID: {pokemon_data[0][1]}'
                    )
                    window['Save'].update(disabled=False)
                    window['Previous'].update(disabled=False)
                    window['Next'].update(disabled=False)

                # Incorrect data
                else:
                    window['pokemon not found'].update('pokemon not found')
                    window['pokemon img'].update()

                # Save
                if event == 'Save' and os.path.exists(f'pokemons/{pokemon_data[1][0]}.png'):
                    desktop = os.path.join(
                        'c:\\Users', os.getlogin(), f'Desktop\\{pokemon_data[1][0]}.png'
                    )
                    file_path = sg.popup_get_file(
                        'Path', save_as=True, default_path=desktop, default_extension='.png'
                    )
                    pokemon = Image.open(f'pokemons/{pokemon_data[1][0]}.png')
                    if file_path is not None:
                        pokemon.save(file_path)

            # Previous Next
            if event in ['Previous', 'Next']:
                pokemon = {'name': pokemon_data[0][0], 'id': str(pokemon_data[0][1])}
                if event == 'Previous':
                    pokemon_id = pokemons_dict[pokemons_dict.index(pokemon) - 1]['id']
                    pokemon_name = pokemons_dict[pokemons_dict.index(pokemon) - 1]['name']
                else:
                    try:
                        pokemon_id = pokemons_dict[pokemons_dict.index(pokemon) + 1]['id']
                        pokemon_name = pokemons_dict[pokemons_dict.index(pokemon) + 1]['name']
                    except IndexError:
                        pokemon_id = 1

                # Make new pokemon_data
                # pokemon_data = pokemon_find(str(pokemon_id), values['graphic'], values['shiny'], values['who'])
                pokemon_data = [[pokemon_name, pokemon_id],
                                pokemon_find(str(pokemon_id), values['graphic'], values['shiny'], values['who'])]
                print(pokemon_data)

            # Update Pokémon img
                if os.path.exists(f'pokemons/{pokemon_data[1][0]}.png'):
                    window['pokemon img'].update(filename=f'pokemons/{pokemon_data[1][0]}.png')
                    window['pokemon not found'].update('')
                    window['pokemon data'].update(f'Name: {pokemon_data[0][0]}, ID: {pokemon_data[0][1]}')

                    # Change value "Pokémon name" with ID
                    if values['pokemon name'].isdigit():
                        window['pokemon name'].update(pokemon_data[0][1])

                    # Change value "Pokémon name" with name
                    else:
                        window['pokemon name'].update(pokemon_data[0][0])
                else:
                    window['pokemon img'].update()
                    window['pokemon not found'].update('Pokemon image not found')
                    window['pokemon data'].update(f'Name: {pokemon_data[0][0]}, ID: {pokemon_data[0][1]}')

                    # Change value "Pokémon name" with ID
                    if values['pokemon name'].isdigit():
                        window['pokemon name'].update(pokemon_data[0][1])

                    # Change value "Pokémon name" with name
                    else:
                        window['pokemon name'].update(pokemon_data[0][0])
        except TypeError:
            window['pokemon not found'].update('Pokemon not found')
            window['pokemon img'].update()

window.close()
