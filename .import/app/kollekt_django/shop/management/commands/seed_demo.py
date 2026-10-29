from datetime import date

from django.core.management.base import BaseCommand

from shop.models import Category, Product

BLOB = "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/"

PRODUCTS = [
    ("Sport", "Ballon de football bonne qualité", "Ballon premium disponible sur commande.", 6500, 18, 32, "#dcd6c8", "Sur commande", date(2026, 11, 15), "WhatsApp%20Image%202026-10-28%20at%2008.24.29-Q0vovKbnIzWZMmD5HjgDD3jUssGibV.jpeg"),
    ("Mode", "Montres cuir — A, B, C", "Choisissez votre modèle et la quantité souhaitée.", 2500, 18, 22, "#ded8cf", "Très demandées", date(2026, 11, 20), "image-T770mO56J7R6TUGZdnnH7M5rF26h9K.png"),
    ("Bien-être", "Pistolet de massage", "Récupération musculaire à la maison.", 3500, 27, 23, "#eadfd5", "Coup de cœur", date(2026, 11, 22), "WhatsApp%20Image%202026-10-17%20at%2009.57.08-9MndYhimu6Mh7G1pTrvq7fb8q9DnZd.jpeg"),
    ("Mode", "Bretelles de maintien", "Maintien discret et confortable pour vos vêtements.", 3000, 11, 19, "#e3ddd3", "Sur commande", date(2026, 11, 28), "WhatsApp%20Image%202026-10-11%20at%2002.52.34-1nRdVY0EqpcVTXmHraDeWwL9lVP3UT.jpeg"),
    ("Maison", "Ensemble de 10 cintres", "Un lot pratique pour organiser votre dressing.", 1000, 34, 66, "#eee8df", "Bon plan", date(2026, 11, 30), "WhatsApp%20Image%202026-10-08%20at%2014.17.34-Sba0FmV1FvO5lws3c9i9W6BZW8T7ZN.jpeg"),
    ("Mode", "Pull over noir / gris", "Tailles M à 5XL, sans taxe supplémentaire.", 4000, 16, 24, "#cbc9c6", "M à 5XL", date(2026, 12, 5), "image-4Ub3AFmSV83aawQvV784WUC7yviRRM.png"),
    ("Maison", "Armoire pliable 3 battants", "Pour ranger vêtements et chaussures facilement.", 12000, 9, 21, "#ded6cc", "Nouveau", date(2026, 12, 8), "WhatsApp%20Image%202026-09-15%20at%2018.25.06-EgfEmge234BmEkzlsqHuyjPXjLi9Vw.jpeg"),
    ("Maison", "Lampe électrique anti-moustiques", "Lumière efficace, prix avec taxes incluses.", 2200, 21, 29, "#e2dff0", "Prix TTC", date(2026, 12, 12), "WhatsApp%20Image%202026-09-15%20at%2004.04.24-1JRJxQTkHmZ3RCM8bBPEx2owFYWViL.jpeg"),
]


class Command(BaseCommand):
    help = "Charge les 8 produits de démonstration de la maquette d'origine."

    def handle(self, *args, **options):
        created = 0
        for cat, name, desc, price, ordered, stock, accent, tag, arrival, img in PRODUCTS:
            category, _ = Category.objects.get_or_create(name=cat)
            _, was_created = Product.objects.get_or_create(
                name=name,
                defaults=dict(
                    category=category, description=desc, price=price, ordered_count=ordered,
                    stock=stock, accent=accent, tag=tag, arrival_date=arrival, image_url=BLOB + img,
                ),
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f"{created} produit(s) créé(s)."))
