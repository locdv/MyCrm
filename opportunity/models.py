from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from common.utils import    STAGES, CURRENCY_CODES, SOURCES
from accounts.models import Account
from contacts.models import Contact
from common.models import Team



# Create your models here.


class Opportunity(models.Model):
    """
    name: tên của opportunity
    account: account liên quan đến opportunity. Mỗi account có thể có nhiều opportunity. Quan hệ many-to-one
    stage: giai đoạn của opportunity
    currency: loại tiền tệ
    amount: giá trị tiền của opportunity
    lead_source: nguồn gốc của lead liên quan đến opportunity
    propability: xác suất thành công của opportunity
    contacts: contacts liên quan. Quan hệ many-to-many
    closed_by: user đóng opportunity
    closed_on: thời gian đóng
    description: mô tả về opportunity
    assigned_to: user được phân công.
    teams: team được phân công
    created_by: user tạo opportunity
    created_on: thời gian tạo
    is_active: trạng thái của opportunity




    """
    name = models.CharField(pgettext_lazy("Name of Opportunity", "Name"), max_length=64)
    account = models.ForeignKey(Account, related_name='opportunity', on_delete=models.CASCADE, blank=True, null=True)
    stage = models.CharField(
        pgettext_lazy("Stage of Opportunity", "Stage"), max_length=64, choices=STAGES
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CODES, blank=True, null=True)
    amount = models.DecimalField(_("Opportunity Amount"), decimal_places=2, max_digits=12, blank=True, null=True)
    lead_source = models.CharField(_("Source of Lead"), max_length=255, choices=SOURCES, blank=True, null=True)
    probability = models.IntegerField(default=0, blank=True, null=True)
    contacts = models.ManyToManyField(Contact)
    closed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    closed_on = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ManyToManyField(User, related_name='opportunity_assigned_to')
    teams = models.ManyToManyField(Team)
    created_by = models.ForeignKey(User, related_name='opportunity_created_by', on_delete=models.CASCADE, blank=True, null=True)
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.name


