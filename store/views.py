from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient
import json
import datetime


from .models import *
from.utils import cookieCart, cartData, guestOrder

# Create your views here.

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {
        'products': products,
        'cartItems': cartItems
    }
    return render(request, "store/store.html", context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']           

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
    }
    return render(request, "store/cart.html", context)


def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']  
        
    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems
    }
    return render(request, "store/checkout.html", context)


def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data ['shipping']['address'],
                city = data ['shipping']['city'],
                zipcode = data ['shipping']['zipcode']
            )
    else:
        customer, order = guestOrder(request, data)
        

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()
    # order.delete()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data ['shipping']['address'],
            city = data ['shipping']['city'],
            zipcode = data ['shipping']['zipcode']
        )
    order.delete()
    return JsonResponse('Payment complete', safe=False)


# Django-daraja

def daraja_mpesa(request):
    cl = MpesaClient()
    phone_number = '0790409559'
    amount = 1
    account_reference = 'FASHIONHUB'
    transaction_desc = 'FASHIONPAY'
    callback_url = 'https://darajambili.herokuapp.com/express-payment'
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    return HttpResponse(response)

def stk_push_callback(request):
        data = request.body
