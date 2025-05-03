from django.shortcuts import render,redirect,get_object_or_404
from .models import Apple,Cart,CustomerDetail,Order
from . forms import RegistrationForm,AuthenticateForm,ChangePasswordForm,UserProfileForm,AdminProfileForm,CustomerForm
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse
from .utils import render_with_cart  # Make sure this import is at the top
#================ Forgot Password ======================
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.http import HttpResponse
# views.py
from .utils import render_with_cart

# Create your views here.


def index(request):
    return render_with_cart(request, 'core/index.html')
#=====================================================================

def iphoneseries(request):
    return render(request,'core/iphoneseries.html')
#=====================================================================

def iphone_categories(request):
    ic = Apple.objects.filter(category='IPHONESERIES')
    for item in ic:
        try:
            discount = round(((item.original_price - item.discounted_price) / item.original_price) * 100)
        except (ZeroDivisionError, TypeError):
            discount = 0
        item.discount_percent = discount

    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()

    return render(request, 'core/iphone_categories.html', {'ic': ic, 'cart_count': cart_count})
#=====================================================================

def ipad_categories(request):
    ic = Apple.objects.filter(category='IPAD')
    for item in ic:
        try:
            discount = round(((item.original_price - item.discounted_price) / item.original_price) * 100)
        except (ZeroDivisionError, TypeError):
            discount = 0
        item.discount_percent = discount

    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()

    return render(request, 'core/ipad_categories.html', {'ic': ic, 'cart_count': cart_count})
#=====================================================================

def macbook_categories(request):
    macs = Apple.objects.filter(category='MACBOOKSERIES')

    for mac in macs:
        try:
            discount = round(((mac.original_price - mac.discounted_price) / mac.original_price) * 100)
        except (ZeroDivisionError, TypeError):
            discount = 0
        mac.discount_percent = discount 

    cart_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0


    return render(request, 'core/macbook_categories.html', {'macs': macs,'cart_count': cart_count})

#=====================================================================

def apple_details(request, id):
    ic = Apple.objects.get(pk=id)
    try:
        discount_percent = round(((ic.original_price - ic.discounted_price) / ic.original_price) * 100)
    except (ZeroDivisionError, TypeError):
        discount_percent = 0
    is_in_cart = False
    if request.user.is_authenticated:
        is_in_cart = Cart.objects.filter(user=request.user, product=ic).exists()
    return render_with_cart(request, 'core/apple_details.html', {
        'ic': ic,
        'is_in_cart': is_in_cart,
        'discount_percent': discount_percent
    })


#=====================================================================

def registration(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            mf = RegistrationForm(request.POST)
            if mf.is_valid():
                mf.save()
                return redirect('login')  
        else:
            mf = RegistrationForm()
        return render(request, 'core/registration.html', {'mf': mf})
    else:
        return redirect('profile')
#=====================================================================
def log_in(request):
    if not request.user.is_authenticated:  
        if request.method == 'POST':      
            mf = AuthenticateForm(request,request.POST)
            if mf.is_valid():
                name = mf.cleaned_data['username']
                pas = mf.cleaned_data['password']
                user = authenticate(username=name, password=pas)
                if user is not None:
                    login(request, user)
                    return redirect('/')
        else:
            mf = AuthenticateForm()
        return render(request,'core/login.html',{'mf':mf})
    else:
        return redirect('profile')
#=====================================================================
def profile(request):
    if request.user.is_authenticated:  # This check wheter user is login, if not it will redirect to login page
        if request.method == 'POST':
            if request.user.is_superuser == True:
                mf = AdminProfileForm(request.POST,instance=request.user)
            else:
                mf = UserProfileForm(request.POST,instance=request.user)
            if mf.is_valid():
                mf.save()
                messages.success(request,'Profile Updated Successfully !!')
        else:
            if request.user.is_superuser == True:
                mf = AdminProfileForm(instance=request.user)
            else:
                mf = UserProfileForm(instance=request.user)
        return render(request,'core/profile.html',{'name':request.user,'mf':mf})
    else:                                                # request.user returns the username
        return redirect('login')
#=====================================================================
def log_out(request):
    logout(request)
    return redirect('index')
#=====================================================================

def changepassword(request):                                       # Password Change Form               
    if request.user.is_authenticated:                              # Include old password 
        if request.method == 'POST':                               
            mf =ChangePasswordForm(request.user,request.POST)
            if mf.is_valid():
                mf.save()
                update_session_auth_hash(request,mf.user)
                return redirect('profile')
        else:
            mf = ChangePasswordForm(request.user)
        return render(request,'core/changepassword.html',{'mf':mf})
    else:
        return redirect('login')
    

#=====================Add to Cart=======================

def add_to_cart(request, id):
    if request.user.is_authenticated:
        apple = Apple.objects.get(pk=id)
        user = request.user
        cart_item, created = Cart.objects.get_or_create(user=user, product=apple)  # This will ensure only one instance per product
        messages.success(request, 'Added to cart successfully!')
        if created:
            return redirect('appledetails', id=id)  # Redirect to the product details page
        else:
            return redirect('viewcart')  # Optionally, redirect to the cart if item already exists
    else:
        return redirect('login')

#=====================================================================
def view_cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.product.discounted_price * item.quantity for item in cart_items)
        final_price = total + 0
        return render_with_cart(request, 'core/view_cart.html', {
            'cart_items': cart_items,
            'total': total,
            'final_price': final_price
        })
    else:
        return redirect('login')
