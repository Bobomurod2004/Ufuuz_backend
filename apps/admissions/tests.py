from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import (
    ApplicationCV,
    ApplicationDiploma,
    ApplicationIdentityDocument,
    ApplicationLanguageCertificate,
    ApplicationMotivationLetter,
    ApplicationTranscript,
    StudentApplication,
)


def _pdf(name, content=b'content'):
    return SimpleUploadedFile(name, content, content_type='application/pdf')


class StudentApplicationApiTests(TestCase):
    endpoint = '/api/v1/admissions/applications/'

    def _required_files(self):
        return {
            'identity_document_files': [_pdf('passport.pdf', b'passport-scan')],
            'diploma_files': [_pdf('diploma.pdf', b'diploma-content')],
        }

    def test_can_create_application_with_multiple_files(self):
        payload = {
            'first_name': 'Ali',
            'last_name': 'Valiyev',
            'middle_name': 'Karimovich',
            'passport_series': 'ab',
            'passport_number': '1234567',
            'phone_number': '+998901234567',
            'cv_files': [_pdf('cv.pdf', b'cv-content')],
            'motivation_letter_files': [_pdf('letter.pdf', b'letter')],
            'identity_document_files': [_pdf('passport.pdf', b'passport')],
            'language_certificate_files': [
                _pdf('lang-1.pdf', b'lang-cert-1'),
                _pdf('lang-2.pdf', b'lang-cert-2'),
            ],
            'transcript_files': [_pdf('transcript.pdf', b'transcript')],
            'diploma_files': [
                _pdf('diploma-1.pdf', b'diploma-1'),
                _pdf('diploma-2.pdf', b'diploma-2'),
            ],
        }

        response = self.client.post(self.endpoint, data=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(StudentApplication.objects.count(), 1)

        application = StudentApplication.objects.first()
        self.assertEqual(application.passport_series, 'AB')
        self.assertEqual(application.cvs.count(), 1)
        self.assertEqual(application.motivation_letters.count(), 1)
        self.assertEqual(application.identity_documents.count(), 1)
        self.assertEqual(application.language_certificates.count(), 2)
        self.assertEqual(application.transcripts.count(), 1)
        self.assertEqual(application.diplomas.count(), 2)
        self.assertEqual(application.status, StudentApplication.Status.PENDING)
        self.assertEqual(
            response.json()['status'],
            StudentApplication.Status.PENDING,
        )

    def test_passport_series_must_be_two_letters(self):
        payload = {
            'first_name': 'Ali',
            'last_name': 'Valiyev',
            'middle_name': 'Karimovich',
            'passport_series': 'ABC',
            'passport_number': '1234567',
            'phone_number': '+998901234567',
            **self._required_files(),
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
            **self._required_files(),
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
            'identity_document_files': [_pdf('passport.pdf', b'passport')],
        }
        response = self.client.post(self.endpoint, data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('diploma_files', response.json())

    def test_identity_document_is_required(self):
        payload = {
            'first_name': 'Ali',
            'last_name': 'Valiyev',
            'middle_name': 'Karimovich',
            'passport_series': 'AB',
            'passport_number': '1234567',
            'phone_number': '+998901234567',
            'diploma_files': [_pdf('diploma.pdf', b'diploma')],
        }
        response = self.client.post(self.endpoint, data=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('identity_document_files', response.json())


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
        ApplicationCV.objects.create(
            application=self.application,
            file=_pdf('cv.pdf', b'cv-content'),
        )
        ApplicationMotivationLetter.objects.create(
            application=self.application,
            file=_pdf('letter.pdf', b'letter-content'),
        )
        ApplicationIdentityDocument.objects.create(
            application=self.application,
            file=_pdf('passport.pdf', b'passport-scan'),
        )
        ApplicationLanguageCertificate.objects.create(
            application=self.application,
            file=_pdf('lang.pdf', b'lang-cert'),
        )
        ApplicationTranscript.objects.create(
            application=self.application,
            file=_pdf('transcript.pdf', b'transcript'),
        )
        ApplicationDiploma.objects.create(
            application=self.application,
            file=_pdf('diploma.pdf', b'diploma-content'),
        )

    def test_staff_admin_can_view_admissions_changelist(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse('admin:admissions_studentapplication_changelist')
        )
        self.assertEqual(response.status_code, 200)

    def test_staff_admin_cannot_access_other_model_admins(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse('admin:common_history_changelist')
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_admin_cannot_delete_application(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(
            reverse(
                'admin:admissions_studentapplication_delete',
                args=[self.application.pk],
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_admin_can_view_uploaded_documents(self):
        self.client.force_login(self.staff_user)
        change_url = reverse(
            'admin:admissions_studentapplication_change',
            args=[self.application.pk],
        )
        response = self.client.get(change_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cv')
        self.assertContains(response, 'diploma')

    def test_superuser_still_has_full_access(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse('admin:common_history_changelist')
        )
        self.assertEqual(response.status_code, 200)
