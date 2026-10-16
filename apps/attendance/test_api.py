"""Integration tests for the role-scoped dashboard APIs."""

import json

from django.test import TestCase
from django.urls import reverse

from events.models import Event
from users.models import CustomUser
from .models import AttendanceRequest


class DashboardApiTests(TestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            username='student-a',
            password='test-password',
            first_name='Ari',
            last_name='Student',
            role=CustomUser.Role.STUDENT,
            division='A',
            student_id='A-100',
        )
        self.other_student = CustomUser.objects.create_user(
            username='student-b',
            password='test-password',
            role=CustomUser.Role.STUDENT,
            division='B',
        )
        self.coordinator = CustomUser.objects.create_user(
            username='coordinator-a',
            password='test-password',
            role=CustomUser.Role.COORDINATOR,
        )
        self.other_coordinator = CustomUser.objects.create_user(
            username='coordinator-b',
            password='test-password',
            role=CustomUser.Role.COORDINATOR,
        )
        self.teacher = CustomUser.objects.create_user(
            username='teacher-a',
            password='test-password',
            role=CustomUser.Role.TEACHER,
            division='A',
        )
        self.event = Event.objects.create(
            name='College Workshop',
            description='Workshop description',
            date='2026-11-10',
            time='10:00',
            venue='Main Hall',
            organizer=self.coordinator,
        )
        self.other_event = Event.objects.create(
            name='Other Workshop',
            description='Another workshop',
            date='2026-11-11',
            time='11:00',
            venue='Other Hall',
            organizer=self.other_coordinator,
        )

    def make_request(self, student=None, event=None, status=None, **fields):
        return AttendanceRequest.objects.create(
            student=student or self.student,
            event=event or self.event,
            event_type=AttendanceRequest.EventType.COORDINATOR,
            reason='I will participate in the event.',
            status=status or AttendanceRequest.Status.PENDING,
            **fields,
        )

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_session_returns_real_role_and_profile(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse('api_session'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['role'], 'student')
        self.assertEqual(response.json()['user']['full_name'], 'Ari Student')
        self.assertTrue(response.cookies.get('csrftoken'))

    def test_react_app_requires_login(self):
        anonymous_response = self.client.get(reverse('react_app'))
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertIn('/auth/login/', anonymous_response.url)

    def test_dashboard_data_is_scoped_to_signed_in_role(self):
        own = self.make_request(status=AttendanceRequest.Status.COORDINATOR_APPROVED)
        other_event_request = self.make_request(event=self.other_event)
        other_division_request = self.make_request(
            student=self.other_student,
            event=self.other_event,
        )

        self.client.force_login(self.coordinator)
        coordinator_response = self.client.get(reverse('api_dashboard'))
        self.assertEqual(
            [item['id'] for item in coordinator_response.json()['requests']],
            [own.pk],
        )

        self.client.force_login(self.teacher)
        teacher_response = self.client.get(reverse('api_dashboard'))
        teacher_ids = {item['id'] for item in teacher_response.json()['requests']}
        self.assertIn(own.pk, teacher_ids)
        self.assertNotIn(other_division_request.pk, teacher_ids)
        self.assertNotIn(other_event_request.pk, teacher_ids)

        self.client.force_login(self.student)
        student_response = self.client.get(reverse('api_dashboard'))
        student_ids = {item['id'] for item in student_response.json()['requests']}
        self.assertEqual(student_ids, {own.pk, other_event_request.pk})
        self.assertNotIn(other_division_request.pk, student_ids)

    def test_student_can_submit_open_request_directly_to_teacher(self):
        self.client.force_login(self.student)

        response = self.post_json(reverse('api_create_request'), {
            'event_type': 'open',
            'reason': 'I am presenting a project.',
            'external_event_name': 'External Summit',
            'external_college_name': 'Partner College',
            'external_event_location': 'Auditorium',
            'external_event_date': '2026-12-05',
            'external_event_time': '09:30',
        })

        self.assertEqual(response.status_code, 201)
        created = AttendanceRequest.objects.get(pk=response.json()['request']['id'])
        self.assertEqual(created.status, AttendanceRequest.Status.COORDINATOR_APPROVED)
        self.assertEqual(created.event_type, AttendanceRequest.EventType.OPEN)

    def test_review_and_attendance_flow_enforces_role_and_division(self):
        item = self.make_request()

        self.client.force_login(self.other_coordinator)
        forbidden_review = self.post_json(
            reverse('api_review_request', args=[item.pk]),
            {'action': 'approve', 'remarks': ''},
        )
        self.assertEqual(forbidden_review.status_code, 404)

        self.client.force_login(self.coordinator)
        coordinator_review = self.post_json(
            reverse('api_review_request', args=[item.pk]),
            {'action': 'approve', 'remarks': 'Approved for the event.'},
        )
        self.assertEqual(coordinator_review.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.status, AttendanceRequest.Status.COORDINATOR_APPROVED)

        self.client.force_login(self.teacher)
        teacher_review = self.post_json(
            reverse('api_review_request', args=[item.pk]),
            {'action': 'approve', 'remarks': 'Final approval.'},
        )
        self.assertEqual(teacher_review.status_code, 200)

        mark_response = self.post_json(
            reverse('api_mark_attendance', args=[item.pk]),
            {},
        )
        self.assertEqual(mark_response.status_code, 200)
        item.refresh_from_db()
        self.assertTrue(item.is_attended)

    def test_coordinator_can_create_event_but_student_cannot(self):
        payload = {
            'name': 'New Event',
            'description': 'A campus event',
            'date': '2026-12-10',
            'time': '13:15',
            'venue': 'Auditorium',
            'is_active': True,
        }
        self.client.force_login(self.student)
        denied = self.post_json(reverse('api_events'), payload)
        self.assertEqual(denied.status_code, 403)

        self.client.force_login(self.coordinator)
        created = self.post_json(reverse('api_events'), payload)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()['event']['organizer'], self.coordinator.get_full_name() or self.coordinator.username)

    def test_teacher_month_filter_rejects_invalid_month(self):
        self.client.force_login(self.teacher)

        response = self.client.get(reverse('api_dashboard'), {'month': '13'})

        self.assertEqual(response.status_code, 400)
