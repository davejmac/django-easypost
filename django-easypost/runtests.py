import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests(*test_args):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'easypost.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['easypost'])
    sys.exit(bool(failures))


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
