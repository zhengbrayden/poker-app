from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import SearchForm
# Create your views here.
from .storage import channel, slug_generator, messages
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

@login_required
def rooms(request):
    logic_error = None

    if request.method == "POST":
        form = SearchForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data['action']
            name = form.cleaned_data['name']

            if action == 'create':
                #lobby creation successful
                res = channel.create_lobby(name, request.user.id)

                if res == 2:
                    #add initial message to lobby
                    messages.add(name, f"Lobby with name '{name}' has been sucessfully created.")
                    messages.add(name, f"'{username}' has joined the lobby.")

                    #generate a slug for the name
                    return redirect(f"{slug_generator.create_slug(name)}/")
                elif res == 0:
                    logic_error = f'The lobby "{name}" has already been created, use join button instead.'
                else:
                    lobby_name = channel.get_player(request.user.id).get_lobby().get_name()
                    logic_error = f'You are already inside the lobby "{lobby_name}".'


            elif action == 'join':
                res = channel.create_player(name, request.user.id)

                if res == 3:
                    #add join message
                    username = User.objects.get(id=request.user.id).username
                    messages.add(name, f"'{username}' has joined the lobby.")
                    return redirect(f"{slug_generator.name2slug[name]}/")
                elif res == 0:
                    logic_error = f'The lobby "{name}" does not exist, use create button instead.'
                
                elif res == 1:
                    #check if player is already in the lobby they are trying to join and if so, redirect them

                    lobby_name = channel.get_player(request.user.id).get_lobby().get_name()

                    if lobby_name == name:
                        return redirect(f"{slug_generator.name2slug[name]}/")

                    logic_error = f'You are already inside the lobby "{lobby_name}".'                    
                else:
                    logic_error = f'The lobby "{lobby_name}" has already started, please wait for another round.'

    else:
        form = SearchForm()

    return render(request, 'room/rooms.html', {'form': form, 'logic_error': logic_error})

@login_required
def room(request, slug):

    # To load the room, the lobby must exist
    if slug not in slug_generator.slug2name:
        raise Http404("Lobby does not exist")

    # User must be a player in the lobby
    lobby = channel.get_lobby(slug_generator.slug2name[slug])

    if not request.user.id in lobby.get_ids():
        raise PermissionDenied()
    
    # Load a page containing the game state

    is_leader = False

    if request.user.id == lobby.get_leader():
        is_leader = True

    lobby_messages = messages.get(lobby.get_name())
    slug = slug_generator.name2slug[lobby.get_name()]

    player = channel.get_player(request.user.id)
    return render(request, 'room/room.html', {'messages' : lobby_messages, 
                                              'lobby': lobby,
                                              'is_leader' : is_leader,
                                              'player': player,
                                              'slug': slug,})