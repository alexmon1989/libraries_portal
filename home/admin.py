from django.contrib import admin
from .models import LibraryKind, LibraryType, Library, Region, City, Profile, LibraryDocument, LibraryRequestAccess
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin


class LibraryTypeAdmin(admin.ModelAdmin):
    model = LibraryType
    #filter_horizontal = ('authors',) #If you don't specify this, you will get a multiple select widget.


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    verbose_name = 'Профиль'


class ProfileAdmin(AuthUserAdmin):
    inlines = [ProfileInline]

    def get_formsets(self, request, obj=None):
        if not obj:
            return []
        return super(ProfileAdmin, self).get_formsets(request, obj)


class LibraryDocumentsInline(admin.StackedInline):
    model = LibraryDocument
    can_delete = True
    verbose_name_plural = 'Документы'
    verbose_name = 'Документ'


class LibraryAdmin(admin.ModelAdmin):
    inlines = [LibraryDocumentsInline]


admin.site.register(LibraryKind)
admin.site.register(LibraryType, LibraryTypeAdmin)
admin.site.register(Library, LibraryAdmin)
admin.site.register(LibraryRequestAccess)
admin.site.register(Region)
admin.site.register(City)
admin.site.unregister(User)
admin.site.register(User, ProfileAdmin)
