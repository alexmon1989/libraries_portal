from django.contrib import admin
from .models import Document, DocumentType, AnotherPerson, Rubric, DocumentStatus


class DocumentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentType)
admin.site.register(DocumentStatus)
admin.site.register(AnotherPerson)
admin.site.register(Rubric)
