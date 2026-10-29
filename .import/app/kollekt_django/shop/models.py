from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class User(AbstractUser):
    phone = models.CharField("Téléphone", max_length=20, blank=True)

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"


class Category(models.Model):
    name = models.CharField("Nom", max_length=60, unique=True)

    class Meta:
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("Nom", max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="Catégorie")
    description = models.CharField("Description", max_length=255, blank=True)
    price = models.PositiveIntegerField("Prix (FCFA TTC)")
    tag = models.CharField("Badge", max_length=40, blank=True, help_text="Ex. : Sur commande, Nouveau…")
    arrival_date = models.DateField("Arrivée prévue", null=True, blank=True)
    ordered_count = models.PositiveIntegerField("Commandes réunies", default=0)
    stock = models.PositiveIntegerField("Places restantes", default=0)
    image = models.ImageField("Image (fichier)", upload_to="products/", blank=True)
    image_url = models.URLField("Image (URL externe)", max_length=500, blank=True)
    accent = models.CharField("Couleur de fond", max_length=7, default="#e3ddd3", help_text="Code hexadécimal, ex. #dcd6c8")
    is_active = models.BooleanField("Visible", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "produit"
        verbose_name_plural = "produits"
        ordering = ["arrival_date", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:150] or "produit"
            slug, i = base, 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("join_product", args=[self.slug])

    @property
    def image_src(self):
        if self.image:
            return self.image.url
        return self.image_url

    @property
    def is_open(self):
        return self.is_active and self.stock > 0

    @property
    def progress_percent(self):
        total = self.ordered_count + self.stock
        return round(self.ordered_count * 100 / total) if total else 0


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        CONFIRMED = "confirmed", "Confirmée"
        PAID = "paid", "Payée"
        DELIVERED = "delivered", "Livrée"
        CANCELLED = "cancelled", "Annulée"

    user = models.ForeignKey("shop.User", on_delete=models.CASCADE, related_name="orders", verbose_name="Client")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orders", verbose_name="Produit")
    quantity = models.PositiveIntegerField("Quantité", default=1)
    unit_price = models.PositiveIntegerField("Prix unitaire (FCFA)")
    status = models.CharField("Statut", max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField("Date", auto_now_add=True)

    class Meta:
        verbose_name = "commande"
        verbose_name_plural = "commandes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} — {self.user} — {self.product}"

    @property
    def total(self):
        return self.unit_price * self.quantity
