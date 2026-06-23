import io
import os
import zipfile

from django.contrib import admin, messages
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    ApplicationCertificate,
    ApplicationDiploma,
    ApplicationDiplomaSupplement,
    ApplicationPassportFile,
    ApplicationPdf,
    StudentApplication,
)

# ── Constants ─────────────────────────────────────────────────────────────────

_STATUS_STYLE = {
    StudentApplication.Status.PENDING: (
        'background:#fef3c7;color:#92400e;border:1px solid #fcd34d'
    ),
    StudentApplication.Status.ACCEPTED: (
        'background:#d1fae5;color:#065f46;border:1px solid #6ee7b7'
    ),
    StudentApplication.Status.REJECTED: (
        'background:#fee2e2;color:#991b1b;border:1px solid #fca5a5'
    ),
}
_STATUS_LABEL = {
    StudentApplication.Status.PENDING: '⏳ Kutilmoqda',
    StudentApplication.Status.ACCEPTED: '✅ Qabul qilindi',
    StudentApplication.Status.REJECTED: '❌ Rad etildi',
}
_DOC_GROUPS = (
    ('application_pdfs', 'ariza_pdf'),
    ('diploma_supplements', 'diplom_ilovasi'),
    ('passport_files', 'pasport'),
    ('diplomas', 'diplom'),
    ('certificates', 'sertifikat'),
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_zip(queryset):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for app in queryset.prefetch_related(
            'application_pdfs', 'diploma_supplements',
            'passport_files', 'diplomas', 'certificates',
        ):
            folder = (
                f"{app.last_name}_{app.first_name}"
                f"_{app.passport_series}{app.passport_number}"
            )
            for related, subfolder in _DOC_GROUPS:
                for i, doc in enumerate(getattr(app, related).all(), 1):
                    if not doc.file:
                        continue
                    try:
                        name = os.path.basename(doc.file.name)
                        with doc.file.open('rb') as f:
                            zf.writestr(f"{folder}/{subfolder}/{i}_{name}", f.read())
                    except (FileNotFoundError, OSError):
                        pass
    buffer.seek(0)
    return buffer


# ── Inline classes ────────────────────────────────────────────────────────────

class _ReadOnlyDocumentInline(admin.TabularInline):
    extra = 0
    can_delete = False
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)


class ApplicationPdfInline(_ReadOnlyDocumentInline):
    model = ApplicationPdf
    verbose_name = 'Ariza PDF'
    verbose_name_plural = '📄 Ariza PDF hujjatlari'
    readonly_fields = ('file', 'created_at')
    fields = ('file', 'created_at')


class ApplicationDiplomaInline(_ReadOnlyDocumentInline):
    model = ApplicationDiploma
    verbose_name = 'Diplom'
    verbose_name_plural = '🎓 Diplomlar'
    readonly_fields = ('file', 'created_at')
    fields = ('file', 'created_at')


class ApplicationDiplomaSupplementInline(_ReadOnlyDocumentInline):
    model = ApplicationDiplomaSupplement
    verbose_name = 'Diplom ilovasi'
    verbose_name_plural = '📎 Diplom ilovasi fayllari'
    readonly_fields = ('file', 'created_at')
    fields = ('file', 'created_at')


class ApplicationPassportFileInline(_ReadOnlyDocumentInline):
    model = ApplicationPassportFile
    verbose_name = 'Pasport fayli'
    verbose_name_plural = '🪪 Pasport fayllari'
    readonly_fields = ('file', 'created_at')
    fields = ('file', 'created_at')


class ApplicationCertificateInline(_ReadOnlyDocumentInline):
    model = ApplicationCertificate
    verbose_name = 'Sertifikat'
    verbose_name_plural = '📜 Sertifikatlar'
    readonly_fields = ('file', 'created_at')
    fields = ('file', 'created_at')


# ── Main ModelAdmin ───────────────────────────────────────────────────────────

