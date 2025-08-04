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
    return render(request, 'home.html')


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
        form = KYCForm(request.POST, instance=kyc)
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
    return render(request, 'game/payout_status.html', {'payouts': payouts})



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
