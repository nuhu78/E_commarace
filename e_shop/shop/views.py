from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import Catagory, OrderItem, Product, Ratting, Cart, Order, CartItem
from django.contrib import messages
from .forms import RegistrationForm,RatingForm, CheckoutForm
from django.db.models import Min, Max, Q , Avg
from django.contrib.auth.decorators import login_required
from .utils import generate_sslcommerz_payment, send_confirmation_email
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
def login_view(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'shop/login.html')        
    
def register_view(request):
    if request.method=='POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('shop:login')
    else:
        form=RegistrationForm()
    return render(request, 'shop/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('shop:login')

def home(request):
    featured_products = Product.objects.filter(is_featured=True).order_by('-created')[:8]
    categories = Catagory.objects.all()
    return render(request, '', {
        'featured_products': featured_products,
        'categories': categories
    })

def product_list(request, category_slug=None):
    category = None
    categories = Catagory.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Catagory, slug=category_slug)
        products = products.filter(catagory=category)

    min_price = products.aggregate(Min('price'))['price__min']
    max_price = products.aggregate(Max('price'))['price__max']
    if request.GET.get('min_price'):
        products = products.filter(price__gte=request.GET.get('min_price'))
    if request.GET.get('max_price'):
        products = products.filter(price__lte=request.GET.get('max_price'))   
    if request.GET.get('ratting'):
        min_ratting = int(request.GET.get('ratting'))
        products=products.annotate(avg_ratting=Avg('rattings__rating')).filter(avg_ratting__gte=min_ratting)
    if request.GET.get('search'):
        query=request.GET.get('search')
        products=products.filter
        (Q(name__icontains=query)
        | Q(description__icontains=query) 
        | Q(catagory__icontains=query))

    return render(request, '', {
        'category': category,
        'categories': categories,
        'products': products,
        'min_price': min_price,
        'max_price': max_price

    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    related_products = Product.objects.filter (catagory=product.catagory).exclude(id=product.id)[:4]
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = Ratting.objects.get(product=product, user=request.user)
        except Ratting.DoesNotExist:
            pass
    ratting_form = RatingForm(instance=user_rating)
    return render(request, '', {
        'product': product,
        'related_products': related_products,
        'user_rating': user_rating,
        'rating_form': ratting_form
        
    })
@login_required
def cart_detail(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart=Cart.objects.create(user=request.user)
    return render(request, '', {'cart': cart})

@login_required
def cart_add(request, product_id):
    product=get_object_or_404(Product, id=product_id, available=True)
    try:
        cart=Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart=Cart.objects.create(user=request.user)
    
    try:
        cart_item=CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity +=1
        cart_item.save()
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity=1)

    messages.success(request, f'{product.name} added to cart.')    
    return redirect('')
@login_required
def cart_remove(request, product_id):
    cart=get_object_or_404(Cart, user=request.user)
    product=get_object_or_404(Product, id=product_id)
    cart_item=get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.delete()
    messages.success(request, f'{product.name} removed from cart.')
    return redirect('')
@login_required
def cart_update(request, product_id):
    cart=get_object_or_404(Cart, user=request.user)
    product=get_object_or_404(Product, id=product_id)
    cart_item=get_object_or_404(CartItem, cart=cart, product=product)
    quantity=int(request.POST.get('quantity', 1))
    if quantity <=0:
        cart_item.delete()
        messages.success(request, f'{product.name} removed from cart.')
    else:
        cart_item.quantity=quantity
        cart_item.save()
        messages.success(request, f'Updated {product.name} quantity to {quantity}.')
    return redirect('')
@login_required
def checkout(request):
    try:
        cart=Cart.objects.get(user=request.user)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('shop:cart_detail')
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('')

    if request.method=='POST':
        form=CheckoutForm(request.POST)
        if form.is_valid():
            order=form.save(commit=False)
            order.user=request.user
            order.save()
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            cart.items.all().delete()
            request.session['order_id']=order.id
            return redirect('')      
    else:
        initial_data={}
        if request.user.first_name:
            initial_data['first_name']=request.user.first_name
        if request.user.last_name:
            initial_data['last_name']=request.user.last_name
        if request.user.email:
            initial_data['email']=request.user.email

        form=CheckoutForm(initial=initial_data)
    return render(request, '', {
        'cart': cart,
        'form': form
        }) 

@csrf_exempt
@login_required
def payment_process(request):
    order_id=request.session.get('order_id')
    if not order_id:
        return redirect('')
    order=get_object_or_404(Order, id=order_id)
    payment_data=generate_sslcommerz_payment(order, request)
    if payment_data['status']=='SUCCESS':
        return redirect(payment_data['GatewayPageURL'])
    else:
        messages.error(request, 'Failed to initiate payment. Please try again.')
        return redirect('')

@csrf_exempt
@login_required
def payment_success(request, order_id):
    order=get_object_or_404(Order, id=order_id, user=request.user)
    order.paid=True
    order.status='Processing'
    order.tansaction_id=order_id
    order.save()
    
    order_items=order.items.all()
    for item in order_items:
        product=item.product
        product.stock -= item.quantity
       
        if product.stock < 0:
            product.stock=0
            product.save()

    send_confirmation_email(order)
    messages.success(request, 'Payment successful! Your order has been placed.')
    return redirect('')

@csrf_exempt
@login_required
def payment_fail(request, order_id):
    order=get_object_or_404(Order, id=order_id, user=request.user)
    order.status='canceled'
    order.save()
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('')        

@csrf_exempt
@login_required
def payment_cancel(request, order_id):
    order=get_object_or_404(Order, id=order_id, user=request.user)
    order.status='canceled'
    order.save()
    messages.info(request, 'Payment canceled. Your order has been canceled.')
    return redirect('')

  