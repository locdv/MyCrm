from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User

from leads.models import Lead
from contacts.models import Contact
from common.models import Team

from common.utils import EVENT_PARENT_TYPE, EVENT_STATUS
# Create your models here.

class Reminder(models.Model):
    """
    thông tin Reminder
    reminder_type: loại reminder
    reminder_time: thời gian bắt đầu reminder.
    """
    reminder_type = models.CharField(max_length=5, blank=True, null=True)
    reminder_time = models.IntegerField(pgettext_lazy("time of the reminder to evenet in Seconds", "Reminder"), blank=True, null=True)
    def __str__(self):
        return self.reminder_type


class Event(models.Model):  
    """
    thông tin event
    limit: giới hạn đối tượng có event
    name: tên event
    event_type: loại event
    content_type: loại content. Là 1 trong 4 giá trị của limit
    object_id: id của event
    parent: đối tượng parent của event. this is account, lead, opportunity, case
    status: trạng thái của event: giá trị enum: EVENT_STATUS
    direction: chỉ dẫn liên quan event
    start_date: ngày bắt đầu event
    close_date: ngày kết thúc
    duration: thời gian kéo dài event
    reminders: reminder cho event
    priority: mức độ ưu tiên của even
    updated_on: thời điểm cập nhật event
    updated_by: user cập nhật event
    attendees_user: user tham dự event
    attendees_contacts: contacts được mời tham gia
    attendees_leads: leads được mời tham gia
    created_on: thời gian tạo event
    created_by: user tạo event
    assigned_to: user chịu trách nhiệm
    team: team chịu trách nhiệm
    description: mô tả event
    is_active: trạng thái event
    """
    limit = models.Q(app_label='account', models='Account', id=10) | \
        models.Q(app_label='leads', model='Lead', id=13) | \
        models.Q(app_label='opportunity', model='Opportunity', id=14) | \
        models.Q(app_label='cases', model='Case', id=11)
    name = models.CharField(pgettext_lazy("Name of the Event", "Event"), max_length=64)
    event_type = models.CharField(_("Type of the event"), max_length=7)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True, limit_choices_to=limit, choices=EVENT_PARENT_TYPE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    parent = GenericForeignKey('content_type', 'object_id')
    status = models.CharField(pgettext_lazy("status of the Event", "Status"), choices=EVENT_STATUS, max_length=64, blank=True)
    direction = models.CharField(max_length=20, blank=True)
    start_date = models.DateTimeField(default=None)
    close_date = models.DateTimeField(default=None, null=True)
    duration = models.IntegerField(pgettext_lazy("Duration of the Event in Second", "Duration"), default=None, null=True)
    reminders = models.ManyToManyField(Reminder, blank=True)
    priority = models.CharField(max_length=10, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='updated_user')
    attendees_user = models.ManyToManyField(User, blank=True,
                                            related_name='attendees_user')
    attendees_contacts = models.ManyToManyField(Contact, blank=True,
                                                related_name='attendees_contact')
    attendees_leads = models.ManyToManyField(Lead, blank=True,
                                             related_name='attendees_lead')
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='event_created_by', on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(User, blank=True, related_name='event_assigned_user')
    team = models.ManyToManyField(Team, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name