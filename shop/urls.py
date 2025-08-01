"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from shop import views
app_name="shop"
urlpatterns = [
    path('',views.CategoryView.as_view(),name="categories"),
    path('products/<int:i>',views.ProductsView.as_view(),name="products"),
    path('productdetail/<int:i>',views.ProductDetailView.as_view(),name="productdetail"),
    path('signup',views.SignupView.as_view(),name="signup"),
path('signin',views.SigninView.as_view(),name="signin"),
    path('otp-verify',views.OtpVerificationView.as_view(),name="verify"),
path('signout',views.SignOutView.as_view(),name="signout"),
    path('addcategory',views.AddCategoryView.as_view(),name="addcategory"),
    path('addproduct',views.AddProductView.as_view(),name="addproduct"),

]