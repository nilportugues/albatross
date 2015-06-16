import git
import os

from django.conf import settings

# Generate this once, so we don't have to do a git lookup on every page load.
release = str(git.Repo(os.path.join(settings.BASE_DIR, "..")).head.commit)


def constants(request):
    return {
        "release": release
    }


def navigation(request):

    path = request.get_full_path()

    return {
        "navigation": {
            "index": "active" if path == "/" else "",
            "about": "active" if path == "/about/" else "",
            "contact": "active" if path == "/contact/" else "",
        }
    }
