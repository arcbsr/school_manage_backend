from typing import List
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config as env_config
from core.models import Branch, Shift, SchoolClass, Section, Subject


class Command(BaseCommand):
    help = "Seed default admin, branch, shifts, classes, sections, subjects"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding defaults..."))

        # Admin
        email = env_config('ADMIN_EMAIL', default='')
        explicit_username = env_config('ADMIN_USERNAME', default='').strip()
        username = explicit_username or (email.split('@', 1)[0] if email else 'admin')
        password = env_config('ADMIN_PASSWORD', default='admin123')
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'"))
        else:
            self.stdout.write(f"Superuser '{username}' already exists")

        # Branch
        branch, _ = Branch.objects.get_or_create(name='Khilgaon', defaults={'address': '', 'is_active': True})
        self.stdout.write(f"Branch: {branch}")

        # Shifts
        from datetime import time
        day, _ = Shift.objects.get_or_create(name='Day', defaults={'start_time': time(8, 0), 'end_time': time(14, 0), 'is_active': True})
        afternoon, _ = Shift.objects.get_or_create(name='Afternoon', defaults={'start_time': time(14, 0), 'end_time': time(20, 0), 'is_active': True})
        self.stdout.write(f"Shifts: {day}, {afternoon}")

        # Classes (Play to 10)
        class_names: List[str] = ['Play', 'Nursery', 'KG', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
        created_classes: List[SchoolClass] = []
        for cname in class_names:
            sc, created = SchoolClass.objects.get_or_create(name=cname, branch=branch, defaults={'is_active': True})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created class {sc}"))
            created_classes.append(sc)

        # Sections (A, B)
        for sc in created_classes:
            for sec_name in ['A', 'B']:
                Section.objects.get_or_create(name=sec_name, school_class=sc, defaults={'is_active': True})
        self.stdout.write("Sections A, B ensured for each class")

        # Subjects (optional baseline)
        for name, code in [('Math', 'MTH'), ('English', 'ENG'), ('Science', 'SCI')]:
            Subject.objects.get_or_create(name=name, defaults={'code': code, 'is_active': True})
        self.stdout.write("Subjects ensured: Math, English, Science")

        self.stdout.write(self.style.SUCCESS("Seeding complete."))