#=====================================================================

def add_quantity(request, id):
    if request.user.is_authenticated:
        product = get_object_or_404(Cart, pk=id, user=request.user)

        # Check if quantity is less than or equal to 2
        if product.quantity < 2:
            product.quantity += 1
            product.save()
            messages.success(request, 'Quantity added successfully!')
        else:
            messages.error(request, 'Cannot add more products. You have reached the limit of 2 items per product.')
        return redirect('viewcart')
    else:
        return redirect('login')
#=====================================================================
def delete_quantity(request, id):
    if request.user.is_authenticated:
        product = get_object_or_404(Cart, pk=id, user=request.user)

        # Check if the quantity is more than 1
        if product.quantity > 1:
            product.quantity -= 1
            product.save()
            messages.success(request, 'Quantity decreased successfully!')
        else:
            messages.error(request, 'Cannot remove more products. The quantity is already at 1.')
        return redirect('viewcart')
    else:
        return redirect('login')


#=====================delete from cart==============

def delete_cart(request,id):
    apple_cart = Cart.objects.get(pk=id)
    apple_cart.delete()
    return redirect('viewcart')
#=====================================================================

def address(request):
    if request.method == 'POST':
            mf =CustomerForm(request.POST)
            if mf.is_valid():
                user=request.user                # user variable store the current user i.e steveroger
                name= mf.cleaned_data['name']
                address= mf.cleaned_data['address']
                city= mf.cleaned_data['city']
                state= mf.cleaned_data['state']
                pincode= mf.cleaned_data['pincode']  
                CustomerDetail(user=user,name=name,address=address,city=city,state=state,pincode=pincode).save()
                return redirect('address')           
    else:
        mf =CustomerForm()
        address = CustomerDetail.objects.filter(user=request.user)
    return render(request,'core/address.html',{'mf':mf,'address':address})

#=====================================================================
def delete_address(request,id):
        de = CustomerDetail.objects.get(pk=id)
        de.delete()
        return redirect('address')


# =====================Checkout Page================


def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = 0
    delivery_charge = 0

    # Process each cart item
    for item in cart_items:
        # Calculate the total price for this item in the cart
        item.product.price_and_quantity_total = item.product.discounted_price * item.quantity
        total += item.product.price_and_quantity_total

        # Decrease stock of the Apple product based on the quantity in the cart
        apple_product = item.product
        apple_product.stock -= item.quantity  # Decrease stock
        apple_product.save()

    final_price = delivery_charge + total
    address = CustomerDetail.objects.filter(user=request.user)

    return render(request, 'core/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'final_price': final_price,
        'address': address
    })
#=====================================================================

def payment(request):

    if request.method=='POST':
        selected_address_id = request.POST.get('selected_address')
        print('=========',selected_address_id)
    cart_items = Cart.objects.filter(user=request.user)      # cart_items will fetch product of current user, and show product available in the cart of the current user.
    total =0
    delivery_charge =0
    for item in cart_items:
        item.product.price_and_quantity_total = item.product.discounted_price * item.quantity
        total += item.product.price_and_quantity_total
    final_price= delivery_charge + total
    
    address = CustomerDetail.objects.filter(user=request.user)

    #================= Paypal Code =====================
   
    host = request.get_host()   # Will fecth the domain site is currently hosted on.
   
    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,   #This is typically the email address associated with the PayPal account that will receive the payment.
        'amount': final_price,    #: The amount of money to be charged for the transaction. 
        'item_name': 'Apple',       # Describes the item being purchased.
        'invoice': uuid.uuid4(),  #A unique identifier for the invoice. It uses uuid.uuid4() to generate a random UUID.
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",         #The URL where PayPal will send Instant Payment Notifications (IPN) to notify the merchant about payment-related events
        'return_url': f"http://{host}{reverse('paymentsuccess',args=[selected_address_id])}",     #The URL where the customer will be redirected after a successful payment. 
        'cancel_url': f"http://{host}{reverse('paymentfailed')}",      #The URL where the customer will be redirected if they choose to cancel the payment. 
    }

    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

    #================= Paypal Code  End =====================

    return render(request, 'core/payment.html', {'final_price':final_price,'address':address,'paypal':paypal_payment})
