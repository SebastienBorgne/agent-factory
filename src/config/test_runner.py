from django.test.runner import DiscoverRunner

# Domain/application/infrastructure tests live alongside their code under
# src/, not inside a Django app's tests.py — Django's default discovery only
# looks at INSTALLED_APPS, so `manage.py test` (no labels) would otherwise
# find nothing. Default to scanning our three top-level packages instead.
_DEFAULT_LABELS = ["domain", "application", "infrastructure", "config"]


class ProjectTestRunner(DiscoverRunner):
    # Signature must match DiscoverRunner.build_suite exactly to override it.
    def build_suite(self, test_labels=None, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
        return super().build_suite(test_labels or _DEFAULT_LABELS, *args, **kwargs)
