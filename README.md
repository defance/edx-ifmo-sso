# ifmo-sso

## Installation

Add this app to you installed apps:

```python
INSTALLED_APPS = (
    #...
    'ifmo_sso',
)
```

You do not need to add any urls to lms/cms urls.py, they are injected as app is started.

Add ifmo.auth.json with following content:
```json
{
      "LMS_BASE_URL": "http://your-lms-url/",
      "CMS_BASE_URL": "http://your-cms-url/",
      "SSO_PATH": "http://de.ifmo.ru/IfmoSSO/",
      "SSO_SECRET":     "your-ifmo-sso-secret-for-lms",
      "SSO_REDIRECT":   "ifmo_sso/authenticate/",
      "SSO_LOGOUTBACK": "ifmo_sso/logout_back/",
      "SSO_SECRET_STUDIO":     "your-sso-secret-for-cms",
      "SSO_REDIRECT_STUDIO":   "ifmo_sso/authenticate/",
      "SSO_LOGOUTBACK_STUDIO": "ifmo_sso/logout_back/"
}
```

