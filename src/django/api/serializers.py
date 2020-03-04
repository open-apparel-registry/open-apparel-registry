from itertools import chain

from django.conf import settings
from django.core import exceptions
from django.db import transaction
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import password_validation
from django.urls import reverse
from django.db.models import Count
from rest_framework.serializers import (CharField,
                                        DecimalField,
                                        EmailField,
                                        IntegerField,
                                        ListField,
                                        BooleanField,
                                        ModelSerializer,
                                        SerializerMethodField,
                                        ValidationError,
                                        Serializer)
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_auth.serializers import (PasswordResetSerializer,
                                   PasswordResetConfirmSerializer)
from allauth.account.utils import setup_user_email

from api.models import (FacilityList,
                        FacilityListItem,
                        Facility,
                        FacilityLocation,
                        FacilityMatch,
                        FacilityClaim,
                        FacilityClaimReviewNote,
                        User,
                        Contributor,
                        ProductType,
                        ProductionType,
                        Source)
from api.countries import COUNTRY_NAMES, COUNTRY_CHOICES
from api.processing import get_country_code
from waffle import switch_is_active


def _get_parent_company(claim):
    if not claim or not claim.parent_company:
        return None

    return {
        'id': claim.parent_company.admin.id,
        'name': claim.parent_company.name,
    }


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)
    name = SerializerMethodField()
    description = SerializerMethodField()
    website = SerializerMethodField()
    contributor_type = SerializerMethodField()
    other_contributor_type = SerializerMethodField()
    contributor_id = SerializerMethodField()
    claimed_facility_ids = SerializerMethodField()

    class Meta:
        model = User
        exclude = ()

    def validate(self, data):
        user = User(**data)
        password = data.get('password')

        try:
            password_validation.validate_password(password=password, user=user)
            return super(UserSerializer, self).validate(data)
        except exceptions.ValidationError as e:
            raise ValidationError({"password": list(e.messages)})

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def save(self, request, **kwargs):
        user = super(UserSerializer, self).save()
        setup_user_email(request, user, [])
        return user

    def get_name(self, user):
        try:
            return user.contributor.name
        except Contributor.DoesNotExist:
            return None

    def get_description(self, user):
        try:
            return user.contributor.description
        except Contributor.DoesNotExist:
            return None

    def get_website(self, user):
        try:
            return user.contributor.website
        except Contributor.DoesNotExist:
            return None

    def get_contributor_type(self, user):
        try:
            return user.contributor.contrib_type
        except Contributor.DoesNotExist:
            return None

    def get_other_contributor_type(self, user):
        try:
            return user.contributor.other_contrib_type
        except Contributor.DoesNotExist:
            return None

    def get_contributor_id(self, user):
        try:
            return user.contributor.id
        except Contributor.DoesNotExist:
            return None

    def get_claimed_facility_ids(self, user):
        if not switch_is_active('claim_a_facility'):
            return {
                'approved': None,
                'pending': None,
            }

        try:
            approved = FacilityClaim \
                .objects \
                .filter(status=FacilityClaim.APPROVED) \
                .filter(contributor=user.contributor) \
                .values_list('facility__id', flat=True)

            pending = FacilityClaim \
                .objects \
                .filter(status=FacilityClaim.PENDING) \
                .filter(contributor=user.contributor) \
                .values_list('facility__id', flat=True)

            return {
                'pending': pending,
                'approved': approved,
            }
        except Contributor.DoesNotExist:
            return {
                'approved': None,
                'pending': None,
            }


class UserProfileSerializer(ModelSerializer):
    name = SerializerMethodField()
    description = SerializerMethodField()
    website = SerializerMethodField()
    contributor_type = SerializerMethodField()
    other_contributor_type = SerializerMethodField()
    facility_lists = SerializerMethodField()
    is_verified = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'description', 'website', 'contributor_type',
                  'other_contributor_type', 'facility_lists', 'is_verified')

    def get_name(self, user):
        try:
            return user.contributor.name
        except Contributor.DoesNotExist:
            return None

    def get_description(self, user):
        try:
            return user.contributor.description
        except Contributor.DoesNotExist:
            return None

    def get_website(self, user):
        try:
            return user.contributor.website
        except Contributor.DoesNotExist:
            return None

    def get_contributor_type(self, user):
        try:
            return user.contributor.contrib_type
        except Contributor.DoesNotExist:
            return None

    def get_other_contributor_type(self, user):
        try:
            return user.contributor.other_contrib_type
        except Contributor.DoesNotExist:
            return None

    def get_contributor_id(self, user):
        try:
            return user.contributor.id
        except Contributor.DoesNotExist:
            return None

    def get_facility_lists(self, user):
        try:
            contributor = user.contributor
            return FacilityListSummarySerializer(
                FacilityList.objects.filter(
                    source__contributor=contributor,
                    source__is_active=True,
                    source__is_public=True,
                ).order_by('-created_at'),
                many=True,
            ).data
        except Contributor.DoesNotExist:
            return []

    def get_is_verified(self, user):
        try:
            return user.contributor.is_verified
        except Contributor.DoesNotExist:
            return False


