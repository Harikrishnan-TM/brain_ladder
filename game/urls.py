from django.urls import path
from . import views


from django.contrib.auth import views as auth_views




urlpatterns = [
    path('start/', views.start_game, name='start_game'),
    path('play/', views.play_level, name='play_level'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('payout/', views.payout_request, name='payout_request'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('game-over/', views.game_over, name='game_over'),
    path('wallet/add-fund/', views.add_fund, name='add_fund'),
    #path('add-funds/', AddFundsView.as_view(), name='add_fund'),
    path('add-funds/', views.add_fund, name='add_fund'),
    #path('payment-success/', payment_success, name='payment_success'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('submit-kyc/', views.submit_kyc, name='submit_kyc'),
    path('payout-status/', views.payout_status, name='payout_status'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='game/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),



]
