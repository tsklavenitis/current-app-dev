from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key'

DEBUG = True

ALLOWED_HOSTS = ['avaxermappdev-7ff3a524a5eb.herokuapp.com','localhost','127.0.0.1']

INSTALLED_APPS = [
    'tinymce',
    'crispy_forms',
    'crispy_bootstrap4', 
    'slick_reporting',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'orm',
    'import_export',
    # 'ckeditor',
    # 'ckeditor_uploader',
    'django_select2', 
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'  # or 'tailwind' if you're using Tailwind



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'orm.middleware.Custom403Middleware',  
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',# Add this line
]

ROOT_URLCONF = 'ormproject.urls'
import os

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'crispy_forms_tags': 'crispy_forms.templatetags.crispy_forms_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'ormproject.wsgi.application'



DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # Adjust the number based on your needs


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'd90hf2otdrh3ru',
        'USER': 'ufc4f2niae8bn1',
        'PASSWORD': 'p60ba92ad3e9f995ebd2f5a0ceb57a1665a8a1e1407185a73c5603baad0d6e753',
        'HOST': 'c5hilnj7pn10vb.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com',  # Or the hostname of your database
        'PORT': '5432',        # Default PostgreSQL port
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Athens'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

# 1. URL to use when referring to static files located in STATIC_ROOT.
STATIC_URL = '/static/'

# 2. Additional directories where Django will search for static files in development
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Include a global static directory
    # or, for Django < 3.1:
    # os.path.join(BASE_DIR, "static"),
]

# 3. Directory where Django will collect static files for deployment
STATIC_ROOT = BASE_DIR / "staticfiles"  # Collect all static files in this directory for production
# or, for Django < 3.1:
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Keep this empty or add custom paths if needed
        'APP_DIRS': True,  # This should be True to allow app-level templates
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CKEDITOR_UPLOAD_PATH = 'content/ckeditor/'

# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': 'Full',
#         'toolbar_Full': [
#             ['FontSize','Bold', 'Italic', 'Underline','NumberedList', 'BulletedList','TextColor', 'BGColor'],
#             ['JustifyLeft', 'JustifyBlock'],
#             ['Link', 'Unlink', 'Anchor'],
#             ['Table', 'HorizontalRule', 'Smiley', 'SpecialChar'],
#         ],
#         'height': 'auto',  # Προσαρμόστε το ύψος ανάλογα με τις ανάγκες σας
#         'width': 'auto',    # Ορίζει το πλάτος του CKEditor στο 100% του container
#         'resize_enabled': True,  # Επιτρέπει την αλλαγή μεγέθους
#     }
# }

TINYMCE_DEFAULT_CONFIG = {
    'theme': 'silver',
    'plugins': 'lists link image preview codesample table fullscreen paste',
    'toolbar': '| fullscreen | undo redo | bold italic underline | alignleft aligncenter alignright alignjustify | '
               'bullist numlist outdent indent | link image | codesample | table  | preview',
    'menubar': True,
    'content_css': 'default',
    'paste_as_text': True,
    'paste_auto_cleanup_on_paste': True,
    # 'valid_elements': 'p,br,b,strong,i,em,u',
    'entity_encoding': 'raw',
    'convert_urls': False,
    
    'height': 400,  # Set the height of the editor
    'width': '100%',  # Set the width of the editor to 100% of the container
    
    'promotion': False,
    'forced_root_block': '',  # Prevent TinyMCE from automatically wrapping content in <p> or <div>
    # 'valid_elements': 'b,strong,i,em,a[href]',  # Allow only specific tags (optional)

}



DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)



# settings.py
EMAIL_BACKEND = 'orm.custom_smtp_backend.CustomSMTPBackend'


JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "ermapp.avax.gr",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "ermapp.avax.gr",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "ermapp.avax.gr",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "/images/avax-logo.jpeg",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "/images/avax-logo.jpeg",

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": "/images/avax-logo.jpeg",

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": '/images/favicon.png',

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the ermapp.avax.gr",

    # Copyright on the footer
    "copyright": "ermapp.avax.gr",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string 
    "search_model": [],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user

    

    ############
    # Top Menu #
    ############

    "topmenu_links": [
        # {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},

           # Your custom report links
         # external url that opens in a new window (Permissions can be added)
        {"name": "METABASE", "url": "https://metabase-a36x.onrender.com", "new_window": True},
        {
            "name": "HeatMaps", 
            "icon": "fas fa-users-cog",
            "url": "interactive_heatmap",  # Ensure this matches the URL name in urls.py
            "permissions": ["orm.view_risk"],
            "new_window": True
        },
        # {
        #     "name": "Risk Detail Report", 
        #     "url": "risk_detail_report",  # Ensure this matches the URL name in urls.py
        #     "permissions": ["orm.view_risk"]
        # },
        
          # Your models
        {"model": "Risks", "name": "Risks", "url": "admin:orm_risk_changelist", "permissions": ["orm.view_risk"]},
        {"model": "Procedures", "name": "Procedures", "url": "admin:orm_procedure_changelist", "permissions": ["orm.view_procedure"]},
        {"model": "Mitigations", "name": "Mitigations", "url": "admin:orm_mitigation_changelist", "permissions": ["orm.view_mitigation"]},
        {"model": "Actions", "name": "Actions", "url": "admin:orm_action_changelist", "permissions": ["orm.view_action"]},
        {"model": "Indicators", "name": "Indicators", "url": "admin:orm_indicator_changelist", "permissions": ["orm.view_indicator"]},
        {"model": "Events", "name": "Events", "url": "admin:orm_event_changelist", "permissions": ["orm.view_event"]},
        {"model": "Approvals", "name": "Approvals", "url": "admin:orm_approvalrequest_changelist", "permissions": ["orm.view_approvalrequest"], "icon": "fa-check-double"},
        {"model": "Assessments", "name": "Assessments", "url": "admin:orm_riskassessment_changelist", "permissions": ["orm.view_riskassessment"]},

    ],
    

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        

    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth","orm.UserProfile","HeatMaps","Categories View", "Risk Detail Report","Portfolios View", "orm.Risk", "orm.Procedure", "orm.Mitigation", "orm.Action", "orm.Indicator", "orm.Event", "orm.ApprovalRequest", "orm.RiskAssessment", "orm.Category", "orm.Portfolio", "orm.IndicatorValueHistory", "orm.RiskScoreHistory" ],

    # Custom links to append to app groups, keyed on app name
     "custom_links": {
         
        "orm": [  # Replace with your app's name
             {
                "name": "HeatMaps", 
                "url": "interactive_heatmap",  # URL name must match the one in urls.py
                "icon": "fas fa-chart-pie",  # Optional: Add an icon
                "permissions": ["orm.view_risk"]
            },
            #  {
            #     "name": "Portfolios HeatMaps", 
            #     "url": "portfolio_heatmap",  # URL name must match the one in urls.py
            #     "icon": "fas fa-chart-pie",  # Optional: Add an icon
            #     "permissions": ["orm.view_risk"]
            # },
            {
                "name": "Portfolios View", 
                "url": "risk_by_portfolio",  # URL name must match the one in urls.py
                "icon": "fas fa-chart-pie",  # Optional: Add an icon
                "permissions": ["orm.view_risk"]
            },
            {
                "name": "Categories View", 
                "url": "risk_category_charts",  # URL name must match the one in urls.py
                "icon": "fas fa-chart-pie",  # Optional: Add an icon
                "permissions": ["orm.view_risk"]
            },
            {
                "name": "Risk Detail Report", 
                "url": "risk_detail_report",  # URL name must match the one in urls.py
                "icon": "fas fa-file-alt",  # Optional: Add an icon
                "permissions": ["orm.view_risk"]
            },
        ],
    },

    
    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "orm.Risk": "fas fa-exclamation-triangle",
        "orm.Action": "fas fa-bolt",
        "orm.RiskAssessment": "fas fa-balance-scale",
        "orm.userprofile": "fas fa-id-card",
        "orm.Procedure": "fas fa-table",
        "orm.Event": "fas fa-bell",
        "orm.Mitigation": "fas fa-shield-alt",
        "orm.approvalrequest": "fas fa-check-double",
        "orm.Indicator": "fas fa-chart-line",
        "orm.category": "fas fa-list",
        "orm.portfolio": "fas fa-briefcase",
        "orm.indicatorvaluehistory":"fas fa-clock",
        "orm.riskscorehistory":"fas fa-clock",

    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"orm.risk":"collapsible","auth.user": "collapsible", "auth.group": "vertical_tabs"},
    
  




}


JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-navy",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-navy",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": True,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": True
}