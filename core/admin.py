from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DoctorStatus

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'username', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('email', 'name', 'username')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'role')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('name', 'email', 'role')}),
    )

@admin.register(DoctorStatus)
class DoctorStatusAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'is_online', 'last_seen')
    list_filter = ('is_online', 'last_seen')
    search_fields = ('doctor__name', 'doctor__email')
    readonly_fields = ('last_seen',)