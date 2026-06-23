from rest_framework import serializers

from .models import (
    ApplicationCV,
    ApplicationDiploma,
    ApplicationIdentityDocument,
    ApplicationLanguageCertificate,
    ApplicationMotivationLetter,
    ApplicationTranscript,
    StudentApplication,
)


class _FileOnlySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'file', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ApplicationCVSerializer(_FileOnlySerializer):
    class Meta(_FileOnlySerializer.Meta):
        model = ApplicationCV


class ApplicationMotivationLetterSerializer(_FileOnlySerializer):
    class Meta(_FileOnlySerializer.Meta):
        model = ApplicationMotivationLetter


class ApplicationIdentityDocumentSerializer(_FileOnlySerializer):
    class Meta(_FileOnlySerializer.Meta):
        model = ApplicationIdentityDocument


class ApplicationLanguageCertificateSerializer(_FileOnlySerializer):
    class Meta(_FileOnlySerializer.Meta):
        model = ApplicationLanguageCertificate


class ApplicationTranscriptSerializer(_FileOnlySerializer):
    class Meta(_FileOnlySerializer.Meta):
        model = ApplicationTranscript


class ApplicationDiplomaSerializer(_FileOnlySerializer):
    class Meta(_FileOnlySerializer.Meta):
        model = ApplicationDiploma


class StudentApplicationSerializer(serializers.ModelSerializer):
    # Read-only nested lists
    cvs = ApplicationCVSerializer(many=True, read_only=True)
    motivation_letters = ApplicationMotivationLetterSerializer(many=True, read_only=True)
    identity_documents = ApplicationIdentityDocumentSerializer(many=True, read_only=True)
    language_certificates = ApplicationLanguageCertificateSerializer(many=True, read_only=True)
    transcripts = ApplicationTranscriptSerializer(many=True, read_only=True)
    diplomas = ApplicationDiplomaSerializer(many=True, read_only=True)

    # Write-only upload fields
    cv_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    motivation_letter_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    identity_document_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
    )
    language_certificate_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    transcript_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    diploma_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
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
            'email',
            # write-only upload fields
            'cv_files',
            'motivation_letter_files',
            'identity_document_files',
            'language_certificate_files',
            'transcript_files',
            'diploma_files',
            # read-only file lists
            'cvs',
            'motivation_letters',
            'identity_documents',
            'language_certificates',
            'transcripts',
            'diplomas',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'cvs',
            'motivation_letters',
            'identity_documents',
            'language_certificates',
            'transcripts',
            'diplomas',
            'status',
            'created_at',
            'updated_at',
        )

    def validate_passport_series(self, value):
        return value.upper()

    def validate(self, attrs):
        if self.instance is None:
            if not attrs.get('identity_document_files'):
                raise serializers.ValidationError({
                    'identity_document_files': (
                        "Kamida bitta shaxsni tasdiqlovchi "
                        "hujjat yuklanishi kerak."
                    ),
                })
            if not attrs.get('diploma_files'):
                raise serializers.ValidationError({
                    'diploma_files': (
                        "Kamida bitta universitet diplomi "
                        "yuklanishi kerak."
                    ),
                })
        return attrs

    def create(self, validated_data):
        cv_files = validated_data.pop('cv_files', [])
        motivation_letter_files = validated_data.pop('motivation_letter_files', [])
        identity_document_files = validated_data.pop('identity_document_files', [])
        language_certificate_files = validated_data.pop('language_certificate_files', [])
        transcript_files = validated_data.pop('transcript_files', [])
        diploma_files = validated_data.pop('diploma_files', [])

        application = StudentApplication.objects.create(**validated_data)

        if cv_files:
            ApplicationCV.objects.bulk_create(
                [ApplicationCV(application=application, file=f)
                 for f in cv_files]
            )
        if motivation_letter_files:
            ApplicationMotivationLetter.objects.bulk_create(
                [ApplicationMotivationLetter(application=application, file=f)
                 for f in motivation_letter_files]
            )
        if identity_document_files:
            ApplicationIdentityDocument.objects.bulk_create(
                [ApplicationIdentityDocument(application=application, file=f)
                 for f in identity_document_files]
            )
        if language_certificate_files:
            ApplicationLanguageCertificate.objects.bulk_create(
                [ApplicationLanguageCertificate(application=application, file=f)
                 for f in language_certificate_files]
            )
        if transcript_files:
            ApplicationTranscript.objects.bulk_create(
                [ApplicationTranscript(application=application, file=f)
                 for f in transcript_files]
            )
        if diploma_files:
            ApplicationDiploma.objects.bulk_create(
                [ApplicationDiploma(application=application, file=f)
                 for f in diploma_files]
            )

        return application
