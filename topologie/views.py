from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.db import transaction
from reversion import revisions as reversion

from topologie.models import Switch, Port, Room
from topologie.forms import EditPortForm, EditSwitchForm, AddPortForm, EditRoomForm
from users.views import form

@login_required
@permission_required('cableur')
def index(request):
    switch_list = Switch.objects.order_by('building', 'number')
    return render(request, 'topologie/index.html', {'switch_list': switch_list})

@login_required
@permission_required('cableur')
def history(request, object, id):
    if object == 'switch':
        try:
             object_instance = Switch.objects.get(pk=id)
        except Switch.DoesNotExist:
             messages.error(request, "Switch inexistant")
             return redirect("/topologie/")
    elif object == 'port':
        try:
             object_instance = Port.objects.get(pk=id)
        except Port.DoesNotExist:
             messages.error(request, "Port inexistant")
             return redirect("/topologie/") 
    elif object == 'room':  
        try:
             object_instance = Room.objects.get(pk=id)
        except Room.DoesNotExist:
             messages.error(request, "Chambre inexistante")
             return redirect("/topologie/")
    else:
        messages.error(request, "Objet  inconnu")
        return redirect("/topologie/")
    reversions = reversion.get_for_object(object_instance)
    return render(request, 're2o/history.html', {'reversions': reversions, 'object': object_instance})

@login_required
@permission_required('cableur')
def index_port(request, switch_id):
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    port_list = Port.objects.filter(switch = switch).order_by('port')
    return render(request, 'topologie/index_p.html', {'port_list':port_list, 'id_switch':switch_id, 'nom_switch':switch})

@login_required
@permission_required('cableur')
def index_room(request):
    room_list = Room.objects.order_by('name')
    return render(request, 'topologie/index_room.html', {'room_list': room_list})

@login_required
@permission_required('infra')
def new_port(request, switch_id):
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    port = AddPortForm(request.POST or None)
    if port.is_valid():
        port = port.save(commit=False)
        port.switch = switch
        try:
            with transaction.atomic(), reversion.create_revision():
                port.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            messages.success(request, "Port ajouté")
        except IntegrityError:
            messages.error(request,"Ce port existe déjà" )
        return redirect("/topologie/switch/" + switch_id)
    return form({'topoform':port}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def edit_port(request, port_id):
    try:
        port = Port.objects.get(pk=port_id)
    except Port.DoesNotExist:
        messages.error(request, u"Port inexistant")
        return redirect("/topologie/")
    port = EditPortForm(request.POST or None, instance=port)
    if port.is_valid():
        with transaction.atomic(), reversion.create_revision():
            port.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in port.changed_data))
        messages.success(request, "Le port a bien été modifié")
        return redirect("/topologie/")
    return form({'topoform':port}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def new_switch(request):
    switch = EditSwitchForm(request.POST or None)
    if switch.is_valid():
        with transaction.atomic(), reversion.create_revision():
            switch.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Le switch a été créé")
        return redirect("/topologie/")
    return form({'topoform':switch}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def edit_switch(request, switch_id):
    try:
        switch = Switch.objects.get(pk=switch_id)
    except Switch.DoesNotExist:
        messages.error(request, u"Switch inexistant")
        return redirect("/topologie/")
    switch = EditSwitchForm(request.POST or None, instance=switch)
    if switch.is_valid():
        with transaction.atomic(), reversion.create_revision():
            switch.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in switch.changed_data))
        messages.success(request, "Le switch a bien été modifié")
        return redirect("/topologie/")
    return form({'topoform':switch}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def new_room(request):
    room = EditRoomForm(request.POST or None)
    if room.is_valid():
        with transaction.atomic(), reversion.create_revision():
            room.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "La chambre a été créé")
        return redirect("/topologie/index_room/")
    return form({'topoform':room}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def edit_room(request, room_id):
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        messages.error(request, u"Chambre inexistante")
        return redirect("/topologie/index_room/")
    room = EditRoomForm(request.POST or None, instance=room)
    if room.is_valid():
        with transaction.atomic(), reversion.create_revision():
            room.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in room.changed_data))
        messages.success(request, "La chambre a bien été modifiée")
        return redirect("/topologie/index_room/")
    return form({'topoform':room}, 'topologie/topo.html', request)

@login_required
@permission_required('infra')
def del_room(request, room_id):
    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        messages.error(request, u"Chambre inexistante" )
        return redirect("/topologie/index_room/")
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            room.delete()
            reversion.set_user(request.user)
            reversion.set_comment("Destruction")
        messages.success(request, "La chambre/prise a été détruite")
        return redirect("/topologie/index_room/")
    return form({'objet': room, 'objet_name': 'Chambre'}, 'topologie/delete.html', request)
