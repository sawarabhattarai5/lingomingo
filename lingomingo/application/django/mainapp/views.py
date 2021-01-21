import pycountry
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from chat.models import *
from .forms import RegisterForm, PostForm
from .models import Language, Friend, get_profile_model, friend_relation, Post, Like

lang_msg = 'Welcome to LingoMingo. Please select Languages in <a href="/profile/edit">Profile Settings</a> to start making friends'


def index(request):
    context = {}
    # if user is authenticated display the following
    if request.user.is_authenticated:
        # display message if user has incomplete section in settings

        if not (request.user.profile.learning_language.all() and request.user.profile.primary_language.all()):
            messages.error(request, lang_msg)

        if request.method == 'POST':
            print(request.POST)  # debug purpose

            # if user click on one of these following buttons, run the functions associated with them
            # under models.Profile class
            #
            # once the function is completed, return user a message via the messages framework to inform
            # them that their action has been executed
            if request.POST.get('add_friend'):
                other_uuid = request.POST.get('add_friend')
                request.user.profile.add_friend(other_uuid)
                messages.success(request, 'Friend request has been sent to ' + get_profile_model().get(
                    uuid=other_uuid).user.first_name)
            if request.POST.get('accept_friend_request'):
                other_uuid = request.POST.get('accept_friend_request')
                request.user.profile.accept_friend_request(other_uuid)
                messages.success(request,
                                 'You are now friends with ' + get_profile_model().get(uuid=other_uuid).user.first_name)
            if request.POST.get('decline_friend_request'):
                other_uuid = request.POST.get('decline_friend_request')
                request.user.profile.decline_friend_request(other_uuid)
                messages.info(request, 'You have declined ' + get_profile_model().get(
                    uuid=other_uuid).user.first_name + '\'s friend request')
            if request.POST.get('cancel_friend_request'):
                other_uuid = request.POST.get('cancel_friend_request')
                request.user.profile.cancel_friend_request(other_uuid)
                messages.info(request, 'You have cancelled the friend request for ' + get_profile_model().get(
                    uuid=other_uuid).user.first_name)

            if request.POST.get('search'):
                query = request.POST.get('search')
                search_results = get_profile_model().filter(
                    Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query))
                if search_results.count() == 0:
                    messages.error(request, 'no result for the search query')
                context.update({'search_results': search_results})

        # matching:
        profile = request.user.profile
        query_set = set([])
        for prime_lang in profile.primary_language.all():
            query = get_profile_model().filter(learning_language__name=prime_lang.name)
            for item in query:
                if not friend_relation(profile, item):
                    query_set.add(item)
        for learn_lang in profile.learning_language.all():
            query = get_profile_model().filter(primary_language__name=learn_lang.name)
            for item in query:
                if not friend_relation(profile, item):
                    query_set.add(item)

        if query_set.__contains__(profile):
            query_set.remove(profile)  # remove their own profile so they can't friend themselves

        context.update({'profile_list': query_set})
        print(context)
        return render(request, 'mainapp/index.html', context)

    # else show them a login/signup page
    else:
        return render(request, 'mainapp/home.html')


# def profile(request, profile_id):
#     profile = get_object_or_404(Profile, pk=profile_id)
#     post_list = Post.objects.filter(profile=profile)
#     return render(request, 'mainapp/profile.html', context={'profile': profile, 'post_list': post_list})

