#!/usr/bin/python

from django.shortcuts import render

from blog.models import BlogPost
from board.models import Thread

import datetime


HOMEPAGE_POST_NUMBER = 10    # Maximum number of posts to display
HOMEPAGE_THREAD_DELAY = 3   # Number of days before expiration


def homepage(request):
    """
    Simple view corresponding to the homepage. It provides some blog posts
    and some board posts, including annotated threads).
    """
    context = {}

    # Last posts to display
    context['post_list'] = BlogPost.published.all().reverse()[:HOMEPAGE_POST_NUMBER]

    # Last threads to display
    date_limit = datetime.date.today() - datetime.timedelta(HOMEPAGE_THREAD_DELAY)
    date_limit = datetime.datetime(date_limit.year, date_limit.month, date_limit.day)
    threads = Thread.objects.all().filter(last_message__date__gte=date_limit).order_by('-date_created')

    # Annotate with flags
    for thread in threads:
        thread.annotate_flag(request.user)
    context['thread_list'] = threads

    return render(request, 'homepage.html', context)
