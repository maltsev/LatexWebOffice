import os
import sys

import django.contrib.auth
from django.db.models.loading import get_model
from django.core.exceptions import ImproperlyConfigured

import settings

#
#
#   Python
#
#

# Creates os.path.relpath for Python 2.4
# Source: http://unittest-ext.googlecode.com/hg-history/fde01baf0a62881cb996b43d044eade876dd01b2/unittest2/unittest2/compatibility.py
if not hasattr(os, 'relpath'):
    if os.path is sys.modules.get('ntpath'):
        def relpath(path, start=os.path.curdir):
            """Return a relative version of a path"""

            if not path:
                raise ValueError("no path specified")
            start_list = os.path.abspath(start).split(os.path.sep)
            path_list = os.path.abspath(path).split(os.path.sep)
            if start_list[0].lower() != path_list[0].lower():
                unc_path, rest = os.path.splitunc(path)
                unc_start, rest = os.path.splitunc(start)
                if bool(unc_path) ^ bool(unc_start):
                    raise ValueError("Cannot mix UNC and non-UNC paths (%s and %s)"
                                                                        % (path, start))
                else:
                    raise ValueError("path is on drive %s, start on drive %s"
                                                        % (path_list[0], start_list[0]))
            # Work out how much of the filepath is shared by start and path.
            for i in range(min(len(start_list), len(path_list))):
                if start_list[i].lower() != path_list[i].lower():
                    break
            else:
                i += 1

            rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
            if not rel_list:
                return os.path.curdir
            return os.path.join(*rel_list)

    else:
        # default to posixpath definition
        def relpath(path, start=os.path.curdir):
            """Return a relative version of a path"""

            if not path:
                raise ValueError("no path specified")

            start_list = os.path.abspath(start).split(os.path.sep)
            path_list = os.path.abspath(path).split(os.path.sep)

            # Work out how much of the filepath is shared by start and path.
            i = len(os.path.commonprefix([start_list, path_list]))

            rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
            if not rel_list:
                return os.path.curdir
            return os.path.join(*rel_list)

    os.path.relpath = relpath



if not hasattr(os, 'SEEK_SET'):
    os.SEEK_SET = 0

if not hasattr(os, 'SEEK_CUR'):
    os.SEEK_CUR = 1

if not hasattr(os, 'SEEK_END'):
    os.SEEK_END = 2







#
#
#   Django
#
#

if not hasattr(django.contrib.auth, 'get_user_model'):
    def get_user_model():
        """
        Returns the User model that is active in this project.
        Adapted version of django.contrib.auth.get_user_model() (Django 1.8)
        """
        try:
            return get_model(*settings.AUTH_USER_MODEL.split('.', 1))
        except ValueError:
            raise ImproperlyConfigured('AUTH_USER_MODEL must be of the form "app_label.model_name"')
        except LookupError:
            raise ImproperlyConfigured('AUTH_USER_MODEL refers to model "%s" that has not been installed' % settings.AUTH_USER_MODEL)


    django.contrib.auth.get_user_model = get_user_model