from rest_framework import serializers
from .models import Contact, SocialLink, ContactAddress, ContactPhone, ContactEmail


class ContactAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactAddress
        fields = ('id', 'address', 'created_at', 'updated_at')


class ContactPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPhone
        fields = ('id', 'phone', 'created_at', 'updated_at')


class ContactEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactEmail
        fields = ('id', 'email', 'created_at', 'updated_at')


class ContactSerializer(serializers.ModelSerializer):
    addresses = ContactAddressSerializer(many=True, read_only=True)
    phones = ContactPhoneSerializer(many=True, read_only=True)
    emails = ContactEmailSerializer(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = (
            'id',
            'address',
            'phone',
            'email',
            'addresses',
            'phones',
            'emails',
            'working_hours',
            'map_url',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = (
            'id',
            'platform',
            'url',
            'icon',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
