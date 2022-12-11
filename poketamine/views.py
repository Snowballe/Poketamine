import json
from time import sleep
from django.http import HttpResponse
from django.shortcuts import render
import requests

# Test if a string is in a list of string
def stringInList(str, list):
    for item in list:
        if item in str.get("name"):
            return True
    return False


# Update pokemons list from pokeapi
def UpdatePokemons(pokemons: list): 
    filteredPokemons = []
    for i in range(len(pokemons)):
        response = requests.get(pokemons[i].get("url"))
        tmp = response.json()
        types, moves = [], []
        for i in range(len(tmp.get("types"))):
            types.append(tmp.get("types")[i].get("type").get("name"))
        for i in range(len(tmp.get("moves"))):
            moves.append(tmp.get("moves")[i].get("move").get("name"))
        tmPoke = { 
            "name": tmp.get("name"),
            "image": tmp.get("sprites").get("front_default"),
            "types": types,
            "stats": tmp.get("stats"),
            "moves": moves,
            "height": tmp.get("height"),
            "weight": tmp.get("weight")
        }
        filteredPokemons.append(tmPoke)
    return filteredPokemons


def updateFile():
    # request all pokemons
    response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=151")
    reqPokemons = response.json().get("results")
    # get details for each pokemon
    UpdatedPokemons = UpdatePokemons(reqPokemons)
    # write to file pokemons.json
    with open("pokemons.json", "w") as file:
        file.write("[")
        for i in range(len(UpdatedPokemons)):
            file.write(json.dumps(UpdatedPokemons[i]))
            if i != len(UpdatedPokemons) - 1:
                file.write(",")
        file.write("]")

def index(request):
    # read file or create it if it doesn't exist
    try :
        with open("pokemons.json", "r") as file:
            reqPokemons = json.load(file)
    except:
        updateFile()
        with open("pokemons.json", "r") as file:
            reqPokemons = json.load(file)

    # get search query
    query: str = request.GET.get('search')
    if query is None or query == "":
        return render(request, 'poketamine/index.html', {'pokemons': reqPokemons})
    
    # filter pokemons
    queryPokemons = [pokemon for pokemon in query.split("-")]
    filteredPokemons: dict["name": str, "url": str] = [pokemon for pokemon in reqPokemons if stringInList(pokemon, queryPokemons)]

    # render filtered pokemons
    context = {'pokemons': filteredPokemons}
    return render(request, 'poketamine/index.html', context)

def details(_, pokemon: str):
    with open("pokemons.json", "r") as file:
        reqPokemons = json.load(file)

    # get pokemon details
    pokemonDetails = list(filter(lambda x: x.get("name") == pokemon, reqPokemons))[0]
    return HttpResponse(f"Details for {pokemonDetails.get('moves')}")