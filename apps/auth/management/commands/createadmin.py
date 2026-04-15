from django.core.management import BaseCommand
from apps.auth.models import User

class Command(BaseCommand):
    help = "Bu funksita DEMO admin user yaratish uchun."

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="superadmin").exists():
            User.objects.create_superuser(
                username="superadmin", password="superadmin02"
            )
            self.stdout.write("Superuser yaratildi!")
        else:
            self.stdout.write("Allaqachon bor.")