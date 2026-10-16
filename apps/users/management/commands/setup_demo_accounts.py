"""Create local-only accounts and sample dashboard data for demos."""

from datetime import date, time, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from attendance.models import AttendanceRequest
from events.models import Event
from users.models import CustomUser


DEMO_ACCOUNTS = {
    'demo.student': {
        'password': 'StudentDemo123!',
        'first_name': 'Riya',
        'last_name': 'Patel',
        'email': 'demo.student@example.invalid',
        'role': CustomUser.Role.STUDENT,
        'division': 'A',
        'grade': CustomUser.Grade.TY,
        'student_id': 'TYCS-301',
        'department': 'Computer Science',
    },
    'demo.coordinator': {
        'password': 'CoordinatorDemo123!',
        'first_name': 'Anil',
        'last_name': 'Iyer',
        'email': 'demo.coordinator@example.invalid',
        'role': CustomUser.Role.COORDINATOR,
        'department': 'Student Activities',
    },
    'demo.teacher': {
        'password': 'TeacherDemo123!',
        'first_name': 'Neha',
        'last_name': 'Kulkarni',
        'email': 'demo.teacher@example.invalid',
        'role': CustomUser.Role.TEACHER,
        'division': 'A',
        'department': 'Computer Science',
    },
}


class Command(BaseCommand):
    help = 'Create or refresh the three local AttendEase demo accounts and dashboard data.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Demo accounts may only be created when DEBUG=True.')

        users = {}
        for username, values in DEMO_ACCOUNTS.items():
            password = values['password']
            defaults = {key: value for key, value in values.items() if key != 'password'}
            user, _created = CustomUser.objects.get_or_create(
                username=username,
                defaults=defaults,
            )
            for key, value in defaults.items():
                setattr(user, key, value)
            user.is_active = True
            user.set_password(password)
            user.save()
            users[username] = user

        today = date.today()
        coordinator = users['demo.coordinator']
        teacher = users['demo.teacher']
        student = users['demo.student']

        events = {}
        event_rows = [
            ('Campus Innovation Hackathon', today + timedelta(days=14), time(9, 0), 'Innovation Hub'),
            ('AI Builders Workshop', today + timedelta(days=21), time(10, 30), 'Seminar Hall'),
            ('Designverse Meetup', today - timedelta(days=5), time(14, 0), 'Pune Innovation Center'),
        ]
        for name, event_date, event_time, venue in event_rows:
            event, _created = Event.objects.update_or_create(
                organizer=coordinator,
                name=name,
                defaults={
                    'description': f'{name}: a sample event for the AttendEase role dashboards.',
                    'date': event_date,
                    'time': event_time,
                    'venue': venue,
                    'is_active': True,
                },
            )
            events[name] = event

        students = [
            (student, 'TYCS-301'),
            (self._student('demo.aarav', 'Aarav', 'Mehta', 'TYCS-318', 'A'), 'TYCS-318'),
            (self._student('demo.diya', 'Diya', 'Shah', 'TYCS-327', 'A'), 'TYCS-327'),
        ]
        request_rows = [
            (students[0][0], events['Campus Innovation Hackathon'], 'pending', 'Presenting our capstone prototype.'),
            (students[1][0], events['Campus Innovation Hackathon'], 'coordinator_approved', 'Participating as a team member.'),
            (students[2][0], events['AI Builders Workshop'], 'teacher_approved', 'Building skills in applied AI.'),
        ]
        for request_student, event, status, reason in request_rows:
            defaults = {
                'event_type': AttendanceRequest.EventType.COORDINATOR,
                'reason': reason,
                'status': status,
                'coordinator': coordinator if status != AttendanceRequest.Status.PENDING else None,
                'coordinator_remarks': 'Approved for the event.' if status != AttendanceRequest.Status.PENDING else '',
                'teacher': teacher if status == AttendanceRequest.Status.TEACHER_APPROVED else None,
                'teacher_remarks': 'Approved. Please confirm attendance.' if status == AttendanceRequest.Status.TEACHER_APPROVED else '',
                'is_attended': status == AttendanceRequest.Status.TEACHER_APPROVED,
            }
            AttendanceRequest.objects.update_or_create(
                student=request_student,
                event=event,
                defaults=defaults,
            )

        external = AttendanceRequest.objects.filter(
            student=student,
            event_type=AttendanceRequest.EventType.OPEN,
            external_event_name='Designverse Meetup',
        ).first()
        if external is None:
            AttendanceRequest.objects.create(
                student=student,
                event_type=AttendanceRequest.EventType.OPEN,
                status=AttendanceRequest.Status.TEACHER_APPROVED,
                reason='Sharing a student design project at the meetup.',
                external_event_name='Designverse Meetup',
                external_college_name='Pune Innovation Center',
                external_event_location='Main Auditorium',
                external_event_date=events['Designverse Meetup'].date,
                external_event_time=events['Designverse Meetup'].time,
                teacher=teacher,
                teacher_remarks='Approved for participation.',
                is_attended=True,
            )
        else:
            external.status = AttendanceRequest.Status.TEACHER_APPROVED
            external.teacher = teacher
            external.teacher_remarks = 'Approved for participation.'
            external.is_attended = True
            external.save()

        self.stdout.write(self.style.SUCCESS('Demo accounts are ready:'))
        for username, values in DEMO_ACCOUNTS.items():
            self.stdout.write(f"  {values['role']}: {username} / {values['password']}")
        self.stdout.write('Sample requests and events were created for all three dashboards.')

    @staticmethod
    def _student(username, first_name, last_name, student_id, division):
        user, _created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'role': CustomUser.Role.STUDENT,
                'division': division,
                'grade': CustomUser.Grade.TY,
                'student_id': student_id,
                'department': 'Computer Science',
                'email': f'{username}@example.invalid',
            },
        )
        return user
