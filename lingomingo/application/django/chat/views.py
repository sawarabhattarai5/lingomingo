# chat/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from mainapp.models import get_profile_model
from .models import *


@login_required()
def room(request, other_profile_uuid=''):
    context = {}
    if other_profile_uuid:
        other_profile = get_profile_model().get(uuid=other_profile_uuid)
        thread = get_or_create_thread(user1=request.user, user2=other_profile.user)
        messages = Message.objects.filter(thread=thread)
        context.update({'room_name': thread.id, 'msgs': messages, 'thread': thread})

    all_thread = get_thread_by_user(request.user)
    context.update({'all_thread': all_thread})
    return render(request, 'chat/room.html', context)
