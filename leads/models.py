from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from accounts.models import Account
from common.models import  Address, Team
from common.utils import LEAD_STATUS, LEAD_SOURCE
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Lead(models.Model):
    """
    thông tin về Lead
    title: tiêu đề về lead
    first_name: tên thật của Lead
    last_name: tên họ của Lead
    email: địa chỉ email
    phone: số điện thoại
    account: account liên quan đến lead. một account có thể có nhiều lead. quan hệ ở đây là many-to-one
    status: trạng thái của lead. giá trị kiểu enum  LEAD_STATUS
    source: nguồn gốc của Lead. nguồn gốc biết đến Lead
    address: địa chỉ của Lead. Nhiều lead có thể có cùng địa chỉ. Quan hệ many-to-one
    website: địa chỉ trang web của liên quan Lead
    description: mô tả về lead
    assigned_to: User được phân công Lead
    teams: team được phân công Lead
    account_name: tên account liên quan lead.
    opportunity_amount:
    created_by: user tạo lead
    created_on: thời gian tạo lead
    is_active: trạng thái của lead
    enquery_type: kiểu yêu cầu của lead
    """
    title = models.CharField(pgettext_lazy("Treatment Pronouns for the customer", "Title"), max_length=64, blank=True, null=True)
    first_name = models.CharField(("First name"), max_length=255)
    last_name = models.CharField(("Last name"), max_length=255)
    email = models.EmailField()
    phone = PhoneNumberField(null=True, blank=True)
    account = models.ForeignKey(Account, related_name='Leads', on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(_("Status of Lead"), max_length=255, blank=True, null=True, choices=LEAD_STATUS)
    source = models.CharField(_("Source of Lead"), max_length=255, blank=True, null=True, choices=LEAD_SOURCE)
    address = models.ForeignKey(Address, related_name='leadaddress', on_delete=models.CASCADE, blank=True, null=True)
    website = models.CharField(_("Website"), max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ManyToManyField(User, related_name='lead_assigned_users')
    teams = models.ManyToManyField(Team)
    account_name = models.CharField(max_length=255, null=True, blank=True)
    opportunity_amount = models.DecimalField(_("Opportunity Amount"), decimal_places=2, max_digits=12, blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='lead_created_by', on_delete=models.CASCADE)
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    is_active = models.BooleanField(default=True)
    enquery_type = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering  = ['-created_on']

    def __str__(self):
        return self.first_name + self.last_name