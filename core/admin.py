from django.contrib import admin
from .models import CGPARecord

# Register your models here.
# admin.py
@admin.register(CGPARecord)
class CGPARecordAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "semester",
        "cgpa",
        "total_units",
        "total_credit_points",
        "created_at",
    )
    list_filter = ("semester", "created_at")
    search_fields = ("user__username", "semester")
    ordering = ("-created_at",)