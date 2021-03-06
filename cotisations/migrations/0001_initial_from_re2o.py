# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-04-08 16:05
from __future__ import unicode_literals

import cotisations.payment_methods.mixins
import cotisations.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re2o.aes_field
import re2o.field_permissions
import re2o.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='designation')),
                ('prix', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='unit price')),
                ('duration', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='duration (in months)')),
                ('type_user', models.CharField(choices=[('Adherent', 'Member'), ('Club', 'Club'), ('All', 'Both of them')], default='All', max_length=255, verbose_name='type of users concerned')),
                ('type_cotisation', models.CharField(blank=True, choices=[('Connexion', 'Connection'), ('Adhesion', 'Membership'), ('All', 'Both of them')], default=None, max_length=255, null=True, verbose_name='subscription type')),
                ('available_for_everyone', models.BooleanField(default=False, verbose_name='is available for every user')),
            ],
            options={
                'verbose_name': 'article',
                'verbose_name_plural': 'articles',
                'permissions': (('view_article', 'Can view an article object'), ('buy_every_article', 'Can buy every article')),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BalancePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minimum_balance', models.DecimalField(decimal_places=2, default=0, help_text='The minimal amount of money allowed for the balance at the end of a payment. You can specify negative amount.', max_digits=5, verbose_name='Minimum balance')),
                ('maximum_balance', models.DecimalField(blank=True, decimal_places=2, default=50, help_text='The maximal amount of money allowed for the balance.', max_digits=5, null=True, verbose_name='Maximum balance')),
                ('credit_balance_allowed', models.BooleanField(default=False, verbose_name='Allow user to credit their balance')),
            ],
            options={
                'verbose_name': 'user balance',
            },
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Banque',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'bank',
                'verbose_name_plural': 'banks',
                'permissions': (('view_banque', 'Can view a bank object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='BaseInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
            ],
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, re2o.field_permissions.FieldPermissionModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ChequePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Cheque',
            },
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ComnpayPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_credential', models.CharField(blank=True, default='', max_length=255, verbose_name='ComNpay VAT Number')),
                ('payment_pass', re2o.aes_field.AESEncryptedField(blank=True, max_length=255, null=True, verbose_name='ComNpay secret key')),
                ('minimum_payment', models.DecimalField(decimal_places=2, default=1, help_text='The minimal amount of money you have to use when paying with ComNpay', max_digits=5, verbose_name='Minimum payment')),
                ('production', models.BooleanField(default=True, verbose_name='Production mode enabled (production URL, instead of homologation)')),
            ],
            options={
                'verbose_name': 'ComNpay',
            },
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Cotisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_cotisation', models.CharField(choices=[('Connexion', 'Connection'), ('Adhesion', 'Membership'), ('All', 'Both of them')], default='All', max_length=255, verbose_name='subscription type')),
                ('date_start', models.DateTimeField(verbose_name='start date')),
                ('date_end', models.DateTimeField(verbose_name='end date')),
            ],
            options={
                'verbose_name': 'subscription',
                'verbose_name_plural': 'subscriptions',
                'permissions': (('view_cotisation', 'Can view a subscription object'), ('change_all_cotisation', 'Can edit the previous subscriptions')),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='NotePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server', models.CharField(max_length=255, verbose_name='server')),
                ('port', models.PositiveIntegerField(blank=True, null=True)),
                ('id_note', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'NoteKfet',
            },
            bases=(cotisations.payment_methods.mixins.PaymentMethodMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('moyen', models.CharField(max_length=255, verbose_name='method')),
                ('available_for_everyone', models.BooleanField(default=False, verbose_name='is available for every user')),
                ('is_balance', models.BooleanField(default=False, editable=False, help_text='There should be only one balance payment method.', validators=[cotisations.validators.check_no_balance], verbose_name='is user balance')),
            ],
            options={
                'verbose_name': 'payment method',
                'verbose_name_plural': 'payment methods',
                'permissions': (('view_paiement', 'Can view a payment method object'), ('use_every_payment', 'Can use every payment method')),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Vente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='amount')),
                ('name', models.CharField(max_length=255, verbose_name='article')),
                ('prix', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='price')),
                ('duration', models.PositiveIntegerField(blank=True, null=True, verbose_name='duration (in months)')),
                ('type_cotisation', models.CharField(blank=True, choices=[('Connexion', 'Connection'), ('Adhesion', 'Membership'), ('All', 'Both of them')], max_length=255, null=True, verbose_name='subscription type')),
            ],
            options={
                'verbose_name': 'purchase',
                'verbose_name_plural': 'purchases',
                'permissions': (('view_vente', 'Can view a purchase object'), ('change_all_vente', 'Can edit all the previous purchases')),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CustomInvoice',
            fields=[
                ('baseinvoice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cotisations.BaseInvoice')),
                ('recipient', models.CharField(max_length=255, verbose_name='Recipient')),
                ('payment', models.CharField(max_length=255, verbose_name='Payment type')),
                ('address', models.CharField(max_length=255, verbose_name='Address')),
                ('paid', models.BooleanField(default=False, verbose_name='Paid')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='Remark')),
            ],
            options={
                'permissions': (('view_custominvoice', 'Can view a custom invoice object'),),
            },
            bases=('cotisations.baseinvoice',),
        ),
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('baseinvoice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cotisations.BaseInvoice')),
                ('cheque', models.CharField(blank=True, max_length=255, verbose_name='cheque number')),
                ('valid', models.BooleanField(default=False, verbose_name='validated')),
                ('control', models.BooleanField(default=False, verbose_name='controlled')),
                ('banque', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cotisations.Banque')),
                ('paiement', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cotisations.Paiement')),
            ],
            options={
                'verbose_name': 'invoice',
                'verbose_name_plural': 'invoices',
                'permissions': (('change_facture_control', 'Can edit the "controlled" state'), ('view_facture', 'Can view an invoice object'), ('change_all_facture', 'Can edit all the previous invoices')),
                'abstract': False,
            },
            bases=('cotisations.baseinvoice',),
        ),
        migrations.AddField(
            model_name='vente',
            name='facture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cotisations.BaseInvoice', verbose_name='invoice'),
        ),
        migrations.AddField(
            model_name='notepayment',
            name='payment',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='payment_method', to='cotisations.Paiement'),
        ),
        migrations.AddField(
            model_name='cotisation',
            name='vente',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='cotisations.Vente', verbose_name='purchase'),
        ),
        migrations.AddField(
            model_name='comnpaypayment',
            name='payment',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='payment_method', to='cotisations.Paiement'),
        ),
        migrations.AddField(
            model_name='chequepayment',
            name='payment',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='payment_method', to='cotisations.Paiement'),
        ),
        migrations.AddField(
            model_name='balancepayment',
            name='payment',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='payment_method', to='cotisations.Paiement'),
        ),
        migrations.CreateModel(
            name='CostEstimate',
            fields=[
                ('custominvoice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cotisations.CustomInvoice')),
                ('validity', models.DurationField(help_text='DD HH:MM:SS', verbose_name='Period of validity')),
            ],
            options={
                'permissions': (('view_costestimate', 'Can view a cost estimate object'),),
            },
            bases=('cotisations.custominvoice',),
        ),
    ]
