# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2019  Alexandre Iooss

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.contrib.auth.management import create_permissions
from django.db import migrations, models

import cotisations.payment_methods.mixins
import cotisations.validators
import re2o.aes_field
import re2o.field_permissions
import re2o.mixins


def create_type(apps, schema_editor):
    Cotisation = apps.get_model('cotisations', 'Cotisation')
    Vente = apps.get_model('cotisations', 'Vente')
    Article = apps.get_model('cotisations', 'Article')
    db_alias = schema_editor.connection.alias
    articles = Article.objects.using(db_alias).all()
    ventes = Vente.objects.using(db_alias).all()
    cotisations = Cotisation.objects.using(db_alias).all()
    for article in articles:
        if article.iscotisation:
            article.type_cotisation = 'All'
            article.save(using=db_alias)
    for vente in ventes:
        if vente.iscotisation:
            vente.type_cotisation = 'All'
            vente.save(using=db_alias)
    for cotisation in cotisations:
        cotisation.type_cotisation = 'All'
        cotisation.save(using=db_alias)


def delete_type(apps, schema_editor):
    Vente = apps.get_model('cotisations', 'Vente')
    Article = apps.get_model('cotisations', 'Article')
    db_alias = schema_editor.connection.alias
    articles = Article.objects.using(db_alias).all()
    ventes = Vente.objects.using(db_alias).all()
    for article in articles:
        if article.type_cotisation:
            article.iscotisation = True
        else:
            article.iscotisation = False
        article.save(using=db_alias)
    for vente in ventes:
        if vente.iscotisation:
            vente.iscotisation = True
        else:
            vente.iscotisation = False
        vente.save(using=db_alias)


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
    try:
        payment = Payment.objects.get(
            moyen='Rechargement en ligne'
        )
    except Payment.DoesNotExist:
        return
    comnpay = ComnpayPayment()
    comnpay.payment_user = options.payment_id
    comnpay.payment = payment
    comnpay.save()
    payment.moyen = "ComnPay"

    payment.save()


def add_solde(apps, schema_editor):
    OptionalUser = apps.get_model('preferences', 'OptionalUser')
    options, _created = OptionalUser.objects.get_or_create()

    Payment = apps.get_model('cotisations', 'Paiement')
    BalancePayment = apps.get_model('cotisations', 'BalancePayment')

    try:
        solde = Payment.objects.get(moyen="solde")
    except Payment.DoesNotExist:
        return
    balance = BalancePayment()
    balance.payment = solde
    balance.minimum_balance = options.solde_negatif
    balance.maximum_balance = options.max_solde
    solde.is_balance = True
    balance.save()
    solde.save()


def reattribute_ids(apps, schema_editor):
    Facture = apps.get_model('cotisations', 'Facture')
    BaseInvoice = apps.get_model('cotisations', 'BaseInvoice')

    for f in Facture.objects.all():
        base = BaseInvoice.objects.create(id=f.pk)
        base.date = f.date
        base.save()
        f.baseinvoice_ptr = base
        f.save()


