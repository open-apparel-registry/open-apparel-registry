import json

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import render
from django.utils.safestring import mark_safe
from simple_history.admin import SimpleHistoryAdmin
from waffle.models import Flag, Sample, Switch
from waffle.admin import FlagAdmin, SampleAdmin, SwitchAdmin

from api import models

from api.reports import get_report_names, run_report


class ApiAdminSite(AdminSite):
    site_header = 'Open Apparel Registry Admin'

    def get_urls(self):
        from django.conf.urls import url
        base_urls = super(ApiAdminSite, self).get_urls()
        urls = [
            url(r'^reports/(?P<name>[\w-]+)/$',
                self.admin_view(self.report_view)),
            url(r'^reports/$', self.admin_view(self.reports_list_view),
                name='reports')
        ]
        return base_urls + urls

    def report_view(self, request, name):
        context = run_report(name)
        return render(request, 'reports/report.html', context)

    def reports_list_view(self, request):
        return render(request, 'reports/reports.html', {
            'names': get_report_names()
        })


admin_site = ApiAdminSite()


class OarUserAdmin(UserAdmin):
    exclude = ('last_name', 'date_joined', 'first_name')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'is_staff', 'is_active',
                           'should_receive_newsletter',
                           'has_agreed_to_terms_of_service')}),
    )


class FacilityHistoryAdmin(SimpleHistoryAdmin):
    history_list_display = ('name', 'address', 'location')

    readonly_fields = ('created_from',)


class FacilityListItemAdmin(admin.ModelAdmin):
    exclude = ('processing_results',)
    readonly_fields = ('facility_list', 'facility',
                       'pretty_processing_results')

    def pretty_processing_results(self, instance):
        # The processing_results field is populated exclusively from processing
        # code so we are not in danger of rendering potentially unsafe user
        # submitted content
        return mark_safe('<pre>{}</pre>'.format(
            json.dumps(instance.processing_results, indent=2)))

    pretty_processing_results.short_description = 'Processing results'


class FacilityMatchAdmin(SimpleHistoryAdmin):
    exclude = ('results',)
    history_list_display = ('status', 'facility')
    readonly_fields = ('facility_list_item', 'facility',
                       'confidence', 'status', 'pretty_results')

    def pretty_results(self, instance):
        # The status field is populated exclusively from processing code so we
        # are not in danger of rendering potentially unsafe user submitted
        # content
        return mark_safe('<pre>{}</pre>'.format(
            json.dumps(instance.results, indent=2)))

    pretty_results.short_description = 'Results'


class ContributorAdmin(SimpleHistoryAdmin):
    history_list_display = ('is_verified', 'verification_notes')


class FacilityClaimAdmin(SimpleHistoryAdmin):
    history_list_display = ('id', 'contact_person', 'created_at', 'status')
    readonly_fields = ('contributor', 'facility', 'status_change_reason',
                       'status_change_by', 'status_change_date', 'status')


class FacilityClaimReviewNoteAdmin(SimpleHistoryAdmin):
    history_list_display = ('id', 'created_at')
    readonly_fields = ('claim', 'author')


class FacilityAliasAdmin(SimpleHistoryAdmin):
    history_list_display = ('oar_id', 'facility')
    readonly_fields = ('oar_id', 'facility', 'reason')


class SourceAdmin(admin.ModelAdmin):
    readonly_fields = ('contributor', 'source_type', 'facility_list', 'create')


admin_site.register(models.Version)
admin_site.register(models.User, OarUserAdmin)
admin_site.register(models.Contributor, ContributorAdmin)
admin_site.register(models.FacilityList)
admin_site.register(models.Source, SourceAdmin)
admin_site.register(models.FacilityListItem, FacilityListItemAdmin)
admin_site.register(models.Facility, FacilityHistoryAdmin)
admin_site.register(models.FacilityLocation)
admin_site.register(models.FacilityMatch, FacilityMatchAdmin)
admin_site.register(models.FacilityClaim, FacilityClaimAdmin)
admin_site.register(models.FacilityClaimReviewNote,
                    FacilityClaimReviewNoteAdmin)
admin_site.register(models.FacilityAlias, FacilityAliasAdmin)
admin_site.register(Flag, FlagAdmin)
admin_site.register(Sample, SampleAdmin)
admin_site.register(Switch, SwitchAdmin)