class FacilityListSummarySerializer(ModelSerializer):
    class Meta:
        model = FacilityList
        fields = ('id', 'name', 'description')


class FacilityListSerializer(ModelSerializer):
    is_active = SerializerMethodField()
    is_public = SerializerMethodField()
    item_count = SerializerMethodField()
    items_url = SerializerMethodField()
    statuses = SerializerMethodField()
    status_counts = SerializerMethodField()
    contributor_id = SerializerMethodField()

    class Meta:
        model = FacilityList
        fields = ('id', 'name', 'description', 'file_name', 'is_active',
                  'is_public', 'item_count', 'items_url', 'statuses',
                  'status_counts', 'contributor_id', 'created_at')

    def get_is_active(self, facility_list):
        try:
            return facility_list.source.is_active
        except Source.DoesNotExist:
            return False

    def get_is_public(self, facility_list):
        try:
            return facility_list.source.is_public
        except Source.DoesNotExist:
            return False

    def get_item_count(self, facility_list):
        try:
            return facility_list.source.facilitylistitem_set.count()
        except Source.DoesNotExist:
            return 0

    def get_items_url(self, facility_list):
        return reverse('facility-list-items',
                       kwargs={'pk': facility_list.pk})

    def get_statuses(self, facility_list):
        try:
            return (facility_list.source.facilitylistitem_set
                    .values_list('status', flat=True)
                    .distinct())
        except Source.DoesNotExist:
            return []

    def get_status_counts(self, facility_list):
        try:
            statuses = FacilityListItem \
                .objects \
                .filter(source=facility_list.source) \
                .values('status') \
                .annotate(status_count=Count('status'))
        except Source.DoesNotExist:
            statuses = []

        status_counts_dictionary = {
            status_dict.get('status'): status_dict.get('status_count')
            for status_dict
            in statuses
        }

        uploaded = status_counts_dictionary.get(
            FacilityListItem.UPLOADED,
            0
        )

        parsed = status_counts_dictionary.get(
            FacilityListItem.PARSED,
            0
        )

        geocoded = status_counts_dictionary.get(
            FacilityListItem.GEOCODED,
            0
        )

        geocoded_no_results = status_counts_dictionary.get(
            FacilityListItem.GEOCODED_NO_RESULTS,
            0
        )

        matched = status_counts_dictionary.get(
            FacilityListItem.MATCHED,
            0
        )

        potential_match = status_counts_dictionary.get(
            FacilityListItem.POTENTIAL_MATCH,
            0
        )

        confirmed_match = status_counts_dictionary.get(
            FacilityListItem.CONFIRMED_MATCH,
            0
        )

        error = status_counts_dictionary.get(
            FacilityListItem.ERROR,
            0
        )

        error_parsing = status_counts_dictionary.get(
            FacilityListItem.ERROR_PARSING,
            0
        )

        error_geocoding = status_counts_dictionary.get(
            FacilityListItem.ERROR_GEOCODING,
            0
        )

        error_matching = status_counts_dictionary.get(
            FacilityListItem.ERROR_MATCHING,
            0
        )

        deleted = status_counts_dictionary.get(
            FacilityListItem.DELETED,
            0
        )

        return {
            FacilityListItem.UPLOADED: uploaded,
            FacilityListItem.PARSED: parsed,
            FacilityListItem.GEOCODED: geocoded,
            FacilityListItem.GEOCODED_NO_RESULTS: geocoded_no_results,
            FacilityListItem.MATCHED: matched,
            FacilityListItem.POTENTIAL_MATCH: potential_match,
            FacilityListItem.CONFIRMED_MATCH: confirmed_match,
            FacilityListItem.ERROR: error,
            FacilityListItem.ERROR_PARSING: error_parsing,
            FacilityListItem.ERROR_GEOCODING: error_geocoding,
            FacilityListItem.ERROR_MATCHING: error_matching,
            FacilityListItem.DELETED: deleted,
        }

    def get_contributor_id(self, facility_list):
        try:
            return facility_list.source.contributor.id \
                if facility_list.source.contributor else None
        except Source.DoesNotExist:
            return None


