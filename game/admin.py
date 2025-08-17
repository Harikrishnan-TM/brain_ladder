from django.contrib import admin
from .models import Question, GameSession, Answer
from .models import PlayWallet
from .models import PayoutRequest, Wallet
from .models import UserProfile

admin.site.register(Question)
admin.site.register(GameSession)
admin.site.register(Answer)

admin.site.register(PlayWallet)

from .models import KYC

@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'upi_id', 'is_paid', 'requested_at')
    list_filter = ('is_paid', 'requested_at')
    search_fields = ('user__username', 'upi_id')

admin.site.register(Wallet)





@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'payout_message')
    search_fields = ('user__username',)


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "pan_number", "aadhaar_number", "is_verified")
    search_fields = ("user__username", "pan_number", "aadhaar_number")
    list_filter = ("is_verified",)