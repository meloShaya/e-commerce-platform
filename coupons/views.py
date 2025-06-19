from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Coupon
from .forms import CouponApplyForm

# Create your views here.
def coupon_apply(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST or None)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code=code, valid_from__lte=now, valid_to__gte=now, active=True)
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            form.add_error('code', 'This coupon is not valid or does not exist.')
    return redirect('cart:cart_detail')
