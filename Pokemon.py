import requests
from PIL import Image
import PySimpleGUI as sg
import os


def pokemon_image(pokemon_name, type, shiny, who):
    try:
        pokeapi = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower() and pokemon_name.replace(' ', '-')}")
        pokemon = pokeapi.json()

        if type == 'Default' and shiny == True:
            url = pokemon['sprites']['front_shiny']
        elif type == 'Artwork' and shiny == False:
            url = pokemon['sprites'].get('other', pokemon['sprites']).get('official-artwork')['front_default']
        elif type == 'Artwork' and shiny == True:
            url = pokemon['sprites'].get('other', pokemon['sprites']).get('official-artwork')['front_shiny']
        elif type == 'Home' and shiny == False:
            url = pokemon['sprites'].get('other', pokemon['sprites']).get('home')['front_default']
        elif type == 'Home' and shiny == True:
            url = pokemon['sprites'].get('other', pokemon['sprites']).get('home')['front_shiny']
        else:
            url = pokemon['sprites']['front_default']

        img = Image.open(requests.get(url, stream=True).raw)
        if who == True:
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
        else:
            img.save('pokemon.png', 'PNG')

        img = Image.open('pokemon.png')
        resized_img = img.resize((500, 500))
        resized_img.save('pokemon.png')
    except:  #ditto
        dittoapi = requests.get("https://pokeapi.co/api/v2/pokemon/ditto")
        ditto = dittoapi.json()
        dittourl = ditto['sprites'].get('other', ditto['sprites']).get('official-artwork')['front_default']
        dittoimg = Image.open(requests.get(dittourl, stream=True).raw)
        dittoimg = dittoimg.convert("RGBA")
        dittoimg.save('ditto.png', 'PNG')
        dittoimg = Image.open('ditto.png')
        resized_img = dittoimg.resize((500, 500))
        resized_img.save('ditto.png')


layout = [[sg.Text('Enter Pokemon NAME:'), sg.InputText(key="pokemon_name")],
          [sg.Text('Graphics type:'), sg.Combo(['Default', 'Artwork', 'Home'], key='type'), sg.Text('Shiny:'), sg.Checkbox('', key='shiny')],
          [sg.Text("Who's that Pokemon:"), sg.Checkbox('coming soon', key='who')],
          [sg.Button('OK'), sg.Button('Save'), sg.Button('Cancel')],
          [sg.Image(key="pokemon_img"), sg.Text('', key='ditto')]]

window = sg.Window('Pokemon', layout, size=(550, 650))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    if event == 'OK':
        if os.path.exists('pokemon.png') == True:
            os.remove('pokemon.png')
        pokemon_image(values['pokemon_name'], values['type'], values['shiny'], values['who'])
        if os.path.exists('pokemon.png') == True:
            window['pokemon_img'].update(filename='pokemon.png')
        else:
            window['pokemon_img'].update(filename='ditto.png')

    if event == 'Save' and os.path.exists('pokemon.png') == True:
        file_path = sg.popup_get_file('Path', save_as=True, default_extension='.png')
        pokemon = Image.open('pokemon.png')
        pokemon.save(file_path)
    elif event == 'Save' and os.path.exists('ditto.png') == True:
        file_path = sg.popup_get_file('Path', save_as=True, default_extension='.png')
        pokemon = Image.open('ditto.png')
        pokemon.save(file_path)
window.close()