def update_rights(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')

    # creates needed permissions
    app = apps.get_app_config('cotisations')
    app.models_module = True
    create_permissions(app)
    app.models_module = False

    ContentType = apps.get_model("contenttypes", "ContentType")
    content_type = ContentType.objects.get_for_model(Permission)
    former, created = Permission.objects.get_or_create(
        codename='change_facture_pdf', content_type=content_type)
    new_1 = Permission.objects.get(codename='add_custominvoice')
    new_2 = Permission.objects.get(codename='change_custominvoice')
    new_3 = Permission.objects.get(codename='view_custominvoice')
    new_4 = Permission.objects.get(codename='delete_custominvoice')
    for group in former.group_set.all():
        group.permissions.remove(former)
        group.permissions.add(new_1)
        group.permissions.add(new_2)
        group.permissions.add(new_3)
        group.permissions.add(new_4)
        group.save()


class Migration(migrations.Migration):
    replaces = [('cotisations', '0001_initial'),
                ('cotisations', '0002_remove_facture_article'),
                ('cotisations', '0003_auto_20160702_1448'),
                ('cotisations', '0004_auto_20160702_1528'),
                ('cotisations', '0005_auto_20160702_1532'),
                ('cotisations', '0006_auto_20160702_1534'),
                ('cotisations', '0007_auto_20160702_1543'),
                ('cotisations', '0008_auto_20160702_1614'),
                ('cotisations', '0009_remove_cotisation_user'),
                ('cotisations', '0010_auto_20160702_1840'),
                ('cotisations', '0011_auto_20160702_1911'),
                ('cotisations', '0012_auto_20160704_0118'),
                ('cotisations', '0013_auto_20160711_2240'),
                ('cotisations', '0014_auto_20160712_0245'),
                ('cotisations', '0015_auto_20160714_2142'),
                ('cotisations', '0016_auto_20160715_0110'),
                ('cotisations', '0017_auto_20170718_2329'),
                ('cotisations', '0018_paiement_type_paiement'),
                ('cotisations', '0019_auto_20170819_0055'),
                ('cotisations', '0020_auto_20170819_0057'),
                ('cotisations', '0021_auto_20170819_0104'),
                ('cotisations', '0022_auto_20170824_0128'),
                ('cotisations', '0023_auto_20170902_1303'),
                ('cotisations', '0024_auto_20171015_2033'),
                ('cotisations', '0025_article_type_user'),
                ('cotisations', '0026_auto_20171028_0126'),
                ('cotisations', '0027_auto_20171029_1156'),
                ('cotisations', '0028_auto_20171231_0007'),
                ('cotisations', '0029_auto_20180414_2056'),
                ('cotisations', '0030_custom_payment'),
                ('cotisations', '0031_comnpaypayment_production'),
                ('cotisations', '0032_custom_invoice'),
                ('cotisations', '0033_auto_20180818_1319'),
                ('cotisations', '0034_auto_20180831_1532'),
                ('cotisations', '0035_notepayment'),
                ('cotisations', '0036_custominvoice_remark'),
                ('cotisations', '0037_costestimate'),
                ('cotisations', '0038_auto_20181231_1657')]

    dependencies = [
        ('preferences', '0025_auto_20171231_2142'),
        ('users', '0005_auto_20160702_0006'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Banque',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('cheque', models.CharField(max_length=255)),
                ('number', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=5)),
                ('article',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='cotisations.Article')),
                ('banque',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='cotisations.Banque')),
            ],
        ),
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('moyen', models.CharField(max_length=255)),
                ('type_paiement',
                 models.IntegerField(choices=[(0, 'Autre'), (1, 'Chèque')],
                                     default=0)),
            ],
        ),
        migrations.AddField(
            model_name='facture',
            name='paiement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    to='cotisations.Paiement'),
        ),
        migrations.AddField(
            model_name='facture',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.RemoveField(
            model_name='facture',
            name='article',
        ),
        migrations.AlterField(
            model_name='facture',
            name='banque',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='cotisations.Banque'),
        ),
        migrations.RemoveField(
            model_name='facture',
            name='name',
        ),
        migrations.RemoveField(
            model_name='facture',
            name='prix',
        ),
        migrations.AlterField(
            model_name='facture',
            name='cheque',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.CreateModel(
            name='Cotisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='iscotisation',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='facture',
            name='valid',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='article',
            name='duration',
            field=models.PositiveIntegerField(blank=True,
                                              help_text='Durée exprimée en mois entiers',
                                              null=True, validators=[
                    django.core.validators.MinValueValidator(0)]),
        ),
        migrations.CreateModel(
            name='Vente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=5)),
                ('iscotisation', models.BooleanField()),
                ('duration', models.PositiveIntegerField(blank=True,
                                                         help_text='Durée exprimée en mois entiers',
                                                         null=True)),
                ('facture',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='cotisations.Facture')),
                ('number', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(1)])),
                ('type_cotisation', models.CharField(blank=True, choices=[
                    ('Connexion', 'Connexion'), ('Adhesion', 'Adhesion'),
                    ('All', 'All')], max_length=255, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='facture',
            name='number',
        ),
        migrations.AddField(
            model_name='facture',
            name='control',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cotisation',
            name='vente',
            field=models.OneToOneField(null=True,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       to='cotisations.Vente'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='article',
            name='type_user',
            field=models.CharField(
                choices=[('Adherent', 'Adherent'), ('Club', 'Club'),
                         ('All', 'All')], default='All', max_length=255),
        ),
        migrations.AddField(
            model_name='article',
            name='type_cotisation',
            field=models.CharField(blank=True,
                                   choices=[('Connexion', 'Connexion'),
                                            ('Adhesion', 'Adhesion'),
                                            ('All', 'All')], default=None,
                                   max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='cotisation',
            name='type_cotisation',
            field=models.CharField(
                choices=[('Connexion', 'Connexion'), ('Adhesion', 'Adhesion'),
                         ('All', 'All')], default='All', max_length=255),
        ),
        migrations.RunPython(
            code=create_type,
            reverse_code=delete_type,
        ),
        migrations.RemoveField(
            model_name='article',
            name='iscotisation',
        ),
        migrations.RemoveField(
            model_name='vente',
            name='iscotisation',
        ),
        migrations.AlterField(
            model_name='article',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterModelOptions(
            name='article',
            options={'permissions': (
                ('view_article', "Can see an article's details"),),
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles'},
        ),
        migrations.AlterModelOptions(
            name='banque',
            options={
                'permissions': (('view_banque', "Can see a bank's details"),),
                'verbose_name': 'Bank', 'verbose_name_plural': 'Banks'},
        ),
        migrations.AlterModelOptions(
            name='cotisation',
            options={'permissions': (
                ('view_cotisation', "Can see a cotisation's details"),
                (
                    'change_all_cotisation',
                    'Can edit the previous cotisations'))},
        ),
        migrations.AlterModelOptions(
            name='facture',
            options={'permissions': (
                ('change_facture_control', 'Can change the "controlled" state'),
                ('change_facture_pdf', 'Can create a custom PDF invoice'),
                ('view_facture', "Can see an invoice's details"),
                ('change_all_facture', 'Can edit all the previous invoices')),
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices'},
        ),
        migrations.AlterModelOptions(
            name='paiement',
            options={'permissions': (
                ('view_paiement', "Can see a payement's details"),),
                'verbose_name': 'Payment method',
                'verbose_name_plural': 'Payment methods'},
        ),
        migrations.AlterModelOptions(
            name='vente',
            options={'permissions': (
                ('view_vente', "Can see a purchase's details"),
                ('change_all_vente', 'Can edit all the previous purchases')),
                'verbose_name': 'Purchase',
                'verbose_name_plural': 'Purchases'},
        ),
        migrations.AlterField(
            model_name='article',
            name='duration',
            field=models.PositiveIntegerField(blank=True, null=True,
                                              validators=[
                                                  django.core.validators.MinValueValidator(
                                                      0)],
                                              verbose_name='Duration (in whole month)'),
        ),
        migrations.AlterField(
            model_name='article',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Designation'),
        ),
        migrations.AlterField(
            model_name='article',
            name='prix',
            field=models.DecimalField(decimal_places=2, max_digits=5,
                                      verbose_name='Unitary price'),
        ),
        migrations.AlterField(
            model_name='article',
            name='type_cotisation',
            field=models.CharField(blank=True,
                                   choices=[('Connexion', 'Connexion'),
                                            ('Adhesion', 'Membership'),
                                            ('All', 'Both of them')],
                                   default=None, max_length=255, null=True,
                                   verbose_name='Type of cotisation'),
        ),
        migrations.AlterField(
            model_name='article',
            name='type_user',
            field=models.CharField(
                choices=[('Adherent', 'Member'), ('Club', 'Club'),
                         ('All', 'Both of them')], default='All',
                max_length=255, verbose_name='Type of users concerned'),
        ),
        migrations.AlterField(
            model_name='banque',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='date_end',
            field=models.DateTimeField(verbose_name='Ending date'),
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='date_start',
            field=models.DateTimeField(verbose_name='Starting date'),
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='type_cotisation',
            field=models.CharField(
                choices=[('Connexion', 'Connexion'), ('Adhesion', 'Membership'),
                         ('All', 'Both of them')], default='All',
                max_length=255, verbose_name='Type of cotisation'),
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='vente',
            field=models.OneToOneField(null=True,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       to='cotisations.Vente',
                                       verbose_name='Purchase'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='cheque',
            field=models.CharField(blank=True, max_length=255,
                                   verbose_name='Cheque number'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='control',
            field=models.BooleanField(default=False, verbose_name='Controlled'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='valid',
            field=models.BooleanField(default=True, verbose_name='Validated'),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='moyen',
            field=models.CharField(max_length=255, verbose_name='Method'),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='type_paiement',
            field=models.IntegerField(choices=[(0, 'Standard'), (1, 'Cheque')],
                                      default=0, verbose_name='Payment type'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='duration',
            field=models.PositiveIntegerField(blank=True, null=True,
                                              verbose_name='Duration (in whole month)'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='facture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='cotisations.Facture',
                                    verbose_name='Invoice'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Article'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='number',
            field=models.IntegerField(
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name='Amount'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='prix',
            field=models.DecimalField(decimal_places=2, max_digits=5,
                                      verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='type_cotisation',
            field=models.CharField(blank=True,
                                   choices=[('Connexion', 'Connexion'),
                                            ('Adhesion', 'Membership'),
                                            ('All', 'Both of them')],
                                   max_length=255, null=True,
                                   verbose_name='Type of cotisation'),
        ),
        migrations.AlterModelOptions(
            name='paiement',
            options={'permissions': (
                ('view_paiement', "Can see a payement's details"),
                ('use_every_payment', 'Can use every payement')),
                'verbose_name': 'Payment method',
                'verbose_name_plural': 'Payment methods'},
        ),
        migrations.AlterModelOptions(
            name='article',
            options={'permissions': (
                ('view_article', "Can see an article's details"),
                ('buy_every_article', 'Can buy every_article')),
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles'},
        ),
        migrations.AddField(
            model_name='paiement',
            name='available_for_everyone',
            field=models.BooleanField(default=False,
                                      verbose_name='Is available for every user'),
        ),
        migrations.AddField(
            model_name='paiement',
            name='is_balance',
            field=models.BooleanField(default=False, editable=False,
                                      help_text='There should be only one balance payment method.',
                                      validators=[
                                          cotisations.validators.check_no_balance],
                                      verbose_name='Is user balance'),
        ),
        migrations.AddField(
            model_name='article',
            name='available_for_everyone',
            field=models.BooleanField(default=False,
                                      verbose_name='Is available for every user'),
        ),
        migrations.CreateModel(
            name='ChequePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('payment', models.OneToOneField(editable=False,
                                                 on_delete=django.db.models.deletion.CASCADE,
                                                 related_name='payment_method',
                                                 to='cotisations.Paiement')),
            ],
            options={
                'verbose_name': 'Cheque',
            },
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin,
                   models.Model),
        ),
        migrations.CreateModel(
            name='ComnpayPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('payment_credential',
                 models.CharField(blank=True, default='', max_length=255,
                                  verbose_name='ComNpay VAD Number')),
                ('payment_pass',
                 re2o.aes_field.AESEncryptedField(blank=True, max_length=255,
                                                  null=True,
                                                  verbose_name='ComNpay Secret Key')),
                ('payment', models.OneToOneField(editable=False,
                                                 on_delete=django.db.models.deletion.CASCADE,
                                                 related_name='payment_method',
                                                 to='cotisations.Paiement')),
                ('minimum_payment',
                 models.DecimalField(decimal_places=2, default=1,
                                     help_text='The minimal amount of money you have to use when paying with ComNpay',
                                     max_digits=5,
                                     verbose_name='Minimum payment')),
            ],
            options={
                'verbose_name': 'ComNpay',
            },
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin,
                   models.Model),
        ),
        migrations.CreateModel(
            name='BalancePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('minimum_balance',
                 models.DecimalField(decimal_places=2, default=0,
                                     help_text='The minimal amount of money allowed for the balance at the end of a payment. You can specify negative amount.',
                                     max_digits=5,
                                     verbose_name='Minimum balance')),
                ('payment', models.OneToOneField(editable=False,
                                                 on_delete=django.db.models.deletion.CASCADE,
                                                 related_name='payment_method',
                                                 to='cotisations.Paiement')),
                ('maximum_balance',
                 models.DecimalField(blank=True, decimal_places=2, default=50,
                                     help_text='The maximal amount of money allowed for the balance.',
                                     max_digits=5, null=True,
                                     verbose_name='Maximum balance')),
                ('credit_balance_allowed', models.BooleanField(default=False,
                                                               verbose_name='Allow user to credit their balance')),
            ],
            options={
                'verbose_name': 'User Balance',
            },
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin,
                   models.Model),
        ),
        migrations.RunPython(
            code=add_comnpay,
        ),
        migrations.RunPython(
            code=add_cheque,
        ),
        migrations.RunPython(
            code=add_solde,
        ),
        migrations.RemoveField(
            model_name='paiement',
            name='type_paiement',
        ),
        migrations.AddField(
            model_name='comnpaypayment',
            name='production',
            field=models.BooleanField(default=True,
                                      verbose_name='Production mode enabled (production url, instead of homologation)'),
        ),
        migrations.CreateModel(
            name='BaseInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('date',
                 models.DateTimeField(auto_now_add=True, verbose_name='Date')),
            ],
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin,
                   re2o.field_permissions.FieldPermissionModelMixin,
                   models.Model),
        ),
        migrations.CreateModel(
            name='CustomInvoice',
            fields=[
                ('baseinvoice_ptr', models.OneToOneField(auto_created=True,
                                                         on_delete=django.db.models.deletion.CASCADE,
                                                         parent_link=True,
                                                         primary_key=True,
                                                         serialize=False,
                                                         to='cotisations.BaseInvoice')),
                ('recipient',
                 models.CharField(max_length=255, verbose_name='Recipient')),
                ('payment',
                 models.CharField(max_length=255, verbose_name='Payment type')),
                ('address',
                 models.CharField(max_length=255, verbose_name='Address')),
                ('paid', models.BooleanField(verbose_name='Paid')),
            ],
            options={
                'permissions': (
                    ('view_custominvoice', 'Can view a custom invoice'),),
            },
            bases=('cotisations.baseinvoice',),
        ),
        migrations.AddField(
            model_name='facture',
            name='baseinvoice_ptr',
            field=models.OneToOneField(null=True,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       to='cotisations.BaseInvoice'),
            preserve_default=False,
        ),
        migrations.RunPython(
            code=reattribute_ids,
        ),
        migrations.AlterField(
            model_name='vente',
            name='facture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='cotisations.BaseInvoice',
                                    verbose_name='Invoice'),
        ),
        migrations.RemoveField(
            model_name='facture',
            name='id',
        ),
        migrations.RemoveField(
            model_name='facture',
            name='date',
        ),
        migrations.AlterField(
            model_name='facture',
            name='baseinvoice_ptr',
            field=models.OneToOneField(auto_created=True,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       parent_link=True, primary_key=True,
                                       serialize=False,
                                       to='cotisations.BaseInvoice'),
        ),
        migrations.RunPython(
            code=update_rights,
        ),
        migrations.AlterModelOptions(
            name='facture',
            options={'permissions': (
                ('change_facture_control', 'Can edit the "controlled" state'),
                ('view_facture', 'Can view an invoice object'),
                ('change_all_facture', 'Can edit all the previous invoices')),
                'verbose_name': 'invoice', 'verbose_name_plural': 'invoices'},
        ),
        migrations.AlterModelOptions(
            name='article',
            options={
                'permissions': (('view_article', 'Can view an article object'),
                                (
                                    'buy_every_article',
                                    'Can buy every article')),
                'verbose_name': 'article', 'verbose_name_plural': 'articles'},
        ),
        migrations.AlterModelOptions(
            name='balancepayment',
            options={'verbose_name': 'user balance'},
        ),
        migrations.AlterModelOptions(
            name='banque',
            options={
                'permissions': (('view_banque', 'Can view a bank object'),),
                'verbose_name': 'bank', 'verbose_name_plural': 'banks'},
        ),
        migrations.AlterModelOptions(
            name='cotisation',
            options={'permissions': (
                ('view_cotisation', 'Can view a subscription object'),
                ('change_all_cotisation',
                 'Can edit the previous subscriptions')),
                'verbose_name': 'subscription',
                'verbose_name_plural': 'subscriptions'},
        ),
        migrations.AlterModelOptions(
            name='custominvoice',
            options={'permissions': (
                ('view_custominvoice', 'Can view a custom invoice object'),)},
        ),
        migrations.AlterModelOptions(
            name='paiement',
            options={'permissions': (
                ('view_paiement', 'Can view a payment method object'),
                ('use_every_payment', 'Can use every payment method')),
                'verbose_name': 'payment method',
                'verbose_name_plural': 'payment methods'},
        ),
        migrations.AlterModelOptions(
            name='vente',
            options={
                'permissions': (('view_vente', 'Can view a purchase object'), (
                    'change_all_vente', 'Can edit all the previous purchases')),
                'verbose_name': 'purchase',
                'verbose_name_plural': 'purchases'},
        ),
        migrations.AlterField(
            model_name='article',
            name='available_for_everyone',
            field=models.BooleanField(default=False,
                                      verbose_name='is available for every user'),
        ),
        migrations.AlterField(
            model_name='article',
            name='duration',
            field=models.PositiveIntegerField(blank=True, null=True,
                                              validators=[
                                                  django.core.validators.MinValueValidator(
                                                      0)],
                                              verbose_name='duration (in months)'),
        ),
        migrations.AlterField(
            model_name='article',
            name='name',
            field=models.CharField(max_length=255, verbose_name='designation'),
        ),
        migrations.AlterField(
            model_name='article',
            name='prix',
            field=models.DecimalField(decimal_places=2, max_digits=5,
                                      verbose_name='unit price'),
        ),
        migrations.AlterField(
            model_name='article',
            name='type_cotisation',
            field=models.CharField(blank=True,
                                   choices=[('Connexion', 'Connection'),
                                            ('Adhesion', 'Membership'),
                                            ('All', 'Both of them')],
                                   default=None, max_length=255, null=True,
                                   verbose_name='subscription type'),
        ),
        migrations.AlterField(
            model_name='article',
            name='type_user',
            field=models.CharField(
                choices=[('Adherent', 'Member'), ('Club', 'Club'),
                         ('All', 'Both of them')], default='All',
                max_length=255,
                verbose_name='type of users concerned'),
        ),
        migrations.AlterField(
            model_name='banque',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='comnpaypayment',
            name='payment_credential',
            field=models.CharField(blank=True, default='', max_length=255,
                                   verbose_name='ComNpay VAT Number'),
        ),
        migrations.AlterField(
            model_name='comnpaypayment',
            name='payment_pass',
            field=re2o.aes_field.AESEncryptedField(blank=True, max_length=255,
                                                   null=True,
                                                   verbose_name='ComNpay secret key'),
        ),
        migrations.AlterField(
            model_name='comnpaypayment',
            name='production',
            field=models.BooleanField(default=True,
                                      verbose_name='Production mode enabled (production URL, instead of homologation)'),
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='date_end',
            field=models.DateTimeField(verbose_name='end date'),
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='date_start',
            field=models.DateTimeField(verbose_name='start date'),
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='type_cotisation',
            field=models.CharField(
                choices=[('Connexion', 'Connection'),
                         ('Adhesion', 'Membership'),
                         ('All', 'Both of them')], default='All',
                max_length=255,
                verbose_name='subscription type'),
        ),
        migrations.AlterField(
            model_name='cotisation',
            name='vente',
            field=models.OneToOneField(null=True,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       to='cotisations.Vente',
                                       verbose_name='purchase'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='cheque',
            field=models.CharField(blank=True, max_length=255,
                                   verbose_name='cheque number'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='control',
            field=models.BooleanField(default=False, verbose_name='controlled'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='valid',
            field=models.BooleanField(default=True, verbose_name='validated'),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='available_for_everyone',
            field=models.BooleanField(default=False,
                                      verbose_name='is available for every user'),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='is_balance',
            field=models.BooleanField(default=False, editable=False,
                                      help_text='There should be only one balance payment method.',
                                      validators=[
                                          cotisations.validators.check_no_balance],
                                      verbose_name='is user balance'),
        ),
        migrations.AlterField(
            model_name='paiement',
            name='moyen',
            field=models.CharField(max_length=255, verbose_name='method'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='duration',
            field=models.PositiveIntegerField(blank=True, null=True,
                                              verbose_name='duration (in months)'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='facture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='cotisations.BaseInvoice',
                                    verbose_name='invoice'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='name',
            field=models.CharField(max_length=255, verbose_name='article'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='number',
            field=models.IntegerField(
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name='amount'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='prix',
            field=models.DecimalField(decimal_places=2, max_digits=5,
                                      verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='type_cotisation',
            field=models.CharField(blank=True,
                                   choices=[('Connexion', 'Connection'),
                                            ('Adhesion', 'Membership'),
                                            ('All', 'Both of them')],
                                   max_length=255, null=True,
                                   verbose_name='subscription type'),
        ),
        migrations.AlterField(
            model_name='facture',
            name='valid',
            field=models.BooleanField(default=False, verbose_name='validated'),
        ),
        migrations.CreateModel(
            name='NotePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('server',
                 models.CharField(max_length=255, verbose_name='server')),
                ('port', models.PositiveIntegerField(blank=True, null=True)),
                ('id_note', models.PositiveIntegerField(blank=True, null=True)),
                ('payment', models.OneToOneField(editable=False,
                                                 on_delete=django.db.models.deletion.CASCADE,
                                                 related_name='payment_method',
                                                 to='cotisations.Paiement')),
            ],
            options={
                'verbose_name': 'NoteKfet',
            },
            bases=(
                cotisations.payment_methods.mixins.PaymentMethodMixin,
                models.Model),
        ),
        migrations.AddField(
            model_name='custominvoice',
            name='remark',
            field=models.TextField(blank=True, null=True,
                                   verbose_name='Remark'),
        ),
        migrations.CreateModel(
            name='CostEstimate',
            fields=[
                ('custominvoice_ptr', models.OneToOneField(auto_created=True,
                                                           on_delete=django.db.models.deletion.CASCADE,
                                                           parent_link=True,
                                                           primary_key=True,
                                                           serialize=False,
                                                           to='cotisations.CustomInvoice')),
                ('validity', models.DurationField(help_text='DD HH:MM:SS',
                                                  verbose_name='Period of validity')),
                ('final_invoice', models.ForeignKey(blank=True, null=True,
                                                    on_delete=django.db.models.deletion.SET_NULL,
                                                    related_name='origin_cost_estimate',
                                                    to='cotisations.CustomInvoice')),
            ],
            options={
                'permissions': (
                    ('view_costestimate', 'Can view a cost estimate object'),),
            },
            bases=('cotisations.custominvoice',),
        ),
        migrations.AlterField(
            model_name='custominvoice',
            name='paid',
            field=models.BooleanField(default=False, verbose_name='Paid'),
        ),
    ]
