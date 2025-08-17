from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.conf import settings
import json
from django.http import JsonResponse
import random
from .models import KYC
from .forms import KYCForm

from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile

from .models import Wallet


from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, date
from .models import PayoutRequest, User
import calendar








from .models import PayoutRequest

from .models import (
    Question,
    GameSession,
    Answer,
    Wallet,
    PlayWallet,
    PayoutRequest
)

# New reward structure based on total correct answers
REWARD_BY_CORRECT_COUNT = {
    0: 0,
    1: 0,
    2: 20,
    3: 40,
    4: 60,
    5: 120,
}

from django.shortcuts import render

def home(request):
    # Get top wallets ordered by balance (top earners with balance > 0)
    top_wallets = Wallet.objects.select_related('user').filter(
        balance__gt=0
    ).order_by('-balance')[:8]
    
    context = {
        'top_wallets': top_wallets,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

def refund_policy(request):
    return render(request, 'refund.html')

def privacy_policy(request):
    return render(request, 'privacy.html')

def terms(request):
    return render(request, 'terms.html')

@login_required
def start_game(request):
    play_wallet, _ = PlayWallet.objects.get_or_create(user=request.user)

    if play_wallet.balance < 20:
        messages.error(request, "⚠️ You need at least ₹20 in your Play Wallet to start a game.")
        return redirect('add_fund')

    # Deduct ₹20 to start the game
    play_wallet.balance -= Decimal('20')
    play_wallet.save()

    session = GameSession.objects.create(user=request.user)
    return redirect('play_level')

@login_required
def play_level(request):
    session = GameSession.objects.filter(user=request.user, is_active=True).last()
    if not session or session.current_level > 5:
        messages.error(request, "No active game.")
        return redirect('start_game')

    #question = Question.objects.filter(level=session.current_level).first()
    questions = list(Question.objects.filter(level=session.current_level))
    question = random.choice(questions) if questions else None

    if request.method == 'POST':
        user_answer = request.POST.get('answer', '').strip()

        is_correct = (
            user_answer and user_answer != "__timeout__" and
            user_answer.lower() == question.correct_answer.strip().lower()
        )

        # Save answer attempt
        Answer.objects.create(
            session=session,
            question=question,
            user_answer=user_answer,
            is_correct=is_correct
        )

        if is_correct:
            session.current_level += 1
            if session.current_level > 5:
                session.is_active = False

                # Game completed — calculate reward
                correct_count = Answer.objects.filter(session=session, is_correct=True).count()
                session.earned_reward = Decimal(REWARD_BY_CORRECT_COUNT.get(correct_count, 0))
                session.save()

                messages.success(request, f"🎉 You completed all levels! You earned ₹{session.earned_reward}.")
                return redirect('game_over')
            else:
                session.save()
                messages.success(request, "✅ Correct! Proceeding to next level.")
                return redirect('play_level')

        else:
            # Game ends on wrong answer
            session.is_active = False
            correct_count = Answer.objects.filter(session=session, is_correct=True).count()
            session.earned_reward = Decimal(REWARD_BY_CORRECT_COUNT.get(correct_count, 0))
            session.save()

            if user_answer == "__timeout__":
                messages.error(request, f"⏰ Time’s up! You earned ₹{session.earned_reward}.")
            else:
                messages.error(request, f"❌ Wrong answer. You earned ₹{session.earned_reward}.")
            return redirect('game_over')

    return render(request, 'game/level.html', {
        'question': question,
        'level': session.current_level
    })

@login_required
def wallet_view(request):
    reward_wallet, _ = Wallet.objects.get_or_create(user=request.user)
    play_wallet, _ = PlayWallet.objects.get_or_create(user=request.user)
    return render(request, 'game/wallet.html', {
        'wallet': reward_wallet,
        'play_wallet': play_wallet
    })

@login_required
def payout_request(request):
    # ✅ Check KYC submission
    try:
        kyc = request.user.kyc
    except KYC.DoesNotExist:
        return redirect('submit_kyc')

    if not kyc.full_name or not kyc.pan_number or not kyc.aadhaar_number:
        return redirect('submit_kyc')

    # ✅ Continue with payout logic
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount'))
            upi_id = request.POST.get('upi_id')

            if amount <= 0:
                messages.error(request, "Amount must be positive.")
            elif amount > wallet.balance:
                messages.error(request, "Insufficient wallet balance.")
            else:
                PayoutRequest.objects.create(user=request.user, amount=amount, upi_id=upi_id)
                wallet.balance -= amount
                wallet.save()
                messages.success(request, "Payout request submitted.")
        except (InvalidOperation, ValueError):
            messages.error(request, "Invalid amount entered.")

        return redirect('wallet')

    return render(request, 'game/payout.html', {'wallet': wallet})

@login_required
def leaderboard_view(request):
    leaders = Wallet.objects.select_related('user').order_by('-balance')[:10]
    return render(request, 'game/leaderboard.html', {'leaders': leaders})

@login_required
def game_over(request):
    session = GameSession.objects.filter(user=request.user).last()

    # Add reward to reward wallet
    if session and not session.is_active:
        reward_wallet, _ = Wallet.objects.get_or_create(user=request.user)
        reward_wallet.balance += Decimal(session.earned_reward)
        reward_wallet.save()

    return render(request, 'game/game_over.html', {
        'session': session
    })

@login_required
def add_fund(request):
    play_wallet, _ = PlayWallet.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', 0))
            if amount > 0:
                import razorpay
                from django.conf import settings

                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                amount_paise = amount * 100  # Razorpay uses paise

                razorpay_order = client.order.create({
                    "amount": amount_paise,
                    "currency": "INR",
                    "payment_capture": "1"
                })

                request.session['order_amount'] = amount
                request.session['order_id'] = razorpay_order['id']

                return render(request, 'game/razorpay_checkout.html', {
                    'order_id': razorpay_order['id'],
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'amount': amount_paise,
                    'currency': 'INR'
                })
            else:
                messages.error(request, "Amount must be greater than 0.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")

        return redirect('wallet')

    return render(request, 'game/add_fund.html', {'play_wallet': play_wallet})

@csrf_exempt
@login_required
def payment_success(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = request.session.get('order_id')
        amount = request.session.get('order_amount')

        if order_id and amount:
            play_wallet, _ = PlayWallet.objects.get_or_create(user=request.user)
            play_wallet.balance += Decimal(amount)
            play_wallet.save()

            # Clear session
            del request.session['order_id']
            del request.session['order_amount']

            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'failed', 'reason': 'missing session data'})


