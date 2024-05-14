from django.http import Http404
import razorpay
from rest_framework import generics,permissions,pagination,viewsets
from . import serializers
from . import models
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.contrib.auth.hashers import make_password

class VendorList(generics.ListCreateAPIView):
    queryset = models.Vendor.objects.all()
    serializer_class = serializers.VendorSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if 'fetch_limit' in self.request.GET:
            limit=int(self.request.GET['fetch_limit'])
            qs=qs.annotate(downloads=Count('product')).order_by('-downloads','-id')
            qs=qs[:limit]
        return qs

class VendorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Vendor.objects.all()
    serializer_class = serializers.VendorDetailSerializer

# Vendor Product List
class VendorProductList(generics.ListAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vendor_id=self.kwargs['vendor_id']
        qs=qs.filter(vendor__id=vendor_id).order_by('id')
        return qs
    
@csrf_exempt
def vendor_register(request):
    if request.method == 'POST':
        # Extract data from request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'Username already exists.'
            })

        # Hash the password securely
        hashed_password = make_password(password)

        # Create the user
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=hashed_password
        )

        # Create the vendor
        vendor = models.Vendor.objects.create(
            user=user,
            mobile=mobile,
            address=address
        )

        return JsonResponse({
            'success': True,
            'user_id': user.id,
            'vendor_id': vendor.id,
            'msg': 'Registration successful.'
        })
    else:
        return JsonResponse({
            'success': False,
            'msg': 'Method not allowed. Only POST requests are supported.'
        }, status=405)
    
@csrf_exempt
def vendor_change_password(request,vendor_id):
    password=request.POST.get('password')
    vendor=models.Vendor.objects.get(id=vendor_id)
    user=vendor.user
    user.password=make_password(password)
    user.save()
    msg={'bool':True,'msg':'Password has been changed'}
    return JsonResponse(msg)

@csrf_exempt
def vendor_login(request):
    username=request.POST.get('username')
    password=request.POST.get('password')
    user=authenticate(username=username,password=password)
    if user:
        vendor=models.Vendor.objects.filter(user=user).first()
        login(request, user)
        msg={
            'bool':True,
            'user':user.username,
            'id':vendor.id,
        }
    else:
        msg={
            'bool':False,
            'msg':"Invalid Username/Password"
        }
    return JsonResponse(msg)

class ProductList(generics.ListCreateAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductListSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if 'category' in self.request.GET:
            category=self.request.GET['category']
            category=models.ProductCategory.objects.get(id=category)
            qs=qs.filter(category=category)
        if 'fetch_limit' in self.request.GET:
            limit=int(self.request.GET['fetch_limit'])
            qs=qs[:limit]
        if 'popular' in self.request.GET:
            limit=int(self.request.GET['popular'])
            qs=qs.order_by('-downloads','-id')
            qs=qs[:limit]
        return qs
    
class ProductImgsList(generics.ListCreateAPIView):
    queryset = models.ProductImage.objects.all()
    serializer_class = serializers.ProductImageSerializer

class ProductImgsDetail(generics.ListCreateAPIView):
    queryset = models.ProductImage.objects.all()
    serializer_class = serializers.ProductImageSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        product_id=self.kwargs['product_id']
        qs = qs.filter(product__id=product_id)
        return qs
    
class ProductImgDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ProductImage.objects.all()
    serializer_class = serializers.ProductImageSerializer
     
class TagProductList(generics.ListCreateAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductListSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        qs = super().get_queryset()
        tag=self.kwargs['tag']
        qs = qs.filter(tags__icontains=tag)
        return qs
    
class RelatedProductList(generics.ListCreateAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductListSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        product_id=self.kwargs['pk']
        product=models.Product.objects.get(id=product_id)
        qs = qs.filter(category=product.category).exclude(id=product_id)
        return qs

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductDetailSerializer

class CustomerList(generics.ListCreateAPIView):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer

class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerDetailSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

@csrf_exempt
def customer_login(request):
    username=request.POST.get('username')
    password=request.POST.get('password')
    print(f'Received username: {username} and password: {password}')
    user=authenticate(username=username,password=password)
    print(f'Authenticated user: {user}')
    if user:
        customer=models.Customer.objects.get(user=user)
        login(request, user)
        msg={
            'bool':True,
            'user':user.username,
            'id':customer.id,
        }
    else:
        msg={
            'bool':False,
            'msg':"Invalid Username/Password"
        }
    return JsonResponse(msg)




@csrf_exempt
def customer_register(request):
    if request.method == 'POST':
        # Extract data from request
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'Username already exists.'
            })

        # Hash the password securely
        hashed_password = make_password(password)

        # Create the user
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=hashed_password
        )

        # Create the customer
        customer = models.Customer.objects.create(
            user=user,
            mobile=mobile
        )

        return JsonResponse({
            'success': True,
            'user_id': user.id,
            'customer_id': customer.id,
            'message': 'Registration successful.'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed. Only POST requests are supported.'
        }, status=405)


