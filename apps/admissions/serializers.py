from rest_framework import serializers

from .models import (
    ApplicationCertificate,
    ApplicationDiploma,
    ApplicationDiplomaSupplement,
    ApplicationPassportFile,
    ApplicationPdf,
    StudentApplication,
)


class ApplicationDiplomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDiploma
        fields = (
            'id',
            'file',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ApplicationCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationCertificate
        fields = (
            'id',
            'file',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ApplicationPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationPdf
        fields = (
            'id',
            'file',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ApplicationDiplomaSupplementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDiplomaSupplement
        fields = (
            'id',
            'file',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ApplicationPassportFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationPassportFile
        fields = (
            'id',
            'file',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class StudentApplicationSerializer(serializers.ModelSerializer):
    diplomas = ApplicationDiplomaSerializer(many=True, read_only=True)
    certificates = ApplicationCertificateSerializer(many=True, read_only=True)
    application_pdfs = ApplicationPdfSerializer(many=True, read_only=True)
    diploma_supplements = ApplicationDiplomaSupplementSerializer(many=True, read_only=True)
    passport_files = ApplicationPassportFileSerializer(many=True, read_only=True)
    application_pdf_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    diploma_supplement_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    passport_scan_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    diploma_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    certificate_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = StudentApplication
        fields = (
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'passport_series',
            'passport_number',
            'phone_number',
            'application_pdf_files',
            'diploma_supplement_files',
            'passport_scan_files',
            'application_pdfs',
            'diploma_supplements',
            'passport_files',
            'status',
            'diploma_files',
            'certificate_files',
            'diplomas',
            'certificates',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'diplomas',
            'certificates',
            'application_pdfs',
            'diploma_supplements',
            'passport_files',
            'status',
            'created_at',
            'updated_at',
        )

    def validate_passport_series(self, value):
        return value.upper()

    def validate(self, attrs):
        diploma_files = attrs.get('diploma_files', [])
        diploma_supplement_files = attrs.get('diploma_supplement_files', [])
        passport_scan_files = attrs.get('passport_scan_files', [])

        if self.instance is None and not diploma_files:
            raise serializers.ValidationError(
                {'diploma_files': "Kamida bitta diplom fayli yuklanishi kerak."}
            )
        if self.instance is None and not diploma_supplement_files:
            raise serializers.ValidationError(
                {'diploma_supplement_files': "Kamida bitta diplom ilovasi fayli yuklanishi kerak."}
            )
        if self.instance is None and not passport_scan_files:
            raise serializers.ValidationError(
                {'passport_scan_files': "Kamida bitta passport fayli yuklanishi kerak."}
            )
        return attrs

    def create(self, validated_data):
        application_pdf_files = validated_data.pop('application_pdf_files', [])
        diploma_supplement_files = validated_data.pop('diploma_supplement_files', [])
        passport_scan_files = validated_data.pop('passport_scan_files', [])
        diploma_files = validated_data.pop('diploma_files', [])
        certificate_files = validated_data.pop('certificate_files', [])

        application = StudentApplication.objects.create(**validated_data)

        if application_pdf_files:
            ApplicationPdf.objects.bulk_create(
                [
                    ApplicationPdf(
                        application=application,
                        file=application_pdf_file,
                    )
                    for application_pdf_file in application_pdf_files
                ]
            )

        if diploma_supplement_files:
            ApplicationDiplomaSupplement.objects.bulk_create(
                [
                    ApplicationDiplomaSupplement(
                        application=application,
                        file=diploma_supplement_file,
                    )
                    for diploma_supplement_file in diploma_supplement_files
                ]
            )

        if passport_scan_files:
            ApplicationPassportFile.objects.bulk_create(
                [
                    ApplicationPassportFile(
                        application=application,
                        file=passport_scan_file,
                    )
                    for passport_scan_file in passport_scan_files
                ]
            )

        if diploma_files:
            ApplicationDiploma.objects.bulk_create(
                [
                    ApplicationDiploma(
                        application=application,
                        file=diploma_file,
                    )
                    for diploma_file in diploma_files
                ]
            )

        if certificate_files:
            ApplicationCertificate.objects.bulk_create(
                [
                    ApplicationCertificate(
                        application=application,
                        file=certificate_file,
                    )
                    for certificate_file in certificate_files
                ]
            )

        return application
