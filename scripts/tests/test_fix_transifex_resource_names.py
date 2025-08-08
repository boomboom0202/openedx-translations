"""
Tests for fix_transifex_resource_names.py.
"""

import pytest

from unittest.mock import MagicMock
from ..fix_transifex_resource_names import (
    get_repo_name_from_resource,
    get_repo_slug_from_resource,
)


@pytest.fixture(autouse=True)
def mock_random_choice(monkeypatch):
    monkeypatch.setattr('random.choice', lambda x: '9')


def test_get_repo_slug_from_resource_with_no_categories():
    resource = MagicMock()
    resource.slug = 'translations-my-xblock-conf-locale-en-lc-messages-django-po--main'
    resource.categories = []
    assert get_repo_slug_from_resource(resource) == 'my-xblock-r999999'


def test_get_repo_slug_from_resource_slug_js_with_no_categories():
    resource = MagicMock()
    resource.slug = 'translations-my-xblock-conf-locale-en-lc-messages-djangojs-po--main'
    resource.categories = []
    assert get_repo_slug_from_resource(resource) == 'my-xblock-js-r999999'


def test_get_repo_name_from_invalid_slug():
    resource = MagicMock()
    resource.slug = 'some-gibberish-slug'
    resource.categories = []
    assert get_repo_name_from_resource(resource) == None


def test_get_repo_name_from_slug_and_categories():
    """
    Categories takes precedence over slug.
    """
    resource = MagicMock()
    resource.slug = 'translations-my-xblock1-conf-locale-en-lc-messages-django-po--main'
    resource.categories = ['github#repository:openedx/openedx-translations#branch:main#path:translations/my-xblock2/openassessment/conf/locale/en/LC_MESSAGES/django.po']  # noqa
    assert get_repo_name_from_resource(resource) == 'my-xblock2'


def test_get_repo_name_from_categories():
    resource = MagicMock()
    resource.slug = 'some-gibberish-slug'
    resource.categories = ['github#repository:openedx/openedx-translations#branch:main#path:translations/my-xblock2/openassessment/conf/locale/en/LC_MESSAGES/django.po']  # noqa
    assert get_repo_name_from_resource(resource) == 'my-xblock2'


def test_get_repo_name_from_categories_with_js():
    resource = MagicMock()
    resource.slug = 'some-gibberish-slug'
    resource.categories = ['github#repository:openedx/openedx-translations#branch:main#path:translations/my-xblock2/openassessment/conf/locale/en/LC_MESSAGES/djangojs.po']  # noqa
    assert get_repo_name_from_resource(resource) == 'my-xblock2-js'


def test_get_repo_name_from_invalid_slug_with_force_suffix():
    resource = MagicMock()
    resource.slug = 'some-gibberish-slug'
    resource.categories = ['github#repository:openedx/openedx-translations#branch:main#path:translations/my-xblock2/openassessment/conf/locale/en/LC_MESSAGES/djangojs.po']  # noqa
    resource.categories = []
    assert get_repo_name_from_resource(resource) == 'my-xblock2-js'


def test_get_repo_slug_from_resource_with_force_suffix():
    resource = MagicMock()
    resource.slug = 'some-gibberish-slug'
    resource.name = 'Some Gibberish Slug'
    resource.categories = []
    # Mock the random number generation for consistent test results
    with mock.patch('random.choice', side_effect=lambda x: '0'):
        result = get_repo_slug_from_resource(resource)
        # Should add -r followed by 6 digits
        assert result == 'some-gibberish-slug-r000000'
        assert result.endswith('-r000000')


def test_get_repo_slug_from_resource_with_existing_r_suffix():
    resource = MagicMock()
    resource.slug = 'my-resource-r123456'
    resource.name = 'my-resource-r123456'
    resource.categories = []
    # Should keep the existing suffix without adding a new one
    assert get_repo_slug_from_resource(resource) == 'my-resource-r123456'


def test_get_repo_slug_from_resource_with_clean_name(monkeypatch):
    resource = MagicMock()
    resource.slug = 'clean-name'
    resource.name = 'Clean Name'  # Clean name in title case
    resource.categories = []
    monkeypatch.setattr('random.choice', lambda x: '0')
    result = get_repo_slug_from_resource(resource)
    # Should add unique suffix to clean names
    assert result == 'clean-name-r000000'


def test_parse_arguments():
    test_args = [
        '--tx-project-slug', 'test-project',
        '--dry-run',
        '--force-suffix'
    ]
    with unittest.mock.patch('sys.argv', ['test_script.py'] + test_args):
        args = parse_arguments()
        assert args.tx_project_slug == 'test-project'
        assert args.dry_run is True
        assert args.force_suffix is True


def test_parse_arguments_minimal():
    test_args = ['--tx-project-slug', 'test-project']
    with unittest.mock.patch('sys.argv', ['test_script.py'] + test_args):
        args = parse_arguments()
        assert args.tx_project_slug == 'test-project'
        assert args.dry_run is False
        assert args.force_suffix is False
