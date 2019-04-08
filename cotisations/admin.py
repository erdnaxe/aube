# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""cotisations.admin
The objects, fields and datastructures visible in the Django admin view
"""

from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Facture, Article, Banque, Paiement, Cotisation, Vente
from .models import CustomInvoice, CostEstimate


class FactureAdmin(VersionAdmin):
    """Class admin d'une facture, tous les champs"""
    pass


class CostEstimateAdmin(VersionAdmin):
    """Admin class for cost estimates."""
    pass


class CustomInvoiceAdmin(VersionAdmin):
    """Admin class for custom invoices."""
    pass


class VenteAdmin(VersionAdmin):
    """Class admin d'une vente, tous les champs (facture related)"""
    pass


class ArticleAdmin(VersionAdmin):
    """Class admin d'un article en vente"""
    pass


class BanqueAdmin(VersionAdmin):
    """Class admin de la liste des banques (facture related)"""
    pass


class PaiementAdmin(VersionAdmin):
    """Class admin d'un moyen de paiement (facture related"""
    pass


class CotisationAdmin(VersionAdmin):
    """Class admin d'une cotisation (date de debut et de fin),
    Vente related"""
    pass


admin.site.register(Facture, FactureAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Banque, BanqueAdmin)
admin.site.register(Paiement, PaiementAdmin)
admin.site.register(Vente, VenteAdmin)
admin.site.register(Cotisation, CotisationAdmin)
admin.site.register(CustomInvoice, CustomInvoiceAdmin)
admin.site.register(CostEstimate, CostEstimateAdmin)
