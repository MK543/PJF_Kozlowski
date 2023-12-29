from django.contrib import admin

from app.models import Comment, Post, Profile, Tag, WebsiteMeta

# Register your models here.
admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(WebsiteMeta)