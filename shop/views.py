from django.shortcuts import render,redirect
from django.views import View
from shop.models import Category

class CategoryView(View):
    def get(self,request):
        c=Category.objects.all()
        return render(request,'categories.html',{'category':c})


class ProductsView(View):
    def get(self,request,i):
        c=Category.objects.get(id=i)

        return render(request,'products.html',{'category':c})
from shop.models import Product
class ProductDetailView(View):
    def get(self,request,i):
        p=Product.objects.get(id=i)
        return render(request,'productdetail.html',{'product':p})

from shop.forms import SignupForm
from django.core.mail import send_mail
class SignupView(View):
    def post(self,request):
        form_instance=SignupForm(request.POST)
        if form_instance.is_valid():


            user=form_instance.save(commit=False)
            user.is_active=False #After otp verification it will set to True.
            user.save()
            user.generate_otp()
            send_mail(
                'OTP Test',
                user.otp,
                'thomaspt2016@example.com',
                [user.email],
                fail_silently=False,
                )
            print('hello')
            return redirect('shop:verify')

    def get(self,request):
        form_instance=SignupForm()
        return render(request,'signup.html',{'form':form_instance})

from shop.models import CustomUser
from django.contrib import messages
class OtpVerificationView(View):

    def post(self,request):
        otp=request.POST.get('otp')
        print(otp)
        try:
            u=CustomUser.objects.get(otp=otp)
            u.is_active=True
            u.is_verified=True
            u.otp=None
            u.save()
            return redirect('shop:categories')
        except:
            # print("invalid otp")
            messages.error(request,"Invalid OTP")
            return redirect('verify')
    def get(self,request):
        return render(request,'otp_verify.html')

from shop.forms import LoginForm
from django.contrib.auth import authenticate,login

class SigninView(View):

    def post(self,request):
        form_instance=LoginForm(request.POST)
        if form_instance.is_valid():
            name=form_instance.cleaned_data['username']
            pwd=form_instance.cleaned_data['password']
            # print(name,pwd)
            user=authenticate(username=name,password=pwd)
            #authenticate() returns user object if all the user credentials are correct else none
            if user and user.is_superuser==True:
                login(request,user)
                return redirect('shop:categories')
            elif user and user.is_superuser==False:
                login(request, user)
                return redirect('shop:categories')
            else:
                print("invalid user credentials")
                return redirect('signin')

    def get(self,request):
        form_instance=LoginForm()
        return render(request,'login.html',{'form':form_instance})



from django.contrib.auth import logout

class SignOutView(View):
    def get(self,request):
        logout(request)       #Removes the user from current session
        return redirect('shop:signin')

from shop.forms import CategoryForm,ProductForm
class AddCategoryView(View):
    def get(self,request):
        form_instance=CategoryForm()
        return render(request,'addcategory.html',{'form':form_instance})
    def post(self,request):
        form_instance=CategoryForm(request.POST,request.FILES)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('shop:categories')
        # else:
        #     form_instance=CategoryForm()
        #     return render(request,'addcategory.html',{'form':form_instance})

class AddProductView(View):
    def get(self, request):
        form_instance = ProductForm()
        return render(request, 'addproduct.html', {'form': form_instance})

    def post(self, request):
        form_instance = ProductForm(request.POST, request.FILES)
        if form_instance.is_valid():
            form_instance.save()
            return redirect('shop:categories')

