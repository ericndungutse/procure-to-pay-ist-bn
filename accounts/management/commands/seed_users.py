# accounts/management/commands/create_initial_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Creates initial users (staff, approvers, finance admin) for the application.'

    def handle(self, *args, **options):
        user_model = get_user_model()
        
        # Define roles from the model's TextChoices
        ROLES = {
            'STAFF': "staff",
            'APPROVER_L1': "approver-level-1",
            'APPROVER_L2': "approver-level-2",
            'FINANCE': "finance",
        }
        
        users_to_create = [
            {'email': 'staff@company.com', 'pwd': 'StaffPassword123', 'name': 'Staff Member', 'username': 'staff_member', 'role': ROLES['STAFF'], 'is_superuser': False},
            {'email': 'approver1@company.com', 'pwd': 'ApproverPassword123', 'name': 'A1 Manager', 'username': 'approver_one', 'role': ROLES['APPROVER_L1'], 'is_superuser': False},
            {'email': 'approver2@company.com', 'pwd': 'ApproverPassword123', 'name': 'A2 Director', 'username': 'approver_two', 'role': ROLES['APPROVER_L2'], 'is_superuser': False},
            {'email': 'finance_admin@company.com', 'pwd': 'SuperAdmin123', 'name': 'Finance Admin', 'username': 'finance_admin', 'role': ROLES['FINANCE'], 'is_superuser': True},
        ]

        for user_data in users_to_create:
            if user_model.objects.filter(email=user_data['email']).exists():
                self.stdout.write(self.style.WARNING(f"User {user_data['email']} already exists. Skipping."))
                continue

            try:
                if user_data['is_superuser']:
                    user_model.objects.create_superuser(
                        email=user_data['email'],
                        password=user_data['pwd'],
                        full_name=user_data['name'],
                        username=user_data['username'],
                        role=user_data['role']
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created Superuser: {user_data['email']}"))
                else:
                    user_model.objects.create_user(
                        email=user_data['email'],
                        password=user_data['pwd'],
                        full_name=user_data['name'],
                        username=user_data['username'],
                        role=user_data['role']
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created User: {user_data['email']}"))
            
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"Database error creating {user_data['email']}: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))