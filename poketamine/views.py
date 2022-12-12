import json
from time import sleep
from django.http import HttpResponse
from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt

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
            "id": tmp.get("id"),
            "name": tmp.get("name"),
            "image": tmp.get("sprites").get("front_default"),
            "types": types,
            "stats": tmp.get("stats"),
            "moves": moves,
            "height": tmp.get("height"),
            "weight": tmp.get("weight"),
            "next": "",
            "prev": ""
        }
        print(tmPoke)
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
    pokemonIndex = reqPokemons.index(pokemonDetails)
    pokemonHasNext = pokemonIndex != len(reqPokemons) - 1
    pokemonHasPrev = pokemonIndex > 0
    if pokemonHasNext:
        nextPokemon = reqPokemons[pokemonIndex + 1]
    else:
        nextPokemon = None
    
    if pokemonHasPrev:
        prevPokemon = reqPokemons[pokemonIndex - 1]
    else:
        prevPokemon = None
    pokemonDetails.update({"next": nextPokemon, "prev": prevPokemon})
    context = {'pokemon': pokemonDetails}
    return render(_, 'poketamine/details.html', context)

@csrf_exempt
def addToTeam(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            print(body)
            with open("team.json", "r") as file:
                team = json.load(file)
            with open("pokemons.json", "r") as file:
                pokemons = json.load(file)
            pokemon = list(filter(lambda x: x.get("name") == body.get("name"), pokemons))[0]
            try:
                if len(team[body.get("teamId")]["pokemons"]) == 6:
                    return HttpResponse("Team is full", status=406)
                team[body.get("teamId")]["pokemons"].append(pokemon)
            except:
                team.update({
                    body.get("teamId"): {"teamId": body.get("teamId"), "pokemons": [pokemon]}
                })

            with open("team.json", "w") as file:
                file.write(json.dumps(team))
            return HttpResponse("Success")
        except Exception as e:
            print(e)
            return HttpResponse("Error", status=500)
    else:
        return HttpResponse("Error 404", status=404)
    
def team(request):
    try:
        with open("team.json", "r") as file:
            teams = json.load(file)
    except:
        teams = []
    context = {"teams": teams}
    return render(request, 'poketamine/team.html', context)

@csrf_exempt
def removeTeam(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            with open("team.json", "r") as file:
                teams = json.load(file)
                teamId = str(body.get("teamId"))
                teams.pop(teamId)
            with open("team.json", "w") as file:
                file.write(json.dumps(teams))
            return HttpResponse("Success")
        except:
            return HttpResponse("Error", status=500)
        

@csrf_exempt
def removePokemon(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            with open("team.json", "r") as file:
                teams = json.load(file)
                teamId = str(body.get("teamId"))
                pokemonId = int(body.get("pokemonId"))
                tmp = teams.get(teamId).get("pokemons")
                tmp.pop(pokemonId)
                if len(tmp) == 0:
                    teams.pop(teamId)
                    with open("team.json", "w") as file:
                        file.write(json.dumps(teams))
                    return HttpResponse("Success")
                teams.get(teamId).update({"pokemons": tmp})
            with open("team.json", "w") as file:
                file.write(json.dumps(teams))
            return HttpResponse("Success")
        except:
            return HttpResponse("Error", status=500)