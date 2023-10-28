import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone


class Command(BaseCommand):
    help = 'sends an email notification to users registered more than N days that are not enrolled to any courses yet'

    def add_arguments(self, parser):
        parser.add_agrument('--days', dest='days', type=int)

    def handle(self, *args, **options):
        emails = []
        subject = 'Start gaining knowledge today!'
        date_joined = timezone.now().today() - datetime.timedelta(days=options['days'] or 0)

        # get users that didn't enroll into any course
        users = (User.objects.annotate(course_count=Count('courses_joined')).
                 filter(course_count=0, date_joined__date__lte=date_joined))

        for user in users:
            message = f"Dear {user.first_name}, " \
                      "We noticed that you didn't enroll in any courses yet." \
                      "What are you waiting for? Start develop your future today!"
            emails.append((subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]))

        send_mass_mail(emails)
        self.stdout.write(f'Sent {len(emails)} reminders.')
