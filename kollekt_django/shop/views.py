from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, F, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import JoinForm, LoginForm, RegisterForm
from .models import Order, Product, User


# --------------------------------------------------------------------------
# Boutique
# --------------------------------------------------------------------------
def home(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    return render(request, "shop/home.html", {
        "products": products,
        "open_count": sum(1 for p in products if p.stock > 0),
    })


@login_required
def join_product(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = JoinForm(request.POST or None, product=product)

    if request.method == "POST" and form.is_valid():
        qty = form.cleaned_data["quantity"]
        with transaction.atomic():
            locked = Product.objects.select_for_update().get(pk=product.pk)
            if qty > locked.stock:
                form.add_error("quantity", f"Il ne reste que {locked.stock} place(s) pour cette offre.")
            else:
                Order.objects.create(
                    user=request.user, product=locked, quantity=qty, unit_price=locked.price,
                )
                locked.stock = F("stock") - qty
                locked.ordered_count = F("ordered_count") + qty
                locked.save(update_fields=["stock", "ordered_count"])
                messages.success(request, f"Votre place est réservée pour « {locked.name} ».")
                return redirect("my_orders")

    return render(request, "shop/join.html", {"product": product, "form": form})


@login_required
def my_orders(request):
    orders = request.user.orders.select_related("product")
    return render(request, "shop/my_orders.html", {"orders": orders})


# --------------------------------------------------------------------------
# Authentification
# --------------------------------------------------------------------------
class SiteLoginView(LoginView):
    template_name = "shop/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        return "/gestion/" if self.request.user.is_staff else "/"


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Compte créé. Vous pouvez maintenant rejoindre vos commandes.")
        nxt = request.POST.get("next") or request.GET.get("next")
        if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
            return redirect(nxt)
        return redirect("home")
    return render(request, "shop/register.html", {
        "form": form, "next": request.GET.get("next", ""),
    })


# --------------------------------------------------------------------------
# Tableau de bord administrateur (équivalent de <AdminDashboard />)
# --------------------------------------------------------------------------
TABS = [
    ("apercu", "Vue d’ensemble", "layout-dashboard"),
    ("commandes", "Commandes", "shopping-bag"),
    ("clients", "Clients", "users"),
    ("paiements", "Paiements", "credit-card"),
    ("catalogue", "Catalogue", "package"),
    ("parametres", "Paramètres", "settings"),
]
TAB_TEXT = {
    "apercu": ("Votre activité", "Voici ce qui se passe chez ALK IMPORT."),
    "commandes": ("Commandes", "Suivez toutes les commandes clients et leur statut."),
    "clients": ("Clients", "Gérez les membres inscrits et leurs coordonnées."),
    "paiements": ("Paiements", "Consultez les paiements reçus et le chiffre d’affaires."),
    "catalogue": ("Catalogue", "Ajoutez, modifiez et suivez vos articles."),
    "parametres": ("Paramètres", "Configurez votre boutique ALK IMPORT."),
}
PAID_STATUSES = [Order.Status.PAID, Order.Status.DELIVERED]


def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/connexion/?next={request.path}")
        if not (request.user.is_active and request.user.is_staff):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@staff_required
def dashboard(request, tab="apercu"):
    if tab not in TAB_TEXT:
        raise Http404
    title, subtitle = TAB_TEXT[tab]

    paid_orders = Order.objects.filter(status__in=PAID_STATUSES)
    revenue = paid_orders.aggregate(t=Sum(F("unit_price") * F("quantity")))["t"] or 0
    pending = Order.objects.filter(status=Order.Status.PENDING).count()

    ctx = {
        "tabs": TABS, "tab": tab, "title": title, "subtitle": subtitle,
        "tab_label": next(label for key, label, _ in TABS if key == tab),
        "stats": {
            "revenue": revenue,
            "orders": Order.objects.count(),
            "clients": User.objects.filter(is_staff=False).count(),
            "pending": pending,
        },
        "pending_badge": pending,
        "statuses": Order.Status.choices,
    }

    if tab == "apercu":
        ctx["orders"] = Order.objects.select_related("user", "product")[:8]
    elif tab == "commandes":
        ctx["orders"] = Order.objects.select_related("user", "product")
    elif tab == "clients":
        ctx["clients"] = User.objects.filter(is_staff=False).annotate(n_orders=Count("orders")).order_by("-date_joined")
    elif tab == "paiements":
        ctx["orders"] = paid_orders.select_related("user", "product")
    elif tab == "catalogue":
        ctx["products"] = Product.objects.select_related("category")

    return render(request, "shop/dashboard.html", ctx)


@staff_required
@require_POST
def order_set_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new = request.POST.get("status")
    if new not in Order.Status.values:
        messages.error(request, "Statut invalide.")
    elif order.status == Order.Status.CANCELLED:
        messages.error(request, "Une commande annulée ne peut plus être modifiée.")
    else:
        with transaction.atomic():
            if new == Order.Status.CANCELLED:
                # On libère les places réservées
                Product.objects.filter(pk=order.product_id).update(
                    stock=F("stock") + order.quantity,
                    ordered_count=F("ordered_count") - order.quantity,
                )
            order.status = new
            order.save(update_fields=["status"])
        messages.success(request, f"Commande #{order.pk} mise à jour.")
    return redirect("dashboard_tab", tab="commandes")
