from django.db import models
import datetime
from django.utils import timezone


class Community(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    company = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    date = models.DateField(default=timezone.now)
    url = models.CharField(max_length=200, unique=True)
    event_id = models.CharField(max_length=50)
    community_id = models.ForeignKey(Community, on_delete=models.CASCADE)
    view = models.IntegerField(default=0)
    unique = models.IntegerField(default=0)
    attendee = models.IntegerField(default=0)
    sessiontime = models.IntegerField(default=0)
    first_visitor = models.IntegerField(default=-1)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return str(self.date) + " " + str(self.name)


class DailyCommunityMember(models.Model):
    id = models.AutoField(primary_key=True)
    community_id = models.ForeignKey(Community, on_delete=models.CASCADE)
    member_count = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.date)


class QiitaTag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    company = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class QiitaPost(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    url = models.CharField(max_length=200)
    tag_id = models.ForeignKey(QiitaTag, on_delete=models.CASCADE)
    lgtm = models.IntegerField(default=0)
    remaining_count = models.IntegerField(default=0)
    first_post_date = models.DateField(default=timezone.now)

    twitter_screen_name = models.CharField(max_length=100, default='undefined')
    last_tweeted_lgtm_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('url', 'tag_id')

    def __str__(self):
        return str(self.name)


class QiitaMember(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.date)


class TwitterTag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    company = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class TwitterPost(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    date = models.DateField(default=timezone.now)
    url = models.CharField(max_length=200)
    tag_id = models.ForeignKey(TwitterTag, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=200)
    follower_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('url', 'tag_id')

    def __str__(self):
        return str(self.name)


class DailyYoutubeSubscriber(models.Model):
    id = models.AutoField(primary_key=True)
    member_count = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.date)


class ZennTopics(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    company = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class ZennPost(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    url = models.CharField(max_length=200)
    topics_id = models.ForeignKey(ZennTopics, on_delete=models.CASCADE)
    liked = models.IntegerField(default=0)
    remaining_count = models.IntegerField(default=0)

    twitter_screen_name = models.CharField(max_length=100, default='undefined')
    last_tweeted_lgtm_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('url', 'topics_id')

    def __str__(self):
        return str(self.name)


class ConnpassMember(models.Model):
    id = models.AutoField(primary_key=True)
    profile_url = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    community_id = models.ForeignKey(Community, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('profile_url', 'community_id')

    def __str__(self):
        return str(self.profile_url)

class QiitaOrganization(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)

    class Meta:
        unique_together = ('username', 'organization')

    def __str__(self):
        return str(self.username)


class YoutubeVideo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    url = models.CharField(max_length=200, unique=True)
    livestreaming = models.BooleanField(default=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.title)


class Leader(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    id_qiita = models.CharField(max_length=50, unique=True)
    id_zenn = models.CharField(max_length=50, unique=True)
    join_date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.name)


class RoleAtEvent(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return str(self.title)


class AttendanceAtEvent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.ForeignKey(Leader, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    role = models.ForeignKey(RoleAtEvent, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class OuterCommunity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class CommunityCollaboration(models.Model):
    id = models.AutoField(primary_key=True)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    outercommunity_id = models.ForeignKey(OuterCommunity, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('event_id', 'outercommunity_id')

    def __str__(self):
        return str(self.event_id)


# Already stopped retrieving below data. Just remain for future analysis.

class DailyEventRegistration(models.Model):
    id = models.AutoField(primary_key=True)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    view = models.IntegerField(default=0)
    unique = models.IntegerField(default=0)
    attendee = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.date)


class QiitaDailyPV(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)
    pv = models.IntegerField(default=0)

    def __str__(self):
        return str(self.date)


class TwitterDailyPV(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)
    pv = models.IntegerField(default=0)

    def __str__(self):
        return str(self.date)


class MonthlyFacebookMember(models.Model):
    id = models.AutoField(primary_key=True)
    community_id = models.ForeignKey(Community, on_delete=models.CASCADE)
    member_count = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.date)


class ZennDailyPV(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(default=timezone.now)
    pv = models.IntegerField(default=0)

    def __str__(self):
        return str(self.date)


class ConnpassPopularEvent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    date = models.DateField(default=timezone.now)
    url = models.CharField(max_length=200)
    attendee = models.IntegerField(default=0)
    series_title = models.CharField(max_length=200)
    series_url = models.CharField(max_length=200)

    def __str__(self):
        return str(self.date)


class TotalMemberKPI(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.date)


class YoutubePopularVideo(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    channel_name = models.CharField(max_length=200)
    channel_url = models.CharField(max_length=200)
    view_count = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.date)