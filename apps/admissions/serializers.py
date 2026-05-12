from rest_framework import serializers

from .models import (
    ApplicationCertificate,
    ApplicationDiploma,
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


class StudentApplicationSerializer(serializers.ModelSerializer):
    diplomas = ApplicationDiplomaSerializer(many=True, read_only=True)
    certificates = ApplicationCertificateSerializer(many=True, read_only=True)
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
            'status',
            'created_at',
            'updated_at',
        )

    def validate_passport_series(self, value):
        return value.upper()

    def validate(self, attrs):
        diploma_files = attrs.get('diploma_files', [])
        if self.instance is None and not diploma_files:
            raise serializers.ValidationError(
                {'diploma_files': "Kamida bitta diplom fayli yuklanishi kerak."}
            )
        return attrs

    def create(self, validated_data):
        diploma_files = validated_data.pop('diploma_files', [])
        certificate_files = validated_data.pop('certificate_files', [])

        application = StudentApplication.objects.create(**validated_data)

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