@login_required
def profile(request, profile_uuid):  # returns profile info with requested uuid
    profile = get_profile_model().get(uuid=profile_uuid)
    post_list = Post.objects.filter(profile=profile).order_by('created_at').reverse()  # latest post shows first
    create_post = None
    edit_post = None
    form = PostForm()
    context = {'profile': profile, 'post_list': post_list, 'create_post': create_post, 'edit_post': edit_post,
               'form': form}

    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('create_post'):
            request.user.profile.create_post(request.POST.get('create_post'))
        if request.POST.get('delete_post'):
            request.user.profile.delete_post(int(request.POST.get('delete_post')))
        if request.POST.get('edit_post'):
            desc = request.POST.get('edit_post')
            postID = request.POST.get('edit_post_id')
            request.user.profile.edit_post(postID, desc)
        if request.POST.get('like_post'):
            post = Post.objects.get(pk=request.POST.get('like_post'))
            profile = request.user.profile
            if post.is_liked(profile):
                Like.objects.get(post=post, profile=profile).delete()
            else:
                Like.objects.create(post=post, profile=profile)

            # post = Post.objects.get(id=int(request.POST.get('like_post')))
            # if request.user.profile not in post.profiles_liked.all():
            #     request.user.profile.like_post(int(request.POST.get('like_post')), 1)
            #     post.profiles_liked.add(request.user.profile)
            # else:
            #     request.user.profile.like_post(int(request.POST.get('like_post')), -1)
            #     post.profiles_liked.remove(request.user.profile)
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                f = form.save(commit=False)
                f.profile = request.user.profile
                f.save()

    return render(request, 'mainapp/profile.html', context=context)


def register(request):
    # sign up system & form is handled by Django, to read more visit
    # https://docs.djangoproject.com/en/3.0/topics/auth/default/
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/profile/edit')

    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def homepage(request):
    username = request.user.get_username()
    userProfile = get_profile_model().get(user=request.user)
    return render(request, 'mainapp/homepage.html', context={'username': username, 'profile': userProfile})


@login_required
def friends(request):
    print(request.POST)

    if not (request.user.profile.learning_language.all() and request.user.profile.primary_language.all()):
        messages.error(request, lang_msg)
    # if user click on un-friend button:
    if request.method == 'POST':
        uuid = request.POST.get('unfriend')
        if request.POST.get('unfriend'):
            friend_obj = Friend.objects.get(
                Q(profile_1=request.user.profile, profile_2=get_profile_model().get(uuid=uuid)) | Q(
                    profile_2=request.user.profile, profile_1=get_profile_model().get(uuid=uuid)))
            friend_obj.delete()

    # else render their friend list
    friend_list = request.user.profile.friend_list()
    context = {'friend_list': friend_list}
    return render(request, 'mainapp/friendlist.html', context)


