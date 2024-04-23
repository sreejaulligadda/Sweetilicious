from django.shortcuts import render
from django.views.generic import ListView, View, DetailView
from .models import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .forms import *
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.template.loader import render_to_string
from django.http import Http404
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

def get_referer(request):
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return None
    return referer

class HomeView(ListView):
    template_name = "index.html"
    context_object_name = 'items'

    def get_queryset(self):
        return Item.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                order = Order.objects.get(user=self.request.user, ordered=False)
                context['object'] = order
            except ObjectDoesNotExist:
                messages.error(self.request, "You do not have an active order")
        return context

class ShopView(ListView):
    model = Item
    paginate_by = 6
    template_name = "shop.html"
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not get_referer(self.request):
            raise Http404
        if self.request.user.is_authenticated:
            try:
                order = Order.objects.get(user=self.request.user, ordered=False)
                context['object'] = order
            except ObjectDoesNotExist:
                messages.error(self.request, "You do not have an active order")
        return context

class CategoryView(View):
    def get(self, *args, **kwargs):
        if not get_referer(self.request):
            raise Http404
        if self.request.user.is_authenticated:
            try:
                category = Category.objects.get(slug=self.kwargs['slug'])
                item = Item.objects.filter(category=category, is_active=True)
                order = Order.objects.get(user=self.request.user, ordered=False)
                context = {
                    'object': order,
                    'object_list': item,
                    'category_title': category,
                    'category_description': category.description,
                    'category_image': category.image
                }
                return render(self.request, "category.html", context)
            except ObjectDoesNotExist:
                category = Category.objects.get(slug=self.kwargs['slug'])
                item = Item.objects.filter(category=category, is_active=True)
                context = {
                    'object_list': item,
                    'category_title': category,
                    'category_description': category.description,
                    'category_image': category.image
                }
                return render(self.request, "category.html", context)
        else:
            category = Category.objects.get(slug=self.kwargs['slug'])
            item = Item.objects.filter(category=category, is_active=True)
            context = {
                    'object_list': item,
                    'category_title': category,
                    'category_description': category.description,
                    'category_image': category.image
            }
            return render(self.request, "category.html", context)

class ItemDetailView(DetailView):
    model = Item
    template_name = "product-detail.html"



@login_required
def add_to_cart(request, slug):
    if not get_referer(request):
        raise Http404
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item qty was updated.")
            return redirect("shoepage:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Item was added to your cart.")
            return redirect("shoepage:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item was added to your cart.")
    return redirect("shoepage:order-summary")


@login_required
def remove_from_cart(request, slug):
    if not get_referer(request):
        raise Http404
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "Item was removed from your cart.")
            return redirect("shoepage:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("shoepage:product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("shoepage:product", slug=slug)
    return redirect("shoepage:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    if not get_referer(self.request):
        raise Http404
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item qty was updated.")
            return redirect("shoepage:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("shoepage:product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("shoepage:product", slug=slug)
    return redirect("shoepage:product", slug=slug)


def get_coupon(request, code):
    if not get_referer(request):
        raise Http404
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("shoepage:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        if not get_referer(self.request):
            raise Http404
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("shoepage:checkout")

            except ObjectDoesNotExist:
                return redirect("shoepage:checkout")

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if not get_referer(self.request):
            raise Http404
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            return render(self.request, 'order_summary.html')

import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))



class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if not get_referer(self.request):
            raise Http404
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("shoepage:checkout")
    def post(self, request, *args, **kwargs):
        if not get_referer(self.request):
            raise Http404
        form = CheckoutForm(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')

                payment_option = form.cleaned_data.get('payment_option')
                request.session['payment_option'] = payment_option
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                    address_type='B'
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                # add redirect to the selected payment option
                if payment_option == 'S':
                    payment_option = 'stripe'
                    return redirect('shoepage:send_payment_email')
                elif payment_option == 'P':
                    payment_option = 'paypal'
                    return redirect('shoepage:send_payment_email', )
            else:
                messages.warning(
                        self.request, "Invalid payment option select")
                return redirect("/checkout/")
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")
    def get_payment_option(self):
        return self.payment_option

def validate_payment_token(request, token):
    token_generator = PasswordResetTokenGenerator()
    user = request.user
    if token_generator.check_token(user, token):
        return True
    return False

class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        token = self.request.GET.get('token')
        if validate_payment_token(self.request, token):
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.billing_address:
                context = {
                    'order': order,
                    'DISPLAY_COUPON_FORM': False
                }
                return render(self.request, "payment.html", context)
            else:
                messages.warning(
                    self.request, "u have not added a billing address")
                return redirect("shoepage:checkout")
        else:
            raise Http404
    def post(self, *args, **kwargs):
        if not get_referer(self.request):
            raise Http404
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token
            )
            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order
            order.ordered = True
            order.payment = payment
            # TODO : assign ref code
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Order was successful")
            return redirect("/")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "RateLimitError")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "The card was declined.")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not Authentication")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network Error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Something went wrong")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.error(self.request, "Serious Error occured")
            return redirect("/")

