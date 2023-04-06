import json
from . models import *


def cookieCart(request):
    # Lấy giá trị từ cookie khi người dùng không login
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('Cart: ', cart)
    # tạo giá trị mặc định để khi log out tránh xảy ra lỗi khi truyền context
    items = []
    order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
    cartItems = order['get_cart_items']
    
    for i in cart:
        # use try block to prevent items in cart that may have been removed 
        try:
            cartItems += cart[i]['quantity']
        
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            
            # tổng giá:
            order['get_cart_total'] += total
            # tổng số lượng hàng hóa:
            order['get_cart_items'] += cart[i]['quantity']
            
            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL,
                    
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)
            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    
    return {'items': items, 'order': order,'cartItems':cartItems}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        items = cookieData['items']
        order = cookieData['order']
    return {'items': items, 'order': order,'cartItems':cartItems}

def guestOrder(request, data):
    print('User not log in ..')
        
    print('COOKIES: ', request.COOKIES)
    # Lấy tên, email và items từ cookie
    name = data['form']['name']
    email = data['form']['email']
    cookieData = cookieCart(request)
    items = cookieData['items']
    
    # Tạo customer có name và email
    customer, created = Customer.objects.get_or_create(email=email,)
    customer.name = name
    customer.save()
    
    order = Order.objects.create(customer=customer, complete=False,)
    # Vì sao tạo orderItem để làm gì
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product, 
            order=order,
            quantity=item['quantity'])
            
    return customer,order