class FacilityQueryParamsSerializer(Serializer):
    name = CharField(required=False)
    contributors = ListField(
        child=IntegerField(required=False),
        required=False,
    )
    contributor_types = ListField(
        child=CharField(required=False),
        required=False,
    )
    countries = ListField(
        child=CharField(required=False),
        required=False,
    )
    page = IntegerField(required=False)
    pageSize = IntegerField(required=False)


class FacilityListQueryParamsSerializer(Serializer):
    contributor = IntegerField(required=False)


class FacilityListItemsQueryParamsSerializer(Serializer):
    search = CharField(required=False)
    status = ListField(
        child=CharField(required=False),
        required=False,
    )

    def validate_status(self, value):
        valid_statuses = ([c[0] for c in FacilityListItem.STATUS_CHOICES]
                          + [FacilityListItem.NEW_FACILITY,
                             FacilityListItem.REMOVED])
        for item in value:
            if item not in valid_statuses:
                raise ValidationError(
                    '{} is not a valid status. Must be one of {}'.format(
                        item, ', '.join(valid_statuses)))


class FacilitySerializer(GeoFeatureModelSerializer):
    oar_id = SerializerMethodField()
    country_name = SerializerMethodField()

    class Meta:
        model = Facility
        fields = ('id', 'name', 'address', 'country_code', 'location',
                  'oar_id', 'country_name')
        geo_field = 'location'

    # Added to ensure including the OAR ID in the geojson properties map
    def get_oar_id(self, facility):
        return facility.id

    def get_country_name(self, facility):
        return COUNTRY_NAMES.get(facility.country_code, '')


class FacilityDetailsSerializer(GeoFeatureModelSerializer):
    oar_id = SerializerMethodField()
    other_names = SerializerMethodField()
    other_addresses = SerializerMethodField()
    other_locations = SerializerMethodField()
    contributors = SerializerMethodField()
    country_name = SerializerMethodField()
    claim_info = SerializerMethodField()

    class Meta:
        model = Facility
        fields = ('id', 'name', 'address', 'country_code', 'location',
                  'oar_id', 'other_names', 'other_addresses', 'contributors',
                  'country_name', 'claim_info', 'other_locations')
        geo_field = 'location'

    # Added to ensure including the OAR ID in the geojson properties map
    def get_oar_id(self, facility):
        return facility.id

    def get_other_names(self, facility):
        return facility.other_names()

    def get_other_addresses(self, facility):
        return facility.other_addresses()

    def get_other_locations(self, facility):
        facility_locations = [
            {
                'lat': l.location.y,
                'lng': l.location.x,
                'contributor_id': l.contributor.admin.id if l.contributor
                else None,
                'contributor_name': l.contributor.name if l.contributor
                else None,
                'notes': l.notes,
            }
            for l
            in FacilityLocation.objects.filter(facility=facility)
        ]

        facility_matches = [
            {
                'lat': l.facility_list_item.geocoded_point.y,
                'lng': l.facility_list_item.geocoded_point.x,
                'contributor_id':
                l.facility_list_item.source.contributor.admin.id
                if l.facility_list_item.source.contributor else None,
                'contributor_name':
                l.facility_list_item.source.contributor.name
                if l.facility_list_item.source.contributor else None,
                'notes': None,
            }
            for l
            in FacilityMatch.objects.filter(facility=facility)
            .filter(status__in=[
                FacilityMatch.CONFIRMED,
                FacilityMatch.AUTOMATIC,
            ])
            .filter(is_active=True)
            if l.facility_list_item.geocoded_point != facility.location
            if l.facility_list_item.geocoded_point is not None
            if l.facility_list_item.source.is_active
            if l.facility_list_item.source.is_public
        ]

        return facility_locations + facility_matches

    def get_contributors(self, facility):
        def format_source(source):
            if type(source) is Source:
                return {
                    'id': source.contributor.admin.id
                    if source.contributor else None,
                    'name': source.display_name,
                    'is_verified': source.contributor.is_verified
                    if source.contributor else False,
                }
            return {
                'name': source,
            }
        request = self.context.get('request') \
            if self.context is not None else None
        user = request.user if request is not None else None
        return [
            format_source(source)
            for source
            in facility.sources(user=user)
        ]

    def get_country_name(self, facility):
        return COUNTRY_NAMES.get(facility.country_code, '')

    def get_claim_info(self, facility):
        if not switch_is_active('claim_a_facility'):
            return None

        try:
            claim = FacilityClaim \
                .objects \
                .filter(status=FacilityClaim.APPROVED) \
                .get(facility=facility)

            return {
                'id': claim.id,
                'facility': {
                    'description': claim.facility_description,
                    'name_english': claim.facility_name_english,
                    'name_native_language': claim
                    .facility_name_native_language,
                    'address': claim.facility_address,
                    'website': claim.facility_website
                    if claim.facility_website_publicly_visible else None,
                    'parent_company': _get_parent_company(claim),
                    'phone_number': claim.facility_phone_number
                    if claim.facility_phone_number_publicly_visible else None,
                    'minimum_order': claim.facility_minimum_order_quantity,
                    'average_lead_time': claim.facility_average_lead_time,
                    'workers_count': claim.facility_workers_count,
                    'female_workers_percentage': claim
                    .facility_female_workers_percentage,
                    'facility_type': claim.facility_type,
                    'other_facility_type': claim.other_facility_type,
                    'affiliations': claim.facility_affiliations,
                    'certifications': claim.facility_certifications,
                    'product_types': claim.facility_product_types,
                    'production_types': claim.facility_production_types,
                },
                'contact': {
                    'name': claim.point_of_contact_person_name,
                    'email': claim.point_of_contact_email,
                } if claim.point_of_contact_publicly_visible else None,
                'office': {
                    'name': claim.office_official_name,
                    'address': claim.office_address,
                    'country': claim.office_country_code,
                    'phone_number': claim.office_phone_number,
                } if claim.office_info_publicly_visible else None,
            }
        except FacilityClaim.DoesNotExist:
            return None


