
from cart.models import Cart
def count_items(request):
    if request.user.is_authenticated: #if a user is logged in
        u=request.user #current logged in user
        c=Cart.objects.filter(user=u)
        count=0
        for i in c:
            count=count+i.quantity #calculates the total number of products in cart
    else:
        count=0

    return {'count':count}