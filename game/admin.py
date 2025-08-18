from django.contrib import admin
from django.utils.html import format_html
from .models import Question, GameSession, Answer
from .models import PlayWallet
from .models import PayoutRequest, Wallet
from .models import UserProfile, KYC

# Register standard models
admin.site.register(Question)
admin.site.register(GameSession)
admin.site.register(Answer)
admin.site.register(PlayWallet)
admin.site.register(Wallet)

# PayoutRequest admin
@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'upi_id', 'is_paid', 'requested_at')
    list_filter = ('is_paid', 'requested_at')
    search_fields = ('user__username', 'upi_id')

# UserProfile admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'payout_message')
    search_fields = ('user__username',)

# KYC admin with image preview
@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "pan_number",
        "aadhaar_number",
        "is_verified",
        "image_tag",  # display uploaded Aadhaar image
    )
    search_fields = ("user__username", "pan_number", "aadhaar_number")
    list_filter = ("is_verified",)

    def image_tag(self, obj):
        if obj.aadhaar_front:  # make sure your KYC model has 'aadhaar_front'
            return format_html('<img src="{}" width="100" />', obj.aadhaar_front.url)
        return "-"
    image_tag.short_description = "KYC Image"
