import datetime
import uuid

import humanize
import pycountry
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Q
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class Language(models.Model):
    name = models.CharField(max_length=100, null=True)
    alpha_3 = models.CharField(max_length=3, null=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    GENDERS = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    # gender = models.CharField(choices=GENDERS, max_length=10, default='N/A')
    # location = models.CharField(max_length=100, default='Earth')
    # email = models.EmailField(default=None)
    # profile_picture = models.URLField(default='https://i.imgur.com/OYQulGk.png')
    # user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    country_list = []
    for c in list(pycountry.countries):
        country_list.append((c.alpha_2.lower(), c.name))

    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    primary_language = models.ManyToManyField(Language, related_name='primary_language')
    learning_language = models.ManyToManyField(Language, related_name='learning_language')
    gender = models.CharField(choices=GENDERS, max_length=10, default='N/A')
    location = models.CharField(choices=country_list, max_length=2, null=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    about_me = models.TextField(default='nothing here', null=True)
    profile_icon = models.CharField(max_length=20, default='paw')

    def __str__(self):
        return self.user.username

    def friend_list(self):
        friend_set = set([])
        query_1 = Friend.objects.filter(profile_1=self)
        for item in query_1:
            if item.is_friend:
                friend_set.add(item.profile_2)

        query_2 = Friend.objects.filter(profile_2=self)
        for item in query_2:
            if item.is_friend:
                friend_set.add(item.profile_1)

        return friend_set

    def get_location_full_name(self):
        if self.location:
            return pycountry.countries.get(alpha_2=self.location.upper()).name
        else:
            return ''

    def add_friend(self, other_uuid):
        Friend.objects.get_or_create(profile_1=self, profile_2=get_profile_model().get(uuid=other_uuid))

    def accept_friend_request(self, other_uuid):
        friend_req = Friend.objects.get(profile_1=get_profile_model().get(uuid=other_uuid), profile_2=self)
        friend_req.is_friend = True
        friend_req.save()

    def decline_friend_request(self, other_uuid):
        friend_req = Friend.objects.get(profile_1=get_profile_model().get(uuid=other_uuid), profile_2=self)
        friend_req.delete()

    def cancel_friend_request(self, other_uuid):
        friend_req = Friend.objects.get(profile_1=self, profile_2=get_profile_model().get(uuid=other_uuid))
        friend_req.delete()

    def incoming_friend_request(self):
        return Friend.objects.filter(profile_2=self, is_friend=False)

    def outgoing_friend_request(self):
        return Friend.objects.filter(profile_1=self, is_friend=False)

    def create_post(self, desc):
        Post.objects.create(profile=self, description=desc)

    def delete_post(self, post_id):
        post = Post.objects.get(id=post_id)
        post.delete()

    def edit_post(self, post_id, desc):
        post = Post.objects.get(id=post_id)
        post.description = desc
        post.created_at = datetime.datetime.now()
        Post.save(post)

    def like_post(self, post_id, num):
        post = Post.objects.get(id=post_id)
        post.like = F('like') + num  # to prevent  race condition
        Post.save(post)

    def create_post2(self, desc, image):
        Post.objects.create(profile=self, description=desc, image=image)


class Friend(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    profile_1 = models.ForeignKey(Profile, related_name="friend_creator", on_delete=models.CASCADE)
    profile_2 = models.ForeignKey(Profile, related_name="friend", on_delete=models.CASCADE)
    is_friend = models.BooleanField(default=False)
    friend_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.profile_1.user.username + ' and ' + self.profile_2.user.username


# when a user object gets created (user register) a profile is added automatically
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# when user object gets saved the profile object gets saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def get_profile_model():
    return Profile.objects.filter(user__is_active=True)


def friend_relation(self, other):
    return bool(len(Friend.objects.filter(Q(profile_1=self, profile_2=other) | Q(profile_1=other, profile_2=self))))


class Post(models.Model):
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post', blank=True)

    def __str__(self):
        return 'Post: ' + self.description

    def get_time(self):
        return humanize.naturaltime(self.created_at)

    def get_like_count(self):
        return Like.objects.filter(post=self).count()

    def is_liked(self, profile):
        return Like.objects.filter(post=self, profile=profile).count() > 0

    def liked_by(self):
        return Like.objects.filter(post=self)[:3]


class Like(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