class PaypalView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        token = self.request.GET.get('token')
        if validate_payment_token(self.request, token):
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.billing_address:
                context = {
                    'order': order,
                    'DISPLAY_COUPON_FORM': False
                }
                return render(self.request, 'process_payment.html', context)
            else:
                messages.warning(
                    self.request, "u have not added a billing address")
                return redirect("shoepage:checkout")
        else:
            raise Http404

class CashView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        token = self.request.GET.get('token')
        if validate_payment_token(self.request, token):
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.billing_address:
                context = {
                    'order': order,
                    'DISPLAY_COUPON_FORM': False
                }
                payment = Payment()
                payment.stripe_charge_id = 'Cash'
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Order was successful")
                return redirect("/")
            else:
                messages.warning(
                    self.request, "u have not added a billing address")
                return redirect("shoepage:checkout")
        else:
            raise Http404


@csrf_exempt
def payment_done(request):

    return render(request, 'payment_done.html')

@csrf_exempt
def payment_canceled(request):
    if not get_referer(request):
        raise Http404
    return render(request, 'payment_cancelled.html')


class Contact(View):
    def get(self, request):
        if not get_referer(request):
            raise Http404
        return render(request, 'conctact.html')

class Privacy(View):
    def get(self, request):
        if not get_referer(request):
            raise Http404
        return render(request, 'privacyandterms.html')

@login_required
def send_payment_email(request):
    if not get_referer(request):
        raise Http404
    try:
        latest_order = Order.objects.filter(user=request.user, ordered=False)
        payment_options =  request.session.get('payment_option')
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(request.user)
        if payment_options == 'S':
            payment_url = f"https://sweetilicious-sreeje.pythonanywhere.com/payment/stripe/?token={token}"
        elif payment_options == 'P':
            payment_url = f"https://sweetilicious-sreeje.pythonanywhere.com/payments/cash/?token={token}"
        else:
            payment_url = f"https://sweetilicious-sreeje.pythonanywhere.com/payment/stripe/?token={token}"
        email_subject = 'Your Order Details'
        email_html_message = render_to_string('email/payment_email.html', {
            'objects': latest_order[0],
            'user': request.user,
            'payment_link': payment_url,
            'refferer': get_referer(request),
        })
        send_mail(
            email_subject,
            '',
            settings.EMAIL_HOST_USER,
            [request.user.email],
            html_message=email_html_message,
            fail_silently=False,
        )
        return render(request, 'pay.html')

    except ObjectDoesNotExist:
        return render(request, 'index.html')
    except IndexError:
        raise Http404

@login_required
def view_wishlist(request):
    user_wishlist = Wishlist.objects.get_or_create(user=request.user)[0]
    wishlist_items = user_wishlist.items.all()
    context = {
        'object_list': wishlist_items,
    }
    if not get_referer(request):
        raise Http404
    return render(request, 'view_wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Item, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    if product not in wishlist.items.all():
        wishlist.items.add(product)
    if not get_referer(request):
        raise Http404
    return redirect('shoepage:view_wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Item, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    if product in wishlist.items.all():
        wishlist.items.remove(product)
    if not get_referer(request):
        raise Http404
    return redirect('shoepage:view_wishlist')

def search(request):
    query = request.GET.get('query')
    if query:
        search_results = Item.objects.filter(slug__icontains=query)
    else:
        search_results = []
    context = {
        'query': query,
        'results': search_results
    }
    if not get_referer(request):
        raise Http404
    return render(request, 'search_results.html', context)

def filter_products(request):
    price_range = request.GET.get('price_range')
    if price_range == 'all':
        filtered_products = Item.objects.all()
    elif price_range == '200+':
        try:
            min_price = map(float, price_range.split('+'))
            filtered_products = Item.objects.filter(price__gte=200, price__lte=10000)
        except ValueError:
            return JsonResponse({'error': 'Invalid price range format'}, status=400)
    else:
        try:
            min_price, max_price = map(float, price_range.split('-'))
            filtered_products = Item.objects.filter(price__gte=min_price, price__lte=max_price)
        except ValueError:
            return JsonResponse({'error': 'Invalid price range format'}, status=400)
    products_data = serialize('json', filtered_products)
    return JsonResponse({'products': products_data})

def get_states(request):
    country_code = request.GET.get('country_code')
    if country_code == 'US':
        states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
        "Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas",
        "Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi",
        "Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
        "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas",
        "Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]
        states_dict = {state: state for state in states}
        return JsonResponse({'states': states_dict})
    elif country_code == 'IN':
        states = ["Andhra Pradesh","Arunachal Pradesh ","Assam","Bihar","Chhattisgarh","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu and Kashmir",
        "Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu",
        "Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh","Dadra and Nagar Haveli","Daman and Diu","Lakshadweep",
        "National Capital Territory of Delhi","Puducherry"]
        states_dict = {state: state for state in states}
        return JsonResponse({'states': states_dict})
    else:
        return JsonResponse({'error': 'Please select a valid country (e.g., "US" or "IN").'}, status=400)
