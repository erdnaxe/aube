"""Payment

Here are defined some views dedicated to online payement.
"""
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseBadRequest

from collections import OrderedDict

from preferences.models import AssoOption
from .models import Facture
from .payment_utils.comnpay import Payment as ComnpayPayment

@csrf_exempt
@login_required
def accept_payment(request, factureid):
    facture = get_object_or_404(Facture, id=factureid)
    messages.success(
        request,
        _("The payment of %(amount)s € has been accepted.") % {
            amount: facture.prix()
        }
    )
    return redirect(reverse('users:profil', kwargs={'userid':request.user.id}))


@csrf_exempt
@login_required
def refuse_payment(request):
    messages.error(
        request,
        _("The payment has been refused.")
    )
    return redirect(reverse('users:profil', kwargs={'userid':request.user.id}))

@csrf_exempt
def ipn(request):
    p = ComnpayPayment()
    order = ('idTpe', 'idTransaction', 'montant', 'result', 'sec', )
    try:
        data = OrderedDict([(f, request.POST[f]) for f in order])
    except MultiValueDictKeyError:
        return HttpResponseBadRequest("HTTP/1.1 400 Bad Request")

    if not p.validSec(data, AssoOption.get_cached_value('payment_pass')):
        return HttpResponseBadRequest("HTTP/1.1 400 Bad Request")

    result = True if (request.POST['result'] == 'OK') else False
    idTpe = request.POST['idTpe']
    idTransaction = request.POST['idTransaction']

    # On vérifie que le paiement nous est destiné
    # TODO : translate comment to English
    if not idTpe == AssoOption.get_cached_value('payment_id'):
        return HttpResponseBadRequest("HTTP/1.1 400 Bad Request")

    try:
        factureid = int(idTransaction)
    except ValueError:
        return HttpResponseBadRequest("HTTP/1.1 400 Bad Request")

    facture = get_object_or_404(Facture, id=factureid)

    # TODO : translate comments to English
    # On vérifie que le paiement est valide
    if not result:
        # Le paiement a échoué : on effectue les actions nécessaires (On indique qu'elle a échoué)
        facture.delete()

        # On notifie au serveur ComNPay qu'on a reçu les données pour traitement
        return HttpResponse("HTTP/1.1 200 OK")

    facture.valid = True
    facture.save()

    # A nouveau, on notifie au serveur qu'on a bien traité les données
    return HttpResponse("HTTP/1.0 200 OK")


def comnpay(facture, request):
    host = request.get_host()
    p = ComnpayPayment(
        str(AssoOption.get_cached_value('payment_id')),
        str(AssoOption.get_cached_value('payment_pass')),
        'https://' + host + reverse(
            'cotisations:accept_payment',
            kwargs={'factureid':facture.id}
        ),
        'https://' + host + reverse('cotisations:refuse_payment'),
        'https://' + host + reverse('cotisations:ipn'),
        "",
        "D"
    )
    r = {
        'action' : 'https://secure.homologation.comnpay.com',
        'method' : 'POST',
        'content' : p.buildSecretHTML(
            "Rechargement du solde",
            facture.prix(),
            idTransaction=str(facture.id)
        ),
        'amount' : facture.prix,
    }
    return r


PAYMENT_SYSTEM = {
    'COMNPAY' : comnpay,
    'NONE' : None
}