@login_required
def profile_settings(request):
    # debug
    print(request.POST)
    if not (request.user.profile.learning_language.all() and request.user.profile.primary_language.all()):
        messages.error(request, lang_msg)

    # list of profile icons for users to choose from
    # https://fontawesome.com/icons?d=gallery&c=animals&m=free
    icon_list = ['cat', 'crow', 'dog', 'dove', 'dragon', 'feather', 'fish', 'frog', 'hippo', 'horse',
                 'horse-head', 'kiwi-bird', 'otter', 'paw', 'spider']

    # if form is submitted in setting page we update the profile object
    if request.method == 'POST':

        # personal infos
        if request.POST.get('fname'):
            request.user.first_name = request.POST.get('fname')
            request.user.last_name = request.POST.get('lname')
            request.user.email = request.POST.get('email')

            if pycountry.countries.get(name=request.POST.get('location')):  # verify if country name exists
                request.user.profile.location = pycountry.countries.get(
                    name=request.POST.get('location')).alpha_2.lower()  # store 2 letter code in db
            messages.success(request, 'Personal Info Updated')

        # about me
        if request.POST.get('about_me'):
            request.user.profile.about_me = request.POST.get('about_me')
            messages.success(request, 'About Me Updated')

        # add a primary language
        if request.POST.get('add_prime_lang'):
            if len(Language.objects.filter(
                    name=request.POST.get('add_prime_lang'))) == 1:  # check if language exist in database
                request.user.profile.primary_language.add(Language.objects.get(name=request.POST.get('add_prime_lang')))
                # create message object so user knows action was done
                messages.success(request, request.POST.get('add_prime_lang') + ' was added to your Primary Languages')
            else:
                messages.error(request, 'The language you are trying to add is not yet supported')
                print("error")

        # removing a primary language
        if request.POST.get('remove_prime_lang'):
            request.user.profile.primary_language.remove(
                Language.objects.get(name=request.POST.get('remove_prime_lang')))
            messages.success(request,
                             request.POST.get('remove_prime_lang') + ' was removed from your Primary Languages')

        # add a learning language
        if request.POST.get('add_learn_lang'):
            if len(Language.objects.filter(
                    name=request.POST.get('add_learn_lang'))) == 1:  # check if language exist in database
                request.user.profile.learning_language.add(
                    Language.objects.get(name=request.POST.get('add_learn_lang')))
                messages.success(request, request.POST.get('add_learn_lang') + ' was added to your Learning Languages')
            else:
                messages.error(request, 'The language you are trying to add is not yet supported')

        # removing a learning language
        if request.POST.get('remove_learn_lang'):
            request.user.profile.learning_language.remove(
                Language.objects.get(name=request.POST.get('remove_learn_lang')))
            messages.success(request,
                             request.POST.get('remove_learn_lang') + ' was removed from your Learning Languages')

        # changing icons
        if request.POST.get('icon'):
            icon = request.POST.get('icon')
            if icon_list.__contains__(icon):
                request.user.profile.profile_icon = icon
                messages.success(request, 'Your icon has been changed to ' + icon)
            else:
                messages.error(request, 'The icon you selected is invalid')

        # IMPORTANT: always save after modifying the object
        request.user.save()  # save user/profile object

    # context rendering section
    user_prime_lang = request.user.profile.primary_language.all()
    user_learn_lang = request.user.profile.learning_language.all()
    languages = Language.objects.all()
    country_list = pycountry.countries.objects

    context = {'profile': request.user.profile, 'languages': languages, 'user_prime_lang': user_prime_lang,
               'user_learn_lang': user_learn_lang, 'country_list': country_list, 'icon_list': icon_list}
    return render(request, 'mainapp/profile_edit.html', context)


def setup(request):
    lang_list_alpha_3 = ['spa', 'fra', 'deu', 'eng', 'jpn', 'ita', 'zho', 'ara', 'rus', 'kor', 'por', 'heb', 'hin',
                         'nep', 'fas', 'tgl', 'hin', 'afr', 'nld', 'ben', 'tur', 'swa', 'urd', 'cat']

    lang_list_alpha_3.sort()
    lang_names = []
    for lang in lang_list_alpha_3:
        lang_names.append(pycountry.languages.get(alpha_3=lang).name)
        obj, created = Language.objects.get_or_create(alpha_3=lang, name=pycountry.languages.get(alpha_3=lang).name)
        if created:
            print(str(obj) + ' was added to database')

    context = {'added_lang_list': lang_names}

    print('language database addition script finished successfully')
    return HttpResponse('Script Ran')


def settings(request):
    context = {}
    return render(request, 'mainapp/settings.html', context)


def setup(request):
    lang_list_alpha_3 = ['spa', 'fra', 'deu', 'eng', 'jpn', 'ita', 'zho', 'ara', 'rus', 'kor', 'por', 'heb', 'hin',
                         'nep', 'fas', 'tgl', 'hin', 'afr', 'nld', 'ben', 'tur', 'swa', 'urd']

    lang_list_alpha_3.sort()
    lang_names = []
    for lang in lang_list_alpha_3:
        lang_names.append(pycountry.languages.get(alpha_3=lang).name)
        obj, created = Language.objects.get_or_create(alpha_3=lang, name=pycountry.languages.get(alpha_3=lang).name)
        if created:
            str(obj) + ' was added to database'

    print('language database addition script finished successfully')

    return HttpResponse('Script Ran')


def match(request):
    context = {}
    return render(request, 'mainapp/match.html', context)


def stepbar(request):
    context = {}
    return render(request, 'mainapp/stepbar.html', context)
