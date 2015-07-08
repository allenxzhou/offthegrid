# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('date', models.DateField(verbose_name=b'Event date')),
                ('start', models.TimeField(verbose_name=b'Event start time')),
                ('end', models.TimeField(verbose_name=b'Event end time')),
                ('location', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Event_Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event', models.ForeignKey(to='events.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='event_vendor',
            name='vendor',
            field=models.ForeignKey(to='events.Vendor'),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('name', 'date')]),
        ),
        migrations.AlterUniqueTogether(
            name='event_vendor',
            unique_together=set([('event', 'vendor')]),
        ),
    ]
