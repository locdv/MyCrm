from django.db import models
from django.utils.translation import ugettext_lazy as _
from common.utils import COUNTRIES, ROLES
from django.contrib.auth.models import User
import time

# Create your models here.


def img_url(self, filename):
    """
        trả về đường dẫn tới ảnh đại diện
    """
    hash_ = int(time.time())
    return "%s/%s/%s" % ("profile_pics", hash_, filename)


class Address(models.Model):
    """    thông tin của Address
        address_line: tên đường
        street: tên phố:
        city: tên thành phố
        state: tên bang
        postcode: mã vùng
        country: tên đất nước
    """
    
    address_line = models.CharField(_("Address"), max_length=255, blank=True, null=True)
    street = models.CharField(_("Street"), max_length=55, blank=True, null=True)
    city = models.CharField(_("City"), max_length=255, blank=True, null=True)
    state = models.CharField(_("State"), max_length=255, blank=True, null=True)
    postcode = models.CharField(_("Post/Zip-code"), max_length=64, blank=True, null=True)
    contry = models.CharField(max_length=3, choices=COUNTRIES, blank=True, null=True)
    def __str__(self):
        return self.city if self.city else ""

class Team(models.Model):
    """
        thông tin của Team
        name: tên Team
        members: các thành viên của team. Mỗi team có thể có nhiều member
        mỗi member có thể thuộc nhiều team. Vì vậy quan hệ giữa Team và User là ManyToMany


    """

    name = models.CharField(max_length=55)
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class Comment(models.Model):
    """
        Thông tin của Comment
        case: comment cho case nào.
        comment: nội dung comment 
        commented_on: thời gian bắt đầu comment. Giá trị được tính tự động
        commented_by: người comment. mỗi user có thể tạo nhiều comment. vì vậy quan hê.
        Many-to-one
        account: account được comment
        lead: lead được comment
        opportunity: opportunity được comment
        contact: contact được comment
    """
    case = models.ForeignKey('cases.Case', blank=True, null=True, related_name="cases", on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    commented_on = models.DateTimeField(auto_now_add=True)
    commented_by = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    account = models.ForeignKey('accounts.Account', blank=True, null=True,
                                related_name="accounts_comments", on_delete=models.CASCADE)
    lead = models.ForeignKey('leads.Lead', blank=True, null=True,
                             related_name="leads", on_delete=models.CASCADE)
    opportunity = models.ForeignKey('opportunity.Opportunity', blank=True,
                                    null=True, related_name="opportunity_comments", on_delete=models.CASCADE)
    contact = models.ForeignKey('contacts.Contact', blank=True, null=True,
                                related_name="contacts_comments", on_delete=models.CASCADE)

    def get_files(self):
        """
            Query comment file bởi comment
        """
        return Comment_Files.object.filter(comment_id=self)


class Comment_Files(models.Model):
    """"
    File comment
    attribute thông tin
    comment: đối tượng comment. Mỗi comment có thể có nhiều comment_files. vì vậy quan hệ many-to-one
    updated_on: thời gian file được cập nhật
    comment_file: file chứa nội dung comment

    """
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(auto_now_add=True)
    comment_file = models.FileField(
        "File", upload_to="comment_file", default='')

    def get_file_name(self):
        if self.comment_file:
            return self.comment_file.path.split('/')[-1]
        else:
            return None


class Attachments(models.Model):
    """
    Thông tin attachment
    created_by: user tạo attachment
    file_name: tên attach
    attachment: file được attach
    lead: lead được attach
    account: account được attach
    contact: contact được attach
    opportunity: opportunity được attach


    """
    created_by = models.ForeignKey(
        User, related_name='attached_created_by', on_delete=models.CASCADE)
    file_name = models.CharField(max_length=60)
    created_on = models.DateTimeField(_("Created on"), auto_now_add=True)
    attachment = models.FileField(
        max_length=1001, upload_to='attachments/%Y/%m/')
    lead = models.ForeignKey('leads.Lead', null=True, blank=True,
                             related_name='lead_attachment', on_delete=models.CASCADE)
    account = models.ForeignKey('accounts.Account', null=True, blank=True,
                                related_name='account_attachment', on_delete=models.CASCADE)
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE,
                                related_name='contact_attachment', blank=True, null=True)
    opportunity = models.ForeignKey(
        'opportunity.Opportunity', blank=True, null=True, related_name='opportinuty_attachment', on_delete=models.CASCADE)
