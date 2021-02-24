from ckanext.odm_dataset_ext.tests import odm_dataset_factories
from ckanext.odm_dataset_ext.plugin import Odm_Dataset_ExtPlugin
from ckanext.odm_dataset_ext.logic import action
from ckan.plugins import toolkit
from ckan.tests import factories
import ckan.tests.helpers as helpers
from ckan import model
from ckan import logic
from ckan.logic import _actions
import pytest
import mock


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOdmDatasetAPIActions:

    def setup(self):
        """
        # create dataset
        # create resource
        # create user
        # create sysadmin
        :return:
        """
        self._org = factories.Organization()
        self._user = factories.User()
        self._org_editor = helpers.call_action(
            "organization_member_create",
            id=self._org["id"],
            username=self._user["name"],
            role="editor",
        )

    def test_package_create(self):
        """
        All the packages created by non admin is private
        :return:
        """
        context = {
            'user': self._user['name'],
            'model': model,
            'ignore_auth': False
        }
        helpers.call_action(
            "package_create",
            context=context,
            name="test-dataset",
            notes_translated={"en": "test"},
            odm_spatial_range="km",
            owner_org=self._org['id']
        )

        pkg = toolkit.get_action('package_show')(context, {'id': 'test-dataset'})
        assert pkg['type'] == 'dataset'
        assert pkg['private']

    def test_package_search(self, monkeypatch):

        def package_search_patch(context, data_dict):
            res = action.package_search(context, data_dict)
            found = False
            for x in data_dict.get('fq_list', []):
                if "extras_odm_spatial_range" in x:
                    found = True
                    break
            assert "fq_list" in data_dict
            assert found
            return res

        monkeypatch.setitem(_actions, 'package_search', package_search_patch)
        helpers.call_action('package_search',
                            context={'user': None, 'model': model, 'session': model.Session})

    def test_dataset_autocomplete(self):

        pkg = odm_dataset_factories.OdmDataset().create(
            name="test_odm_auto_complete",
            title_translated={'en': "test auto Complete"}
        )

        # not full match
        q = pkg['name'][:len(pkg['name'])-2]
        _res = toolkit.get_action('odm_dataset_autocomplete')({'user': None, 'model': model,
                                                               'session': model.Session},
                                                              {'q': q, 'type': "dataset"}
                                                              )
        assert len(_res) >= 1
        assert _res[0]['name'] == pkg['name']

        q = "test auto Com"
        _res = toolkit.get_action('odm_dataset_autocomplete')({'user': None, 'model': model,
                                                               'session': model.Session},
                                                              {'q': q, 'type': "dataset"}
                                                              )
        assert len(_res) >= 1
        assert _res[0]['title'] == pkg['title_translated']['en']

    def test_dataset_autocomplete_exact(self):

        pkg = odm_dataset_factories.OdmDataset().create(
            name="test_odm_auto_complete_exact",
            title_translated={'en': "test auto Complete"}
        )

        # Exact match
        q = pkg['name']
        _res = toolkit.get_action('odm_dataset_autocomplete_exact')({'user': None, 'model': model,
                                                                     'session': model.Session},
                                                                    {'q': q, 'type': "dataset"}
                                                                    )
        assert len(_res) >= 1
        assert _res[0]['name'] == pkg['name']

        q = "test_odm_auto"
        with pytest.raises(logic.NotFound):
            _ = toolkit.get_action('odm_dataset_autocomplete_exact')({'user': None, 'model': model,
                                                                      'session': model.Session},
                                                                      {'q': q, 'type': "dataset"}
                                                                     )

    def test_keywords_autocomplete(self):

        # Keywords has taxonomy tag dependency
        factories.Vocabulary(name="taxonomy", tags=[
            {
               "name": "Test 1"
            },
            {
                "name": "Test 2"
            }
        ])

        pkg = odm_dataset_factories.OdmDataset().create(
            name="test_odm_auto_complete_exact",
            title_translated={'en': "test auto Complete"},
            odm_keywords="land,infrastructure,transport"
        )

        assert "odm_keywords" in pkg
        assert pkg['odm_keywords'] == "land,infrastructure,transport"

        # Exact match
        q = "land"
        _res = toolkit.get_action('odm_keyword_autocomplete')({'user': None, 'model': model,
                                                               'session': model.Session},
                                                              {'q': q, 'type': "dataset"}
                                                              )
        assert len(_res) >= 1
        assert _res[0]['name'] == pkg['name']

        # Near match
        q = "transp"
        _res = toolkit.get_action('odm_keyword_autocomplete')({'user': None, 'model': model,
                                                               'session': model.Session},
                                                              {'q': q, 'type': "dataset"}
                                                              )
        assert len(_res) >= 1
        assert _res[0]['name'] == pkg['name']

    def test_unsafe_user_show(self):

        _user1 = factories.User()

        context = {
            "user": self._user['name'],
            "model": model,
            "session": model.Session,
            "unsafe_user_show": True
        }

        user = action.unsafe_user_show(context, {"id": _user1['id']})
        show = toolkit.get_action('user_show')(context, {"id": _user1["id"]})

        # user show and unsafe_user_show both are same
        assert user
        assert show
        assert "fullname" in user
        assert "display_name" in user
        assert len(user) != len(show)