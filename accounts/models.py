"""
account: thông tin của khách hàng, đối tác. Account đại diện cho công ty.

"""
from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from common.utils import INDCHOICES
from common.models import Address, Team
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class Account(models.Model):
    """
        Thông tin về Account
        name: tên Account
        email: địa chỉ Email
        phone: số điện thoại liên lạc
        industry: lĩnh vực làm việc
        billing_address: địa chỉ hóa đơn
        shipping_address: địa chỉ ship hàng
        website: địa chỉ website của công ty
        description: mô tả thêm thông tin về Account
        assigned_to: User được phân công làm việc với Account
        teams: team liên quan đến Account
        created_by: User đã tạo account
        created_on: thời gian tạo account
        is_active: trạng thái của account

    """
    name = models.CharField(pgettext_lazy("Name of Account", "Name"), max_length=64)
    email = models.EmailField()
    phone = PhoneNumberField(null=True)
    industry = models.CharField(_("Industry Type"), max_length=255, choices=INDCHOICES, blank=True, null= True)
    billing_address = models.ForeignKey(Address, related_name='account_billing_address', blank=True, null=True, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, related_name='acount_shipping_address', on_delete=models.CASCADE, blank=True, null=True)
    website = models.URLField(_("Website"), blank=True, null = True)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ManyToManyField(User, related_name='account_assigned_to')
    teams = models.ManyToManyField(Team)
    created_by = models.ForeignKey(User, related_name='account_created_by', blank=True, null=True, on_delete=models.CASCADE)
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_on']


