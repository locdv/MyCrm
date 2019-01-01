from django.db import models
from datetime import datetime
# Create your models here.
class Email(models.Model):
    """
    thông tin email
    from_email: địa chỉ email của người gửi
    to_email: địa chỉ email của người nhận
    subject: tiêu đề của email
    message: nội dung email
    file: file được đính kèm trong email
    send_time: thời gian gửi email
    status: trạng thái của email
    important: mức độ quan trọng của email

    """
    from_email = models.EmailField(max_length=200)
    to_email = models.EmailField(max_length=200)
    subject = models.CharField(max_length=200)
    message = models.CharField(max_length=200)
    file = models.FileField(null=True, upload_to="files/")
    send_time = models.DateTimeField(default=datetime.now)
    status = models.CharField(max_length=200, default="sent")
    important = models.BooleanField(max_length=10, default=False)

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ['-id']
