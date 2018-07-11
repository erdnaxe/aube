# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-07-02 18:56
from __future__ import unicode_literals

import re2o.aes_field
import cotisations.payment_methods.mixins
from django.db import migrations, models
import django.db.models.deletion


def add_cheque(apps, schema_editor):
    ChequePayment = apps.get_model('cotisations', 'ChequePayment')
    Payment = apps.get_model('cotisations', 'Paiement')
    for p in Payment.objects.filter(type_paiement=1):
        cheque = ChequePayment()
        cheque.payment = p
        cheque.save()


def add_comnpay(apps, schema_editor):
    ComnpayPayment = apps.get_model('cotisations', 'ComnpayPayment')
    Payment = apps.get_model('cotisations', 'Paiement')
    AssoOption = apps.get_model('preferences', 'AssoOption')
    options, _created = AssoOption.objects.get_or_create()
    payment, _created = Payment.objects.get_or_create(
        moyen='Rechargement en ligne'
    )
    comnpay = ComnpayPayment()
    comnpay.payment_user = options.payment_id
    comnpay.payment = payment
    comnpay.save()
    payment.moyen = "ComnPay"

    payment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0044_remove_payment_pass'),
        ('cotisations', '0031_article_allow_self_subscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChequePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='payment_method', to='cotisations.Paiement')),
            ],
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ComnpayPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_credential', models.CharField(blank=True, default='', max_length=255)),
                ('payment_pass', re2o.aes_field.AESEncryptedField(blank=True, max_length=255, null=True)),
                ('payment', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='payment_method', to='cotisations.Paiement')),
            ],
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
        ),
        migrations.RunPython(add_comnpay),
        migrations.RunPython(add_cheque),
    ]