class FacilityCreateBodySerializer(Serializer):
    country = CharField(required=True)
    name = CharField(required=True, max_length=200)
    address = CharField(required=True, max_length=200)

    def validate_country(self, value):
        try:
            return get_country_code(value)
        except ValueError as ve:
            raise ValidationError(ve)


class FacilityCreateQueryParamsSerializer(Serializer):
    create = BooleanField(default=True, required=False)
    public = BooleanField(default=True, required=False)


class FacilityClaimSerializer(ModelSerializer):
    facility_name = SerializerMethodField()
    oar_id = SerializerMethodField()
    contributor_name = SerializerMethodField()
    contributor_id = SerializerMethodField()
    facility_address = SerializerMethodField()
    facility_country_name = SerializerMethodField()

    class Meta:
        model = FacilityClaim
        fields = ('id', 'created_at', 'updated_at', 'contributor_id', 'oar_id',
                  'contributor_name', 'facility_name', 'facility_address',
                  'facility_country_name', 'status')

    def get_facility_name(self, claim):
        return claim.facility.name

    def get_oar_id(self, claim):
        return claim.facility_id

    def get_contributor_name(self, claim):
        return claim.contributor.name

    def get_contributor_id(self, claim):
        return claim.contributor.admin.id

    def get_facility_address(self, claim):
        return claim.facility.address

    def get_facility_country_name(self, claim):
        return COUNTRY_NAMES.get(claim.facility.country_code, '')


class FacilityClaimDetailsSerializer(ModelSerializer):
    contributor = SerializerMethodField()
    facility = SerializerMethodField()
    status_change = SerializerMethodField()
    notes = SerializerMethodField()
    facility_parent_company = SerializerMethodField()

    class Meta:
        model = FacilityClaim
        fields = ('id', 'created_at', 'updated_at', 'contact_person', 'email',
                  'phone_number', 'company_name', 'website',
                  'facility_description', 'preferred_contact_method', 'status',
                  'contributor', 'facility', 'verification_method',
                  'status_change', 'notes', 'facility_parent_company',
                  'job_title', 'linkedin_profile')

    def get_contributor(self, claim):
        return UserProfileSerializer(claim.contributor.admin).data

    def get_facility(self, claim):
        return FacilitySerializer(claim.facility).data

    def get_status_change(self, claim):
        if claim.status == FacilityClaim.PENDING:
            return {
                'status_change_by': None,
                'status_change_date': None,
                'status_change_reason': None,
            }

        return {
            'status_change_by': claim.status_change_by.email,
            'status_change_date': claim.status_change_date,
            'status_change_reason': claim.status_change_reason,
        }

    def get_notes(self, claim):
        notes = FacilityClaimReviewNote \
            .objects \
            .filter(claim=claim) \
            .order_by('id')
        data = FacilityClaimReviewNoteSerializer(notes, many=True).data
        return data

    def get_facility_parent_company(self, claim):
        return _get_parent_company(claim)


