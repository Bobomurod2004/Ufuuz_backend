from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import (
    ApplicationCertificate,
    ApplicationDiploma,
    StudentApplication,
)


class StudentApplicationApiTests(TestCase):
    endpoint = '/api/v1/admissions/applications/'

    def test_can_create_application_with_multiple_files(self):
        diploma_1 = SimpleUploadedFile('diplom-1.pdf', b'diploma-one', content_type='application/pdf')
        diploma_2 = SimpleUploadedFile('diplom-2.pdf', b'diploma-two', content_type='application/pdf')
        certificate_1 = SimpleUploadedFile(
            'certificate-1.pdf',
            b'certificate-one',
            content_type='application/pdf',
        )

        payload = {
            'first_name': 'Ali',
            'last_name': 'Valiyev',
            'middle_name': 'Karimovich',
            'passport_series': 'ab',
            'passport_number': '1234567',
            'phone_number': '+998901234567',
            'diploma_files': [diploma_1, diploma_2],
            'certificate_files': [certificate_1],
        }

        response = self.client.post(self.endpoint, data=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(StudentApplication.objects.count(), 1)
        self.assertEqual(ApplicationDiploma.objects.count(), 2)
        self.assertEqual(ApplicationCertificate.objects.count(), 1)

        application = StudentApplication.objects.first()
        self.assertIsNotNone(application)
        self.assertEqual(application.passport_series, 'AB')
        self.assertEqual(application.status, StudentApplication.Status.PENDING)
        self.assertEqual(response.json()['status'], StudentApplication.Status.PENDING)

    def test_passport_series_must_be_two_letters(self):
        payload = {
            'first_name': 'Ali',
            'last_name': 'Valiyev',
            'middle_name': 'Karimovich',
            'passport_series': 'ABC',
            'passport_number': '1234567',
            'phone_number': '+998901234567',
            'diploma_files': [
                SimpleUploadedFile('diplom.pdf', b'diploma', content_type='application/pdf')
            ],
        }

        response = self.client.post(self.endpoint, data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('passport_series', response.json())

    def test_passport_number_must_be_7_digits_string(self):
        payload = {
            'first_name': 'Ali',
            'last_name': 'Valiyev',
            'middle_name': 'Karimovich',
            'passport_series': 'AB',
            'passport_number': '12A4567',
            'phone_number': '+998901234567',
            'diploma_files': [
                SimpleUploadedFile('diplom.pdf', b'diploma', content_type='application/pdf')
            ],
        }

        response = self.client.post(self.endpoint, data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('passport_number', response.json())

    def test_diploma_file_is_required(self):
        payload = {
            'first_name': 'Ali',
            'last_name': 'Valiyev',
            'middle_name': 'Karimovich',
            'passport_series': 'AB',
            'passport_number': '1234567',
            'phone_number': '+998901234567',
        }

        response = self.client.post(self.endpoint, data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('diploma_files', response.json())


class StudentApplicationAdminPermissionTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.superuser = user_model.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='pass12345',
        )
        self.staff_user = user_model.objects.create_user(
            username='admissions_admin',
            email='admissions_admin@example.com',
            password='pass12345',
            is_staff=True,
        )
        self.application = StudentApplication.objects.create(
            first_name='Ali',
            last_name='Valiyev',
            middle_name='Karimovich',
            passport_series='AB',
            passport_number='1234567',
            phone_number='+998901234567',
        )
        ApplicationDiploma.objects.create(
            application=self.application,
            file=SimpleUploadedFile('diploma.pdf', b'diploma', content_type='application/pdf'),
        )
        ApplicationCertificate.objects.create(
            application=self.application,
            file=SimpleUploadedFile(
                'certificate.pdf',
                b'certificate',
                content_type='application/pdf',
            ),
        )

    def test_staff_admin_can_view_admissions_changelist(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('admin:admissions_studentapplication_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_staff_admin_cannot_access_other_model_admins(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('admin:common_history_changelist'))
        self.assertEqual(response.status_code, 403)

    def test_staff_admin_cannot_change_application(self):
        self.client.force_login(self.staff_user)
        change_url = reverse('admin:admissions_studentapplication_change', args=[self.application.pk])
        response = self.client.post(
            change_url,
            data={
                'first_name': 'Ali',
                'last_name': 'Valiyev',
                'middle_name': 'Karimovich',
                'passport_series': 'AB',
                'passport_number': '1234567',
                'phone_number': '+998901234567',
                'status': StudentApplication.Status.ACCEPTED,
            },
        )
        self.assertEqual(response.status_code, 403)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, StudentApplication.Status.PENDING)

    def test_staff_admin_can_view_uploaded_documents_read_only(self):
        self.client.force_login(self.staff_user)
        change_url = reverse('admin:admissions_studentapplication_change', args=[self.application.pk])
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'diploma')
        self.assertContains(response, 'certificate')
        self.assertNotContains(response, 'name="_save"')

    def test_staff_admin_cannot_delete_application(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse('admin:admissions_studentapplication_delete', args=[self.application.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_superuser_still_has_full_access(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('admin:common_history_changelist'))
        self.assertEqual(response.status_code, 200)
