# Generated by Django 2.2 on 2019-06-15 03:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djstripe', '0004_auto_20190612_0850'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='business_logo',
        ),
        migrations.RemoveField(
            model_name='account',
            name='business_name',
        ),
        migrations.RemoveField(
            model_name='account',
            name='business_primary_color',
        ),
        migrations.RemoveField(
            model_name='account',
            name='business_url',
        ),
        migrations.RemoveField(
            model_name='account',
            name='debit_negative_balances',
        ),
        migrations.RemoveField(
            model_name='account',
            name='decline_charge_on',
        ),
        migrations.RemoveField(
            model_name='account',
            name='display_name',
        ),
        migrations.RemoveField(
            model_name='account',
            name='legal_entity',
        ),
        migrations.RemoveField(
            model_name='account',
            name='payout_schedule',
        ),
        migrations.RemoveField(
            model_name='account',
            name='payout_statement_descriptor',
        ),
        migrations.RemoveField(
            model_name='account',
            name='statement_descriptor',
        ),
        migrations.RemoveField(
            model_name='account',
            name='support_email',
        ),
        migrations.RemoveField(
            model_name='account',
            name='support_phone',
        ),
        migrations.RemoveField(
            model_name='account',
            name='support_url',
        ),
        migrations.RemoveField(
            model_name='account',
            name='timezone',
        ),
        migrations.RemoveField(
            model_name='account',
            name='verification',
        ),
    ]
