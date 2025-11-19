from django.contrib import admin
from .models import ZendeskProfile


@admin.register(ZendeskProfile)
class ZendeskAgentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'employee_id',
        'role',
        'country',
        'created_at',
    ]
    list_filter = [
        'role',
        'country',
        'created_at',
    ]
    search_fields = [
        'country',
        'user',
    ]
    readonly_fields = ['created_at']
    
