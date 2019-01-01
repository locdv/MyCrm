from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from accounts.models import Account
from common.models import Address, Team
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Contact(models.Model):
    """
    thông tin của Contact
    first_name: tên thật của 


    """
    first_name =  models.CharField(_("First name"), max_length=255)
    last_name = models.CharField(_("Last name"), max_length=255)
    account = models.ForeignKey(Account, related_name='lead_account_contacts', on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(null=True, unique=True)
    address = models.ForeignKey(Address, related_name='address_contacts', on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ManyToManyField(User, related_name='contact_assigned_users')
    teams = models.ManyToManyField(Team)
    created_by = models.ForeignKey(User, related_name='contact_created_by', on_delete=models.CASCADE, blank=True, null=True)
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name

    class Meta:
        unique_together = (("email", ),)