@csrf_exempt
def customer_change_password(request,customer_id):
    password=request.POST.get('password')
    customer=models.Customer.objects.get(id=customer_id)
    user=customer.user
    user.password=make_password(password)
    user.save()
    msg={'bool':True,'msg':'Password has been changed'}
    return JsonResponse(msg)


class OrderList(generics.ListCreateAPIView):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

class OrderItemList(generics.ListCreateAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemsSerializer

class CustomerOrderItemList(generics.ListAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id=self.kwargs['pk']
        qs = qs.filter(order__customer__id=customer_id)
        return qs
    
# Vendor Order Item List
class VendorOrderItemList(generics.ListAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vendor_id=self.kwargs['pk']
        qs = qs.filter(product__vendor__id=vendor_id)
        return qs
    
# Vendor Daily Orders
class VendorDailyReport(generics.ListAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrdersSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vendor_id=self.kwargs['pk']
        qs = qs.filter(product__vendor__id=vendor_id)
        return qs
    
# Vendor Customers
class VendorCustomerList(generics.ListAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vendor_id=self.kwargs['pk']
        qs = qs.filter(product__vendor__id=vendor_id)
        return qs
    
# Vendor Customer Order Items
class VendorCustomerOrderItemList(generics.ListAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderItemsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        vendor_id=self.kwargs['vendor_id']
        customer_id=self.kwargs['customer_id']
        qs = qs.filter(order__customer__id=customer_id,product__vendor__id=vendor_id)
        return qs

class OrderDetail(generics.ListAPIView):
    queryset = models.OrderItems.objects.all()
    serializer_class = serializers.OrderDetailSerializer

    def get_queryset(self):
        try:
            order_id=self.kwargs['pk']
            order=models.Order.objects.get(id=order_id)
            order_items=models.OrderItems.objects.filter(order=order)
            return order_items
        except:
            raise Http404("Order does not exist")
        
class OrderDelete(generics.RetrieveDestroyAPIView):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderDetailSerializer
        
class CustomerAddressViewSet(viewsets.ModelViewSet):
    serializer_class=serializers.CustomerAddressSerializer
    queryset=models.CustomerAddress.objects.all()

    def perform_create(self, serializer):
        # Get the customer ID from the request data
        customer_id = self.request.data.get('customer')
        # Retrieve the Customer instance corresponding to the customer ID
        customer = models.Customer.objects.get(id=customer_id)
        # Set the customer field of the CustomerAddress instance
        serializer.save(customer=customer)

class ProductRatingViewSet(viewsets.ModelViewSet):
    serializer_class=serializers.ProductRatingSerializer
    queryset=models.ProductRating.objects.all()

#Category List API
class CategoryList(generics.ListCreateAPIView):
    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if 'popular' in self.request.GET:
            limit=int(self.request.GET['popular'])
            qs=qs.annotate(downloads=Count('category_product')).order_by('-downloads','-id')
            qs=qs[:limit]
        return qs

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.CategoryDetailSerializer

# Order Update
class OrderModify(generics.RetrieveUpdateAPIView):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

def update_order_status(request,order_id):
    if request.method=='POST':
        if 'payment_mode' in request.POST:
            payment_mode=request.POST.get('payment_mode')
            trans_ref=request.POST.get('trans_ref')
            updateRes=models.Order.objects.filter(id=order_id).update(order_status=True,payment_mode=payment_mode,trans_ref=trans_ref)
        else:
            updateRes=models.Order.objects.filter(id=order_id).update(order_status=True)
        msg={
            'bool':False
        }
        if updateRes:
            msg={
                'bool':True
            }
    return JsonResponse(msg)

@csrf_exempt
def update_product_download_count(request,product_id):
    if request.method=='POST':
        product=models.Product.objects.get(id=product_id)
        totalDownloads = int(product.downloads)
        totalDownloads+=1
        if totalDownloads == 0:
            totalDownloads=1
        updateRes = models.Product.objects.filter(id=product_id).update(downloads=totalDownloads)
        msg={
            'bool':False
        }
        if updateRes:
            msg={
                'bool':True
            }
    return JsonResponse(msg)

# Wishlist
class WishList(generics.ListCreateAPIView):
    queryset = models.Wishlist.objects.all()
    serializer_class = serializers.WishlistSerializer

@csrf_exempt
def check_in_wishlist(request):
    if request.method=='POST':
        product_id=request.POST.get('product')
        customer_id=request.POST.get('customer')
        checkWishlist = models.Wishlist.objects.filter(product__id=product_id,customer__id=customer_id).count()
        msg={
            'bool':False
        }
        if checkWishlist > 0:
            msg={
                'bool':True
            }
    return JsonResponse(msg)

@csrf_exempt
def delete_customer_orders(request,customer_id):
    if request.method=='DELETE':
        orders=models.Order.objects.filter(customer__id=customer_id).delete()
        msg={
            'bool':False
        }
        if orders:
            msg={
                'bool':True
            }
    return JsonResponse(msg)

# Customer Wish Items
class CustomerWishItemList(generics.ListAPIView):
    queryset = models.Wishlist.objects.all()
    serializer_class = serializers.WishlistSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id=self.kwargs['pk']
        qs = qs.filter(customer__id=customer_id)
        return qs
    
@csrf_exempt
def remove_from_wishlist(request):
    if request.method=='POST':
        wishlist_id=request.POST.get('wishlist_id')
        res = models.Wishlist.objects.filter(id=wishlist_id).delete
        msg={
            'bool':False
        }
        if res:
            msg={
                'bool':True
            }
    return JsonResponse(msg)

# Customer Address List
class CustomerAddressList(generics.ListAPIView):
    queryset = models.CustomerAddress.objects.all()
    serializer_class = serializers.CustomerAddressSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id=self.kwargs['pk']
        qs = qs.filter(customer__id=customer_id).order_by('id')
        return qs
    
@csrf_exempt
def mark_default_address(request,pk):
    if request.method=='POST':
        address_id=request.POST.get('address_id')
        models.CustomerAddress.objects.all().update(default_address=False)
        res = models.CustomerAddress.objects.filter(id=address_id).update(default_address=True)
        msg={
            'bool':False
        }
        if res:
            msg={
                'bool':True
            }
    return JsonResponse(msg)

def customer_dashboard(request,pk):
    customer_id=pk
    totalOrders=models.Order.objects.filter(customer__id=customer_id).count()
    totalWishList=models.Wishlist.objects.filter(customer__id=customer_id).count()
    totalAddress=models.CustomerAddress.objects.filter(customer__id=customer_id).count()
    msg={
        'totalOrders':totalOrders,
        'totalWishList':totalWishList,
        'totalAddress':totalAddress,
    }
    return JsonResponse(msg)

def vendor_dashboard(request,pk):
    vendor_id=pk
    totalProducts=models.Product.objects.filter(vendor__id=vendor_id).count()
    totalOrders=models.OrderItems.objects.filter(product__vendor__id=vendor_id).count()
    totalCustomers=models.OrderItems.objects.filter(product__vendor__id=vendor_id).values('order__customer').count()
    msg={
        'totalProducts':totalProducts,
        'totalOrders':totalOrders,
        'totalCustomers':totalCustomers,
    }
    return JsonResponse(msg)

@csrf_exempt
def create_razorpay_order(request):
    client = razorpay.Client(auth=("rzp_test_oy9pi3SdZpttG2", "uaI3vRVdlHKm9PuHYFmQLurq"))
    res=client.order.create({
        "amount": int(request.POST.get('amount')),
        "currency": "INR",
        "receipt": request.POST.get('order_id'),
        "partial_payment": False,
    })
    if res:
        msg={
            'bool':True,
            'data':res
        }
    else:
        msg={
            'bool':False,
        }
    return JsonResponse(msg)