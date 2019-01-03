"""
Case: thông tin của một task.

"""

from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from common.utils import    CASE_TYPE, PRIORITY_CHOICE, STATUS_CHOICE
from accounts.models import Account
from contacts.models import Contact
from common.models import Team
from planner.models import Event

# Create your models here.
class Case(models.Model):
    """
        Thông tin về Case (một task)
        name: tên case
        status: trạng thái của case. Là giá trị kiểu enum: STATUS_CHOICE
        priority: mực độ ưu tiên của case
        case_type: phân loại case: giá trị kiểu enum: CASE_TYPE
        account: account liên quan tới case. một accout có thể có nhiều case. vì vậy quan hệ ở đây là many-to-one
        contacts: contacts liên quan tới case. một contact có thể có nhiều case. một case có thể liên quan nhiều contact. Quan hệ
        ở đây là many-to-many
        closed_on: thời gian case được đóng
        description: mô tả thêm về case
        assigned_to: user được phân công cho case. Một user có thể được giao nhiều case. Một case có thể được giao cho nhiều user. Vì
        vậy quan hệ ở đây là many-to-many
        teams: team liên quan đến case:Quan hệ many-to-many
        created_by: User tạo case. Một user có thể tạo nhiều case. Quan hệ many-to-one
        created_on: thời gian tạo case.
        is_active: trạng thái của case


    """
    name = models.CharField(pgettext_lazy("name of the case", "Name"), max_length=64)
    status = models.CharField(choices=STATUS_CHOICE, max_length=64)
    priority = models.CharField(choices=PRIORITY_CHOICE, max_length=64, blank=True, null=True)
    case_type = models.CharField(choices=CASE_TYPE, max_length=255, blank=True, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null = True)
    contacts = models.ManyToManyField(Contact)
    closed_on = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ManyToManyField(User, related_name='case_assigned_user')
    teams = models.ManyToManyField(Team)
    created_by = models.ForeignKey(User, related_name='case_created_by', on_delete=models.CASCADE, blank=True, null=True)
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']
    
    def __str__(self):
        return self.name

    def get_meetings(self):
        """
            get meeting event
        """
        content_type = ContentType.objects.get(app_label="cases", model="case")
        return Event.objects.filter(
            content_type=content_type, object_id=self.id, event_type="Meeting", status="Planned")

    def get_completed_meetings(self):
        # get cuộc họp đã hoàn thành
        content_type = ContentType.objects.get(app_label="cases", model="case")
        return Event.objects.filter(
            content_type=content_type, object_id=self.id, event_type="Meeting").exclude(status="Planned")

    def get_tasks(self):
        # get task đang trạng thái planned
        content_type = ContentType.objects.get(app_label="cases", model="case")
        return Event.objects.filter(content_type=content_type, object_id=self.id, event_type="Task", status="Planned")

    def get_completed_tasks(self):
        # get task đã hoàn thành
        content_type = ContentType.objects.get(app_label="cases", model="case")
        return Event.objects.filter(
            content_type=content_type, object_id=self.id, event_type="Task").exclude(status="Planned")

    def get_calls(self):
        # get cuộc gọi trạng thái planned
        content_type = ContentType.objects.get(app_label="cases", model="case")
        return Event.objects.filter(content_type=content_type, object_id=self.id, event_type="Call", status="Planned")

    def get_completed_calls(self):
        # get cuộc gọi đã hoàn thành
        content_type = ContentType.objects.get(app_label="cases", model="case")
        return Event.objects.filter(
            content_type=content_type, object_id=self.id, event_type="Call").exclude(status="Planned")

    def get_assigned_user(self):
        # get user được phân công task
        return User.objects.get(id=self.assigned_to.id)
