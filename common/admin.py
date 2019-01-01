from django.contrib import admin
from common.models import Address, Team, Comment, Comment_Files, Attachments
# Register your models here.
admin.site.register(Address)
admin.site.register(Team)
admin.site.register(Attachments)
admin.site.register(Comment_Files)    
admin.site.register(Comment)