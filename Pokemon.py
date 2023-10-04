import numpy as np
import requests
from PIL import Image
from matplotlib import pyplot as plt
import PySimpleGUI as sg

def pokemon_image(pokemon_name):
    pokeapi = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}")
    pokemon = pokeapi.json()
    url = pokemon['sprites'].get('other', pokemon['sprites']).get('official-artwork')['front_default']
    img = Image.open(requests.get(url, stream=True).raw)

    plt.imshow(np.asarray(img))
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('pokemon.png')
    plt.close()

layout = [[sg.Text('Enter Pokemon NAME'), sg.InputText(key="a")],
          [sg.Text('Pokemon:'), sg.Image(key="pokemon")],
          [sg.Button('OK'), sg.Button('Cancel')]]

window = sg.Window('Window Title', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break
    if event == "OK":
        pokemon_image(values["a"])
        window['pokemon'].update(filename='pokemon.png')

window.close()