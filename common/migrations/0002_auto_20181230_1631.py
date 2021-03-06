# Generated by Django 2.1.4 on 2018-12-30 09:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('leads', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contacts', '0001_initial'),
        ('opportunity', '0001_initial'),
        ('accounts', '0002_auto_20181230_1631'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contacts_comments', to='contacts.Contact'),
        ),
        migrations.AddField(
            model_name='comment',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='leads', to='leads.Lead'),
        ),
        migrations.AddField(
            model_name='comment',
            name='opportunity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opportunity_comments', to='opportunity.Opportunity'),
        ),
        migrations.AddField(
            model_name='attachments',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='account_attachment', to='accounts.Account'),
        ),
        migrations.AddField(
            model_name='attachments',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contact_attachment', to='contacts.Contact'),
        ),
        migrations.AddField(
            model_name='attachments',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attached_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attachments',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lead_attachment', to='leads.Lead'),
        ),
        migrations.AddField(
            model_name='attachments',
            name='opportunity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opportinuty_attachment', to='opportunity.Opportunity'),
        ),
    ]