# In views.py
  # You'll create this in step 4

@login_required
def submit_kyc(request):
    kyc, created = KYC.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = KYCForm(request.POST, request.FILES, instance=kyc)  # ✅ include request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, "✅ KYC submitted successfully.")
            return redirect('wallet')
    else:
        form = KYCForm(instance=kyc)

    return render(request, 'game/kyc_form.html', {'form': form})



@login_required
def payout_status(request):
    payouts = PayoutRequest.objects.filter(user=request.user).order_by('-requested_at')

    try:
        user_message = request.user.userprofile.payout_message
    except UserProfile.DoesNotExist:
        user_message = ""

    return render(request, 'game/payout_status.html', {
        'payouts': payouts,
        'user_message': user_message
    })



def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '🎉 Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'game/signup.html', {'form': form})


#payout tracking page

def is_admin_or_staff(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin_or_staff)
def financial_year_payouts(request):
    # Get current financial year (April to March in India)
    today = date.today()
    if today.month >= 4:  # April onwards
        fy_start = date(today.year, 4, 1)
        fy_end = date(today.year + 1, 3, 31)
        financial_year = f"FY {today.year}-{str(today.year + 1)[2:]}"
        current_fy_year = today.year
    else:  # January to March
        fy_start = date(today.year - 1, 4, 1)
        fy_end = date(today.year, 3, 31)
        financial_year = f"FY {today.year - 1}-{str(today.year)[2:]}"
        current_fy_year = today.year - 1
    
    # Allow selection of different financial years
    selected_year = request.GET.get('year')
    if selected_year:
        try:
            year = int(selected_year)
            fy_start = date(year, 4, 1)
            fy_end = date(year + 1, 3, 31)
            financial_year = f"FY {year}-{str(year + 1)[2:]}"
        except ValueError:
            pass
    
    # TDS threshold amount (₹20,000 per user per FY)
    TDS_THRESHOLD = 20000
    
    # Get user-wise payout data for TDS tracking
    user_payouts = PayoutRequest.objects.filter(
        is_paid=True,
        requested_at__date__gte=fy_start,
        requested_at__date__lte=fy_end
    ).values(
        'user__id',
        'user__username', 
        'user__first_name', 
        'user__last_name',
        'user__email'
    ).annotate(
        total_amount=Sum('amount'),
        total_requests=Count('id')
    ).order_by('-total_amount')
    
    # Categorize users for TDS
    tds_applicable_users = []
    below_threshold_users = []
    
    for user in user_payouts:
        user['needs_tds'] = user['total_amount'] >= TDS_THRESHOLD
        user['tds_amount'] = user['total_amount'] * 0.1 if user['needs_tds'] else 0  # 10% TDS
        user['amount_after_tds'] = user['total_amount'] - user['tds_amount']
        
        if user['needs_tds']:
            tds_applicable_users.append(user)
        else:
            below_threshold_users.append(user)
    
    # Overall statistics
    total_paid_amount = sum(user['total_amount'] for user in user_payouts)
    total_tds_amount = sum(user['tds_amount'] for user in tds_applicable_users)
    total_users_with_payouts = len(user_payouts)
    users_requiring_tds = len(tds_applicable_users)
    
    # Monthly TDS breakdown
    monthly_tds_data = []
    for month in range(4, 16):  # April (4) to March (15, which is 3 of next year)
        if month > 12:
            actual_month = month - 12
            year_for_month = fy_start.year + 1
        else:
            actual_month = month
            year_for_month = fy_start.year
        
        month_start = date(year_for_month, actual_month, 1)
        month_end = date(year_for_month, actual_month, calendar.monthrange(year_for_month, actual_month)[1])
        
        monthly_users = PayoutRequest.objects.filter(
            is_paid=True,
            requested_at__date__gte=month_start,
            requested_at__date__lte=month_end
        ).values('user__id').annotate(
            monthly_total=Sum('amount')
        )
        
        # Check how many users crossed threshold in this month (cumulative)
        users_above_threshold = 0
        monthly_tds = 0
        monthly_amount = 0
        
        for user_data in monthly_users:
            user_id = user_data['user__id']
            # Get cumulative amount till this month
            cumulative_amount = PayoutRequest.objects.filter(
                user__id=user_id,
                is_paid=True,
                requested_at__date__gte=fy_start,
                requested_at__date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_amount += user_data['monthly_total']
            
            if cumulative_amount >= TDS_THRESHOLD:
                users_above_threshold += 1
                monthly_tds += user_data['monthly_total'] * 0.1
        
        monthly_tds_data.append({
            'month': calendar.month_name[actual_month],
            'year': year_for_month,
            'amount': monthly_amount,
            'users_above_threshold': users_above_threshold,
            'tds_amount': monthly_tds,
        })
    
    # Generate list of available financial years (last 5 years)
    available_years = []
    for i in range(5):
        year = current_fy_year - i
        available_years.append({
            'year': year,
            'display': f"FY {year}-{str(year + 1)[2:]}"
        })
    
    context = {
        'financial_year': financial_year,
        'fy_start': fy_start,
        'fy_end': fy_end,
        'tds_threshold': TDS_THRESHOLD,
        'tds_applicable_users': tds_applicable_users,
        'below_threshold_users': below_threshold_users,
        'total_paid_amount': total_paid_amount,
        'total_tds_amount': total_tds_amount,
        'total_users_with_payouts': total_users_with_payouts,
        'users_requiring_tds': users_requiring_tds,
        'monthly_tds_data': monthly_tds_data,
        'available_years': available_years,
        'selected_year': selected_year or current_fy_year,
    }
    
    return render(request, 'game/financial_year_payouts.html', context)