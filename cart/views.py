from django.shortcuts import render,redirect
from shop.models import Product
from cart.models import Cart
from django.views import View
class AddtoCartView(View):
    def get(self,request,i):
        #cart -user,product,quantity
        u=request.user #logged in user
        p=Product.objects.get(id=i)
        try:
            c=Cart.objects.get(user=u,product=p) #if product  already  inside Cart Table
            c.quantity+=1 #increments the quantity value by 1
            c.save()
        except:    #if product not inside cart table creates a new cart record.
            c=Cart.objects.create(user=u,product=p,quantity=1)
            c.save()

        return redirect('cart:cartview')

class CartView(View):
    def get(self,request):
       u=request.user
       c=Cart.objects.filter(user=u)
       total=0
       for i in c:
           total+=i.quantity*i.product.price

       return render(request,'cart.html',{'cart':c,'total':total})

class CartdecrementView(View):
    def get(self,request,i):
        u=request.user
        p=Product.objects.get(id=i)
        try:
            c=Cart.objects.get(user=u,product=p)
            if c.quantity>1: #if cart object quantity is greater than 1
                c.quantity-=1 #decrements quantity by 1
                c.save()
            else:
                c.delete() #if cart object quantity is 1 then deletes the cart object
        except:
            pass
        return redirect('cart:cartview')

class CartremoveView(View):
    def get(self, request, i):
        u = request.user
        p = Product.objects.get(id=i)
        try:
            c = Cart.objects.get(user=u, product=p)
            c.delete()

        except:
            pass
        return redirect('cart:cartview')

def check_stock(c):
    stock=True
    for i in c:
        if i.product.stock<i.quantity:
            stock=False
            break
    return stock

import razorpay
from django.contrib import messages
from cart.forms import OrderForm
from cart.models import Order_items
class OrderFormView(View):
    def post(self,request):
        data=request.POST
        print(data)
        u=request.user

        #order -->user,address,phone,payment,order_id,is_paid,amount
        form_instance=OrderForm(request.POST)
        if form_instance.is_valid():
            order_object=form_instance.save(commit=False)
            order_object.user=u
            order_object.save() #creates an order_object in Order Table


            c=Cart.objects.filter(user=u) #Cart items selected by  particular user
            stock=check_stock(c) #to check the stock before creating order
            if stock:

                for i in c:
                    o=Order_items.objects.create(order=order_object,product=i.product,quantity=i.quantity)
                    o.save()
                    #in each iteration creates an order_items object corresponding to a cart object

                #Order Amount
                total=0
                for i in c:
                    total+=i.quantity*i.product.price

                if order_object.payment_method=="ONLINE":

                    #Razorpay Payment Gateway Integration
                    #1.creates client connection
                    # client = razorpay.Client(auth=("rzp_test_sJgGk1sHeX3AWm", "ylWAgRlJ3cxLO4BG25C7YEAX"))
                    clinent = razorpay.Client(auth=("rzp_test_6q2Y2f2fYK3y1o", "k9k7lX1qj2f9W2o0J2o1Y4Y2"))
                    #2.order creation
                    response_payment=clinent.order.create(dict(amount=total*100,currency='INR'))
                    #prints the response_payment
                    print(response_payment)

                    order_id=response_payment['id']
                    order_object.order_id=order_id
                    order_object.is_ordered=False
                    order_object.amount=total
                    order_object.save()
                    return render(request, 'payment.html', {'payment': response_payment, 'name': u.username})


                elif order_object.payment_method=="COD":
                    order_object.is_ordered=True
                    order_object.amount=total
                    order_object.save()
                    items = Order_items.objects.filter(order=order_object)

                    for i in items:
                        i.product.stock -= i.quantity  # decrements the each item stock
                        i.product.save()

                    # To delete cart of the current user
                    c = Cart.objects.filter(user=u)
                    c.delete()
                    return redirect('shop:categories')
                else:
                    pass
            else:
                messages.error(request,"Currently items not available")
                return render(request,'payment.html')
    def get(self,request):
        form_instance=OrderForm()

        return render(request,'orderform.html',{'form':form_instance})



from django.utils.decorators import method_decorator
from shop.models import CustomUser
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from cart.models import Order
@method_decorator(csrf_exempt, name='dispatch')#to avoid csrf protection error
class PaymentsuccessView(View):
    def post(self,request,i):
        user=CustomUser.objects.get(username=i)
        login(request,user) #To add the current user into session again

        response=request.POST
        print(response) #payment confirmation send by Razorpay to our application
                        #order-id,payment-id,signature

        #To change ordered field to True after completion of payment
        o=Order.objects.get(order_id=response['razorpay_order_id'])
        o.is_ordered=True
        o.save()

        #To change the product stock first filter ordered_items
        items=Order_items.objects.filter(order=o)

        for i in items:
            i.product.stock-=i.quantity #decrements the each item stock
            i.product.save()


        #To delete cart of the current user
        c=Cart.objects.filter(user=user)
        c.delete()



        return render(request,'payment_success.html')


class OrderSummaryView(View):
    def get(self,request):
        u = request.user
        o = Order.objects.filter(user=u, is_ordered=True)
        return render(request, 'ordersummary.html', {'orders': o})