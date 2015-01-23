# -*- coding: utf-8 -*-

from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.exceptions import SuspiciousOperation
from django.db import IntegrityError
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from edxmako.shortcuts import render_to_response
from student.models import UserProfile

# import ifmo_sso
import hashlib
import logging

logger = logging.getLogger('ifmo_sso')


def sso_login(request, template='sso_login.html', redirect_on_success=settings.SSO_REDIRECT):
    context_dict = {'csrftoken': csrf(request)['csrf_token'], 'redirect': redirect_on_success}
    return render_to_response(template, context_dict)


@require_POST
# FIXME: Move secret out of parameters
def sso_authenticate(request, redirect_on_success='/', redirect_on_failure='/login', secret=settings.SSO_SECRET):
    u = None
    # FIXME: Handle this user-friedly, now just 500-error is thrown on Exception
    sso_validate_data(request, secret)

    def _get_email():
        email = request.POST.get('email')
        if "@" not in email:
            # FIXME: Move to settings
            email = u_ssoid + '@niuitmo.ru'
        return email

    try:
        # Try to find user with given SSO ID
        u_ssoid = request.POST.get('ssoid')
        u = User.objects.get(username__exact=u_ssoid)
        p = UserProfile.objects.get(user=u)
        # TODO: Update user info concerning incoming data
    except User.DoesNotExist:
        # Register new user
        try:
            # Creating User
            u = User.objects.create_user(username=u_ssoid, email=_get_email())
            u.is_active = True

            # Creating edX UserProfile
            p = UserProfile.objects.create(user_id=u.id)

        except IntegrityError, e:
            # Possible reason: email already exists, FIXME: handle this correctly
            logger.error('Failed to register user: Integrity error => ' + e.message)
            u = None
            p = None

    if p is not None:
        p.name = '%s %s %s' % (u.last_name, u.first_name, request.POST.get('middlename'))
        p.gender = request.POST.get('gender')
        p.year_of_birth = request.POST.get('birthdate').split(' ')[0].split('.')[-1]
        p.country = request.POST.get('countryCode')
        # Persisting data
        p.save()

    # If user WAS found or new one registered
    if u is not None:
        # Update user data
        u.last_name = request.POST.get('lastname')
        u.first_name = request.POST.get('firstname')
        u.email = _get_email()
        u.save()
        # Dirty hack imitating autheticate(user, hash), see: http://stackoverflow.com/a/2787747
        u.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, u)

    else:
        # Redirect to login page
        # TODO: Use comprehensive messages
        return redirect(redirect_on_failure)
    return redirect(redirect_on_success)


def sso_logout(request, redirect_on_complete=settings.SSO_LOGOUTBACK):
    # Logout from edX
    auth_logout(request)
    # Logout from SSO
    return redirect(settings.SSO_PATH + '?logout=logout&logoutback=' + redirect_on_complete)


@csrf_exempt
def sso_logout_back(request, redirect_on_complete='/'):
    return redirect(redirect_on_complete)


# TODO: Move to decorator
def sso_validate_data(request, secret):
    # TODO: Truncate line
    required_fields = [
        "ssoid", "lastname", "firstname", "middlename", "birthdate", "gender", "countryCode", "roles", "ttl"
    ]
    str_to_hash = "".join([request.POST.get(i) for i in required_fields]) + secret
    str_to_hash = str_to_hash.encode('windows-1251')
    hash_result = hashlib.sha1()
    hash_result.update(str_to_hash)
    if request.POST.get('hash') != hash_result.hexdigest().upper():
        logger.error('Hash validation failed for ssoid = ' + request.POST.get('ssoid'))
        raise SuspiciousOperation
