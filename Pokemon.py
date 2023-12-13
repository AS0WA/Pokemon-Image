import requests
from PIL import Image
import PySimpleGUI as sg
import os


def pokemon_func(pokemon_name, graphic, shiny, who):
    img = pokemon_image_url(pokemon_name, graphic, shiny)
    if img is not None:
        if who is True:
            img = pokemon_who(img)
        else:
            img.save('pokemon.png', 'PNG')

        img = Image.open('pokemon.png')
        resized_img = img.resize((500, 500))
        resized_img.save('pokemon.png')
    else:
        ditto()


def pokemon_image_url(pokemon_name, graphic, shiny):
    try:
        pokeapi = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower() and pokemon_name.replace(' ', '-')}")
        pokemon = pokeapi.json()

        if graphic == 'Default' and shiny is True:
            url = pokemon['sprites']['front_shiny']
        elif graphic == 'Artwork' and shiny is False:
            url = pokemon['sprites'].get('other', pokemon['sprites']).get('official-artwork')['front_default']
        elif graphic == 'Artwork' and shiny is True:
            url = pokemon['sprites'].get('other', pokemon['sprites']).get('official-artwork')['front_shiny']
        elif graphic == 'Home' and shiny is False:
            url = pokemon['sprites'].get('other', pokemon['sprites']).get('home')['front_default']
        elif graphic == 'Home' and shiny is True:
            url = pokemon['sprites'].get('other', pokemon['sprites']).get('home')['front_shiny']
        else:
            url = pokemon['sprites']['front_default']

        img = Image.open(requests.get(url, stream=True).raw)

        return img
    except:
        return None


def pokemon_who(img):
    new_data = []
    img = img.convert("RGBA")
    data = img.getdata()
    for item in data:
        if item[0] > 0 and item[1] > 0 and item[2] > 0:
            new_data.append((0, 0, 0, 255))
        else:
            new_data.append((255, 255, 255, 255))
    img.putdata(new_data)
    img.save('pokemon.png', 'PNG')

    return img


def ditto():
    ditto_api = requests.get("https://pokeapi.co/api/v2/pokemon/ditto")
    ditto = ditto_api.json()
    ditto_url = ditto['sprites'].get('other', ditto['sprites']).get('official-artwork')['front_default']
    ditto_img = Image.open(requests.get(ditto_url, stream=True).raw)
    ditto_img = ditto_img.convert("RGBA")
    ditto_img.save('ditto.png', 'PNG')
    ditto_img = Image.open('ditto.png')
    resized_img = ditto_img.resize((500, 500))
    resized_img.save('ditto.png')


layout = [[sg.Text('Enter Pokemon Name:'), sg.InputText(key="pokemon_name")],
          [sg.Text('Graphics type:'), sg.Combo(['Default', 'Artwork', 'Home'], key='graphic'), sg.Text('Shiny:'),
           sg.Checkbox('', key='shiny')],
          [sg.Text("Who's that Pokemon:"), sg.Checkbox('coming soon', key='who')],
          [sg.Button('OK'), sg.Button('Save'), sg.Button('Cancel')],
          [sg.Image(key="pokemon_img"), sg.Text('', key='ditto')]]

window = sg.Window('Pokemon', layout, size=(550, 650))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    if event == 'OK':
        if os.path.exists('pokemon.png'):
            os.remove('pokemon.png')
        pokemon_func(values['pokemon_name'], values['graphic'], values['shiny'], values['who'])
        if os.path.exists('pokemon.png'):
            window['pokemon_img'].update(filename='pokemon.png')
        else:
            window['pokemon_img'].update(filename='ditto.png')

    if event == 'Save' and os.path.exists('pokemon.png'):
        file_path = sg.popup_get_file('Path', save_as=True, default_extension='.png')
        pokemon = Image.open('pokemon.png')
        pokemon.save(file_path)
    elif event == 'Save' and os.path.exists('ditto.png'):
        file_path = sg.popup_get_file('Path', save_as=True, default_extension='.png')
        pokemon = Image.open('ditto.png')
        pokemon.save(file_path)

window.close()