class FacilityClaimReviewNoteSerializer(ModelSerializer):
    author = SerializerMethodField()

    class Meta:
        model = FacilityClaimReviewNote
        fields = ('id', 'created_at', 'updated_at', 'note', 'author')

    def get_author(self, note):
        return note.author.email


class ApprovedFacilityClaimSerializer(ModelSerializer):
    facility = SerializerMethodField()
    countries = SerializerMethodField()
    contributors = SerializerMethodField()
    facility_types = SerializerMethodField()
    facility_parent_company = SerializerMethodField()
    affiliation_choices = SerializerMethodField()
    certification_choices = SerializerMethodField()
    product_type_choices = SerializerMethodField()
    production_type_choices = SerializerMethodField()

    class Meta:
        model = FacilityClaim
        fields = ('id', 'facility_description',
                  'facility_name_english', 'facility_name_native_language',
                  'facility_address', 'facility_phone_number',
                  'facility_phone_number_publicly_visible',
                  'facility_website', 'facility_minimum_order_quantity',
                  'facility_average_lead_time', 'point_of_contact_person_name',
                  'point_of_contact_email', 'facility_workers_count',
                  'facility_female_workers_percentage',
                  'point_of_contact_publicly_visible',
                  'office_official_name', 'office_address',
                  'office_country_code', 'office_phone_number',
                  'office_info_publicly_visible',
                  'facility', 'countries', 'facility_parent_company',
                  'contributors', 'facility_website_publicly_visible',
                  'facility_types', 'facility_type', 'other_facility_type',
                  'affiliation_choices', 'certification_choices',
                  'facility_affiliations', 'facility_certifications',
                  'facility_product_types', 'facility_production_types',
                  'product_type_choices', 'production_type_choices')

    def get_facility(self, claim):
        return FacilityDetailsSerializer(
            claim.facility, context=self.context).data

    def get_countries(self, claim):
        return COUNTRY_CHOICES

    def get_contributors(self, claim):
        return [
            (contributor.id, contributor.name)
            for contributor
            in Contributor.objects.all().order_by('name')
        ]

    def get_facility_types(self, claim):
        return FacilityClaim.FACILITY_TYPE_CHOICES

    def get_facility_parent_company(self, claim):
        return _get_parent_company(claim)

    def get_affiliation_choices(self, claim):
        return FacilityClaim.AFFILIATION_CHOICES

    def get_certification_choices(self, claim):
        return FacilityClaim.CERTIFICATION_CHOICES

    def get_product_type_choices(self, claim):
        seeds = [
            seed
            for seed
            in ProductType.objects.all().values_list('value', flat=True)
            or []
        ]

        new_values = FacilityClaim \
            .objects \
            .all() \
            .values_list('facility_product_types', flat=True)

        values = [
            new_value
            for new_value
            in new_values if new_value is not None
        ]

        # Using `chain` flattens nested lists
        union_of_seeds_and_values = list(
            set(chain.from_iterable(values)).union(seeds))
        union_of_seeds_and_values.sort()

        return [
            (choice, choice)
            for choice
            in union_of_seeds_and_values
        ]

    def get_production_type_choices(self, claim):
        seeds = [
            seed
            for seed
            in ProductionType.objects.all().values_list('value', flat=True)
            or []
        ]

        new_values = FacilityClaim \
            .objects \
            .all() \
            .values_list('facility_production_types', flat=True)

        values = [
            new_value
            for new_value
            in new_values if new_value is not None
        ]

        # Using `chain` flattens nested lists
        union_of_seeds_and_values = list(
            set(chain.from_iterable(values)).union(seeds))
        union_of_seeds_and_values.sort()

        return [
            (choice, choice)
            for choice
            in union_of_seeds_and_values
        ]


class FacilityMatchSerializer(ModelSerializer):
    oar_id = SerializerMethodField()
    name = SerializerMethodField()
    address = SerializerMethodField()
    location = SerializerMethodField()

    class Meta:
        model = FacilityMatch
        fields = ('id', 'status', 'confidence', 'results',
                  'oar_id', 'name', 'address', 'location',
                  'is_active')

    def get_oar_id(self, match):
        return match.facility.id

    def get_name(self, match):
        return match.facility.name

    def get_address(self, match):
        return match.facility.address

    def get_location(self, match):
        [lng, lat] = match.facility.location

        return {
            "lat": lat,
            "lng": lng,
        }


