from flask import Blueprint, make_response
from ckanext.odm_dataset_ext import utils

odm_dataset_views = Blueprint('odm_dataset', __name__)


def odm_dataset_autocomplete():
    data = utils.odm_autocomplete_dataset()
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response


def odm_keyword_autocomplete():
    data = utils.odm_auto_complete_keyword()
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    return response


odm_dataset_views.add_url_rule(
    "/dataset/reference/<reference>", methods=["GET"], view_func=utils.read_reference
)
odm_dataset_views.add_url_rule(
    "/dataset/<id>/resource/<rid>/detail", methods=["GET"], view_func=utils.resource_read_detail
)
odm_dataset_views.add_url_rule(
    "/dataset/autocomplete", methods=["GET"], view_func=odm_dataset_autocomplete
)
odm_dataset_views.add_url_rule(
    "/dataset/keyword_autocomplete", methods=["GET"], view_func=odm_keyword_autocomplete
)