@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name_display',
        'phone_number',
        'email',
        'status_badge',
        'created_at',
        'zip_button',
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'first_name', 'last_name', 'middle_name',
        'passport_series', 'passport_number',
        'phone_number', 'email',
    )
    ordering = ('-created_at',)
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ['mark_accepted', 'mark_rejected', 'download_documents_zip', 'send_email_action']
    inlines = [
        ApplicationPdfInline,
        ApplicationDiplomaSupplementInline,
        ApplicationPassportFileInline,
        ApplicationDiplomaInline,
        ApplicationCertificateInline,
    ]

    _always_readonly = (
        'first_name', 'last_name', 'middle_name',
        'passport_series', 'passport_number',
        'phone_number', 'email',
        'reviewed_by', 'reviewed_at',
        'created_at', 'updated_at',
    )

    def get_readonly_fields(self, request, obj=None):
        return self._always_readonly

    def get_fieldsets(self, request, obj=None):
        return (
            ('👤 Ariza egasi', {
                'fields': (
                    ('last_name', 'first_name', 'middle_name'),
                    ('passport_series', 'passport_number'),
                    ('phone_number', 'email'),
                ),
            }),
            ('📋 Holat', {
                'fields': (
                    'status',
                    'review_note',
                    ('reviewed_by', 'reviewed_at'),
                ),
            }),
            ('🕒 Vaqt', {
                'fields': (('created_at', 'updated_at'),),
                'classes': ('collapse',),
            }),
        )

    # ── Custom URLs ───────────────────────────────────────────────────

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                '<int:pk>/zip/',
                self.admin_site.admin_view(self._download_single_zip),
                name='admissions_application_zip',
            ),
            path(
                'send-email/',
                self.admin_site.admin_view(self._send_email_view),
                name='admissions_application_send_email',
            ),
        ]
        return custom + urls

    def _download_single_zip(self, request, pk):
        qs = StudentApplication.objects.filter(pk=pk)
        buf = _build_zip(qs)
        app = qs.first()
        fname = (
            f"{app.last_name}_{app.first_name}"
            f"_{app.passport_series}{app.passport_number}.zip"
        ) if app else "hujjatlar.zip"
        resp = HttpResponse(buf.getvalue(), content_type='application/zip')
        resp['Content-Disposition'] = f'attachment; filename="{fname}"'
        return resp

    def _send_email_view(self, request):
        ids = request.POST.getlist('ids') or request.GET.getlist('ids')
        qs = StudentApplication.objects.filter(pk__in=ids)

        recipients = [a for a in qs if a.email]
        no_email_apps = [a for a in qs if not a.email]

        if request.method == 'POST' and 'subject' in request.POST:
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()
            sent = 0
            failed = 0
            for app in recipients:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=None,
                        recipient_list=[app.email],
                        fail_silently=False,
                    )
                    sent += 1
                except Exception:
                    failed += 1
            if sent:
                self.message_user(
                    request,
                    f'✅ {sent} ta foydalanuvchiga email muvaffaqiyatli yuborildi.',
                    messages.SUCCESS,
                )
            if failed:
                self.message_user(
                    request,
                    f'⚠️ {failed} ta emailni yuborishda xatolik yuz berdi.',
                    messages.WARNING,
                )
            return redirect(reverse('admin:admissions_studentapplication_changelist'))

        # Default email matni
        status_labels = {
            StudentApplication.Status.PENDING: 'ko\'rib chiqilmoqda',
            StudentApplication.Status.ACCEPTED: 'qabul qilindi',
            StudentApplication.Status.REJECTED: 'rad etildi',
        }
        if len(recipients) == 1:
            app = recipients[0]
            label = status_labels.get(app.status, app.status)
            default_subject = f"Arizangiz holati — {label}"
            default_message = (
                f"Hurmatli {app.first_name} {app.last_name},\n\n"
                f"Sizning arizangiz holati: {label.upper()}.\n\n"
                "Qo'shimcha ma'lumot uchun biz bilan bog'laning.\n\n"
                "Hurmat bilan,\nUFU Qabul komissiyasi"
            )
        else:
            default_subject = "Arizangiz holati haqida"
            default_message = (
                "Hurmatli ariza egasi,\n\n"
                "Arizangiz ko'rib chiqildi. Qo'shimcha ma'lumot uchun biz bilan bog'laning.\n\n"
                "Hurmat bilan,\nUFU Qabul komissiyasi"
            )

        return render(request, 'admin/admissions/send_email.html', {
            'title': 'Email yuborish',
            'recipients': recipients,
            'no_email_apps': no_email_apps,
            'selected_ids': ids,
            'default_subject': default_subject,
            'default_message': default_message,
            'opts': StudentApplication._meta,
        })

    # ── list_display columns ──────────────────────────────────────────

    @admin.display(description='F.I.SH', ordering='last_name')
    def full_name_display(self, obj):
        return format_html(
            '<span style="font-weight:600;">{} {} {}</span>',
            obj.last_name, obj.first_name, obj.middle_name,
        )

    @admin.display(description='Holat', ordering='status')
    def status_badge(self, obj):
        style = _STATUS_STYLE.get(obj.status, '')
        label = _STATUS_LABEL.get(obj.status, obj.status)
        return format_html(
            '<span style="{};padding:3px 10px;border-radius:20px;'
            'font-size:12px;font-weight:600;white-space:nowrap;">{}</span>',
            style, label,
        )

    @admin.display(description='ZIP')
    def zip_button(self, obj):
        url = reverse('admin:admissions_application_zip', args=[obj.pk])
        return format_html(
            '<a href="{}" style="background:#0ea5e9;color:#fff;padding:4px 12px;'
            'border-radius:6px;font-size:12px;font-weight:600;'
            'text-decoration:none;white-space:nowrap;">⬇ ZIP</a>',
            url,
        )

    # ── Actions ───────────────────────────────────────────────────────

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.action(description='✅ Qabul qilindi deb belgilash')
    def mark_accepted(self, request, queryset):
        count = queryset.count()
        queryset.update(
            status=StudentApplication.Status.ACCEPTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f'{count} ta ariza qabul qilindi.')

    @admin.action(description='❌ Rad etildi deb belgilash')
    def mark_rejected(self, request, queryset):
        count = queryset.count()
        queryset.update(
            status=StudentApplication.Status.REJECTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, f'{count} ta ariza rad etildi.')

    @admin.action(description='⬇ Barcha hujjatlarni ZIP yuklab olish')
    def download_documents_zip(self, request, queryset):
        buf = _build_zip(queryset)
        resp = HttpResponse(buf.getvalue(), content_type='application/zip')
        resp['Content-Disposition'] = 'attachment; filename="arizalar_hujjatlari.zip"'
        return resp

    @admin.action(description='📧 Email yuborish')
    def send_email_action(self, request, queryset):
        ids = list(queryset.values_list('pk', flat=True))
        url = reverse('admin:admissions_application_send_email')
        id_params = '&'.join(f'ids={pk}' for pk in ids)
        return redirect(f'{url}?{id_params}')

    # ── Permissions ───────────────────────────────────────────────────

    def _can_access(self, request):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_active and user.is_staff)

    def has_module_permission(self, request):
        return self._can_access(request)

    def has_view_permission(self, request, obj=None):
        return self._can_access(request)

    def has_change_permission(self, request, obj=None):
        return self._can_access(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        user = getattr(request, 'user', None)
        return bool(user and user.is_authenticated and user.is_superuser)
