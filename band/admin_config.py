from django.contrib.admin.apps import AdminConfig


class BandAdminConfig(AdminConfig):
    default_site = "band.admin_site.BandAdminSite"