class FacilityListItemSerializer(ModelSerializer):
    matches = SerializerMethodField()
    country_name = SerializerMethodField()
    processing_errors = SerializerMethodField()
    matched_facility = SerializerMethodField()

    class Meta:
        model = FacilityListItem
        exclude = ('created_at', 'updated_at', 'geocoded_point',
                   'geocoded_address', 'processing_results', 'facility')

    def get_matches(self, facility_list_item):
        return FacilityMatchSerializer(
            facility_list_item.facilitymatch_set.order_by('id'),
            many=True,
        ).data

    def get_country_name(self, facility_list_item):
        return COUNTRY_NAMES.get(facility_list_item.country_code, '')

    def get_processing_errors(self, facility_list_item):
        if facility_list_item.status not in FacilityListItem.ERROR_STATUSES:
            return None

        return [
            processing_result['message']
            for processing_result
            in facility_list_item.processing_results
            if processing_result['error']
        ]

    def get_matched_facility(self, facility_list_item):
        # Currently this will return None for automatic matches because the
        # matching method here
        # https://github.com/open-apparel-registry/open-apparel-registry/blob/develop/src/django/api/processing.py#L104
        # doesn't set the facility for automatic matches
        if facility_list_item.facility is None:
            return None

        [lng, lat] = facility_list_item.facility.location

        return {
            "oar_id": facility_list_item.facility.id,
            "address": facility_list_item.facility.address,
            "name": facility_list_item.facility.name,
            "created_from_id": facility_list_item.facility.created_from.id,
            "location": {
                "lat": lat,
                "lng": lng,
            },
        }


class UserPasswordResetSerializer(PasswordResetSerializer):
    email = EmailField()
    password_reset_form_class = PasswordResetForm

    def validate_email(self, user_email):
        data = self.initial_data
        self.reset_form = self.password_reset_form_class(data=data)
        if not self.reset_form.is_valid():
            raise ValidationError("Error")

        if not User.objects.filter(email__iexact=user_email).exists():
            raise ValidationError("Error")

        return user_email

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.

        if settings.ENVIRONMENT == 'Development':
            domain_override = 'localhost:6543'
        else:
            domain_override = request.get_host()

        opts = {
            'use_https': settings.ENVIRONMENT != 'Development',
            'domain_override': domain_override,
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'subject_template_name':
                'mail/reset_user_password_subject.txt',
            'email_template_name':
                'mail/reset_user_password_body.txt',
            'html_email_template_name':
                'mail/reset_user_password_body.html',
        }

        self.reset_form.save(**opts)


class UserPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    @transaction.atomic
    def save(self):
        self.user.save()

        return self.set_password_form.save()


class FacilityMergeQueryParamsSerializer(Serializer):
    target = CharField(required=True)
    merge = CharField(required=True)

    def validate_target(self, target_id):
        if not Facility.objects.filter(id=target_id).exists():
            raise ValidationError(
                'Facility {} does not exist.'.format(target_id))

    def validate_merge(self, merge_id):
        if not Facility.objects.filter(id=merge_id).exists():
            raise ValidationError(
                'Facility {} does not exist.'.format(merge_id))


class LogDownloadQueryParamsSerializer(Serializer):
    path = CharField(required=True)
    record_count = IntegerField(required=True)


class FacilityUpdateLocationParamsSerializer(Serializer):
    # The Google geocoder returns points with 7 decimals of precision, which is
    # "[the] practical limit of commercial surveying"
    # https://en.wikipedia.org/wiki/Decimal_degrees
    lat = DecimalField(max_digits=None, decimal_places=7, required=True)
    lng = DecimalField(max_digits=None, decimal_places=7, required=True)
    contributor_id = IntegerField(required=False)
    notes = CharField(required=False)

    def validate_lat(self, lat):
        if lat < -90 or lat > 90:
            raise ValidationError('lat must be between -90 and 90.')

    def validate_lng(self, lat):
        if lat < -180 or lat > 180:
            raise ValidationError('lng must be between -180 and 180.')

    def validate_contributor_id(self, contributor_id):
        if not Contributor.objects.filter(id=contributor_id).exists():
            raise ValidationError(
                'Contributor {} does not exist.'.format(contributor_id))
