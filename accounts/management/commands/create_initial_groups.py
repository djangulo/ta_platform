"""Creates groups and base permissions for each group"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission

from accounts.models import ModGroup as Group
from django.db.models import Q

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        superusers, superusers_created = (
            Group.objects.get_or_create(name='superuser',
                                        is_supervisor=True,
                                        is_admin=True))
        if superusers_created:
            for perm in Permission.objects.all():
                superusers.permissions.add(perm)
            superusers.save()

        admins, admins_created = (
            Group.objects.get_or_create(name='admin',
                                        is_supervisor=True,
                                        is_admin=True))
        # if admins_created:
            # for p in Permission.objects.all().filter(
            #         Q(name__icontains='entry') |
            #         Q(name__icontains='image') |
            #         Q(name__icontains='user')
            #     ).exclude(
            #         Q(name__icontains='log')
            #     ):
            #     admins.permissions.add(p)
            # admins.save()
        supervisor, supervisor_created = (
            Group.objects.get_or_create(name='supervisor',
                                        is_supervisor=True,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % supervisor, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        human_resources, human_resources_created = (
            Group.objects.get_or_create(name='human_resources',
                                        is_supervisor=False,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % human_resources, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        recruiter, recruiter_created = (
            Group.objects.get_or_create(name='recruiter',
                                        is_supervisor=False,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % recruiter, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        sourcer, sourcer_created = (
            Group.objects.get_or_create(name='sourcer',
                                        is_supervisor=False,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % sourcer, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        hiring_manager, hiring_manager_created = (
            Group.objects.get_or_create(name='hiring_manager',
                                        is_supervisor=False,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % hiring_manager, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        lab_manager, lab_manager_created = (
            Group.objects.get_or_create(name='lab_manager',
                                        is_supervisor=False,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % lab_manager, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        reporting, reporting_created = (
            Group.objects.get_or_create(name='reporting',
                                        is_supervisor=False,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % reporting, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        payroll, payroll_created = (
            Group.objects.get_or_create(name='payroll',
                                        is_supervisor=False,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % payroll, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        employee, employee_created = (
            Group.objects.get_or_create(name='employee',
                                        is_supervisor=False,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % employee, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        candidate, candidate_created = (
            Group.objects.get_or_create(name='candidate',
                                        is_supervisor=False,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % candidate, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        ANON, ANON_created = (
            Group.objects.get_or_create(name='ANON',
                                        is_supervisor=True,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % ANON, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        BOT, BOT_created = (
            Group.objects.get_or_create(name='BOT',
                                        is_supervisor=True,
                                        is_admin=False))
        self.stdout.write(" Creating group %s..." % BOT, ending="")
        self.stdout.write(self.style.SUCCESS(" OK"))
        self.stdout.flush()
        # if staff_created:
        #     for p in Permission.objects.all().filter(
        #             Q(name__icontains='entry') |
        #             Q(name__icontains='image')
        #         ).exclude(
        #             Q(name__icontains='log') |
        #             Q(name__icontains='publish') |
        #             Q(name__icontains='delete')
        #         ):
        #         staff.permissions.add(p)
        #     staff.save()
