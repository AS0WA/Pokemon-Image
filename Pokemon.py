import requests
from PIL import Image
import PySimpleGUI as sg
import os


def pokemon_func(pokemon_name, graphic, shiny, who):
    pokemon = pokemon_image_url(pokemon_name, graphic, shiny)
    if pokemon is not None:
        if who is True:
            img = pokemon_who(pokemon[0])
        else:
            pokemon[0].save("pokemon.png", "PNG")

        img = Image.open("pokemon.png")
        resized_img = img.resize((500, 500))
        resized_img.save("pokemon.png")

        return pokemon[1]


def pokemon_image_url(pokemon_name, graphic, shiny):
    try:
        pokeapi = requests.get(
            f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower() and pokemon_name.replace(' ', '-')}")
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
        if os.path.exists("pokemon.png"):
            os.remove("pokemon.png")
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
    img.save("pokemon.png", "PNG")

    return img


def change_pokemon(window, offset, values, pokemon_data):
    pokemon_id = pokemon_data[1] + offset
    pokemon_data = pokemon_func(
        str(pokemon_id), values["graphic"], values["shiny"], values["who"]
    )

    if os.path.exists("pokemon.png"):
        window["pokemon name"].update(pokemon_id)
        window["pokemon img"].update(filename="pokemon.png")
        window["pokemon data"].update(f"Name: {pokemon_data[0]}, ID: {pokemon_data[1]}")
        window["pokemon not found"].update("")


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
    [sg.Text("Who's that Pokemon:"), sg.Checkbox("coming soon", key="who")],
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
        # Delete old pokemon.png
        if os.path.exists("pokemon.png"):
            os.remove("pokemon.png")

        # Make pokemon image, name and ID
        pokemon_data = pokemon_func(
            values["pokemon name"], values["graphic"], values["shiny"], values["who"]
        )

        # Correct data
        if os.path.exists("pokemon.png"):
            window["pokemon img"].update(filename="pokemon.png")
            window["pokemon not found"].update("")
            window["pokemon data"].update(
                f"Name: {pokemon_data[0]}, ID: {pokemon_data[1]}"
            )
            window["Save"].update(disabled=False)
            window["Previous"].update(disabled=False)
            window["Next"].update(disabled=False)

        # Incorrect data
        else:
            window["pokemon not found"].update("Pokemon not found")
            window["pokemon img"].update()

    # Save
    if event == "Save" and os.path.exists("pokemon.png"):
        desktop = os.path.join(
            "c:\\Users", os.getlogin(), f"Desktop\\{pokemon_data[0]}.png"
        )
        file_path = sg.popup_get_file(
            "Path", save_as=True, default_path=desktop, default_extension=".png"
        )
        pokemon = Image.open("pokemon.png")
        if file_path is not None:
            pokemon.save(file_path)

    # Previous Next
    if event in ["Previous", "Next"] and os.path.exists("pokemon.png"):
        pokemon_id = pokemon_data[1] + (-1 if event == "Previous" else 1)
        pokemon_data = pokemon_func(
            str(pokemon_id), values["graphic"], values["shiny"], values["who"]
        )

        # Make new pokemon.png
        if os.path.exists("pokemon.png"):
            window["pokemon img"].update(filename="pokemon.png")
            window["pokemon not found"].update("")
            window["pokemon data"].update(
                f"Name: {pokemon_data[0]}, ID: {pokemon_data[1]}"
            )

            # Change value "pokemon name" with ID
            if values["pokemon name"].isdigit():
                window["pokemon name"].update(pokemon_data[1])

            # Change value "pokemon name" with name
            else:
                window["pokemon name"].update(pokemon_data[0])

window.close()
