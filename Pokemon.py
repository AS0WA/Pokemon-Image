import requests
from PIL import Image
from matplotlib import pyplot as plt
import PySimpleGUI as sg

def pokemon_image(pokemon_name, type, shiny):
    try:
        pokeapi = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower() and pokemon_name.replace(' ', '-')}")
        if pokeapi.status_code != 200:
            pokeapi = requests.get(f"https://pokeapi.co/api/v2/pokemon/ditto")
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

        plt.imshow(img)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig('pokemon.png')
        plt.close()
    except:
        pokeapi = requests.get(f"https://pokeapi.co/api/v2/pokemon/ditto")

layout = [[sg.Text('Enter Pokemon NAME:'), sg.InputText(key="pokemon_name")],
          [sg.Text('Rodzaj grafiki:'), sg.Combo(['Default', 'Artwork', 'Home'], key='type')],
          [sg.Text('Shiny:'), sg.Checkbox('', key='shiny')],
          [sg.Text('Pokemon:'), sg.Image(key="pokemon_img")],
          [sg.Button('OK'), sg.Button('Cancel')]]

window = sg.Window('Window Title', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    if event == "OK":
        pokemon_image(values['pokemon_name'], values['type'], values['shiny'])
        window['pokemon_img'].update(filename='pokemon.png')

window.close()