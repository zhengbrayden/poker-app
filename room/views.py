from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# Create your views here.
from .models import Message, Room

@login_required
def rooms(request):
    if request.method == "POST":
        action = request.POST.get
        return redirect() #redirect to the appropriate room
    else:
        rooms = Room.objects.all()

        return render(request, 'room/rooms.html', {'rooms': rooms})

@login_required
def room(request, slug):
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room).order_by('-date_added')[0:25][::-1]
    return render(request, 'room/room.html', {'room': room, 'messages' : messages})