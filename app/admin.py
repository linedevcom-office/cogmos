from django.contrib import admin

# Register your models here.

from .models import *


class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'company')


admin.site.register(Community, CommunityAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'url', 'community_id', 'view', 'unique', 'attendee', 'sessiontime', 'first_visitor')


admin.site.register(Event, EventAdmin)


class DailyCommunityMemberAdmin(admin.ModelAdmin):
    list_display = ('community_id', 'member_count', 'date')


admin.site.register(DailyCommunityMember, DailyCommunityMemberAdmin)


class QiitaTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')


admin.site.register(QiitaTag, QiitaTagAdmin)


class QiitaPostAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'url', 'tag_id', 'lgtm', 'remaining_count', 'twitter_screen_name', 'last_tweeted_lgtm_count', 'first_post_date')


admin.site.register(QiitaPost, QiitaPostAdmin)


class QiitaMemberAdmin(admin.ModelAdmin):
    list_display = ('date', 'name')


admin.site.register(QiitaMember, QiitaMemberAdmin)


class TwitterTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')


admin.site.register(TwitterTag, TwitterTagAdmin)


class TwitterPostAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'url', 'tag_id', 'user_id', 'follower_count')


admin.site.register(TwitterPost, TwitterPostAdmin)


class DailyYoutubeSubscriberAdmin(admin.ModelAdmin):
    list_display = ('member_count', 'date')


admin.site.register(DailyYoutubeSubscriber, DailyYoutubeSubscriberAdmin)


class ZennTopicsAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')


admin.site.register(ZennTopics, ZennTopicsAdmin)


class ZennPostAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'url', 'topics_id', 'liked', 'remaining_count', 'twitter_screen_name', 'last_tweeted_lgtm_count')


admin.site.register(ZennPost, ZennPostAdmin)


class ConnpassMemberAdmin(admin.ModelAdmin):
    list_display = ('profile_url', 'date', 'community_id')


admin.site.register(ConnpassMember, ConnpassMemberAdmin)


class QiitaOrganizationAdmin(admin.ModelAdmin):
    list_display = ('username', 'organization')


admin.site.register(QiitaOrganization, QiitaOrganizationAdmin)


class YoutubeVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'livestreaming', 'date')


admin.site.register(YoutubeVideo, YoutubeVideoAdmin)


class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_qiita', 'id_zenn', 'join_date')


admin.site.register(Leader, LeaderAdmin)


class RoleAtEventAdmin(admin.ModelAdmin):
    list_display = ('title',)


admin.site.register(RoleAtEvent, RoleAtEventAdmin)


class AttendanceAtEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'role')


admin.site.register(AttendanceAtEvent, AttendanceAtEventAdmin)


class OuterCommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')


admin.site.register(OuterCommunity, OuterCommunityAdmin)


class CommunityCollaborationAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'outercommunity_id')


admin.site.register(CommunityCollaboration, CommunityCollaborationAdmin)


"""
class DailyEventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'view', 'unique', 'attendee', 'date')


admin.site.register(DailyEventRegistration, DailyEventRegistrationAdmin)


class QiitaDailyPVAdmin(admin.ModelAdmin):
    list_display = ('date', 'pv')


admin.site.register(QiitaDailyPV, QiitaDailyPVAdmin)


class TwitterDailyPVAdmin(admin.ModelAdmin):
    list_display = ('date', 'pv')


admin.site.register(TwitterDailyPV, TwitterDailyPVAdmin)


class MonthlyFacebookMemberAdmin(admin.ModelAdmin):
    list_display = ('community_id', 'member_count', 'date')


admin.site.register(MonthlyFacebookMember, MonthlyFacebookMemberAdmin)


class ZennDailyPVAdmin(admin.ModelAdmin):
    list_display = ('date', 'pv')


admin.site.register(ZennDailyPV, ZennDailyPVAdmin)


class ConnpassPopularEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'url', 'attendee', 'series_title', 'series_url')


admin.site.register(ConnpassPopularEvent, ConnpassPopularEventAdmin)


class TotalMemberKPIAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date')


admin.site.register(TotalMemberKPI, TotalMemberKPIAdmin)


class YoutubePopularVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'channel_name', 'channel_url', 'view_count')


admin.site.register(YoutubePopularVideo, YoutubePopularVideoAdmin)
"""