#=====================================================================
def payment_success(request,selected_address_id):
    user = request.user
    address_data = CustomerDetail.objects.get(pk=selected_address_id)
    cart = Cart.objects.filter(user=request.user)
    for cart in cart:
        Order(user=user,customer=address_data,quantity=cart.quantity,apple=cart.product).save()
        cart.delete()
    return render(request,'core/payment_success.html')
#=====================================================================
def payment_failed(request):
    return render(request,'core/payment_failed.html')
#=====================================================================

def order(request):
    ord = Order.objects.filter(user=request.user)
    return render(request,'core/order.html',{'ord':ord})


    #========================================== Buy Now ========================================================

def buynow(request, id):
    if not request.user.is_authenticated:
        # Redirect to login page with next parameter
        return redirect('login')
    
    apple = get_object_or_404(Apple, pk=id)

    if apple.stock < 1:
        return render(request, 'core/buynow.html', {
            'error': f"Sorry, {apple.name} is out of stock.",
            'apple': apple
        })


    apple.stock -= 1
    apple.save()

    delivery_charge = 0  
    final_price = delivery_charge + apple.discounted_price

    address = CustomerDetail.objects.filter(user=request.user)

    return render(request, 'core/buynow.html', {
        'final_price': final_price,
        'address': address,
        'apple': apple
    })


def buynow_payment(request,id):

    if request.method == 'POST':
        selected_address_id = request.POST.get('buynow_selected_address')

    apple = Apple.objects.get(pk=id)     # cart_items will fetch product of current user, and show product available in the cart of the current user.
    delivery_charge =0
    final_price= delivery_charge + apple.discounted_price
    
    address = CustomerDetail.objects.filter(user=request.user)

#================= Paypal Code ======================================

    host = request.get_host()   # Will fecth the domain site is currently hosted on.

    paypal_checkout = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': final_price,
        'item_name': 'Apple',
        'invoice': uuid.uuid4(),
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('buynowpaymentsuccess', args=[selected_address_id,id])}",
        'cancel_url': f"http://{host}{reverse('paymentfailed')}",
    }

    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

    #========================================================================

    return render(request, 'core/payment.html', {'final_price':final_price,'address':address,'apple':apple,'paypal':paypal_payment})

def buynow_payment_success(request,selected_address_id,id):
    print('payment sucess',selected_address_id)   # we have fetch this id from return_url': f"http://{host}{reverse('paymentsuccess', args=[selected_address_id])}
                                                  # This id contain address detail of particular customer
    user =request.user
    customer_data = CustomerDetail.objects.get(pk=selected_address_id,)
    
    apple = Apple.objects.get(pk=id)
    Order(user=user,customer=customer_data,apple=apple,quantity=1).save()
   
    return render(request,'core/buynow_payment_success.html')


#===============================================forget password========================

def forgot_password(request):          
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(f'/reset_password/{uidb64}/{token}/')           
            send_mail(
                'Password Reset',
                f'Click the following link to reset your password: {reset_url}',
                'kembulkarakshat9967@gmail.com',  
                [email],
                fail_silently=False,
            )
            return redirect('passwordresetdone')
        else:
            messages.success(request,'please enter valid email address')
    return render(request, 'core/forgot_password.html')
                                         
#=====================================================================

def reset_password(request, uidb64, token):
    if request.method == 'POST':
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(password)
                    user.save()
                    return redirect('passwordresetdone')
                else:
                    return HttpResponse('Token is invalid', status=400)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return HttpResponse('Invalid link', status=400)
        else:
            return HttpResponse('Passwords do not match', status=400)
    return render(request, 'core/reset_password.html')
#=====================================================================
def password_reset_done(request):
    return render(request, 'core/password_reset_done.html')
#=====================================================================

def search(request):
    query = request.GET.get('query', '').strip()
    apples = []
    if query:
        apples = Apple.objects.filter(name__icontains=query)
        apples |= Apple.objects.filter(small_description__icontains=query)
        apples |= Apple.objects.filter(description__icontains=query)
    else:
        messages.warning(request, "Please enter a search term.")
        return redirect('home')
    return render_with_cart(request, 'core/search_results.html', {'apples': apples, 'query': query})

#=====================================================================
def apple_detail(request, id):
    apple = Apple.objects.get(id=id)
    return render(request, 'core/apple_detail.html', {'apple': apple})
#=====================================================================
