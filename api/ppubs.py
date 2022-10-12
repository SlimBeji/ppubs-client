from http import HTTPStatus

from flask import render_template
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from schemas.ppubs import (
    CrwalPatentHighlightGet,
    CrwalPatentHighlightGetResponse,
    ClearCacheGetResponse
)
from core.ppub_crawler import (
    search_for_patent_highlight,
    extract_html_from_highlight,
    clear_search_for_patent_highlight_cache
)


ppubs_blueprint = Blueprint("Ppubs", __name__, url_prefix="/api/ppubs")


@ppubs_blueprint.route("/crawl")
class CrwalPatentHighlight(MethodView):
    @ppubs_blueprint.arguments(CrwalPatentHighlightGet, location="query")
    @ppubs_blueprint.response(HTTPStatus.OK, CrwalPatentHighlightGetResponse)
    def get(self, args):
        identifier = args.get("identifier")
        highlight = search_for_patent_highlight(identifier)
        if "error" in highlight:
            abort(highlight.get("status"), message=highlight.get("error"))

        html_feed_data = extract_html_from_highlight(highlight)
        html = render_template("patent_highlight.j2", **html_feed_data)
        
        return dict(html=html)


@ppubs_blueprint.route("/cache/clear")
class ClearCache(MethodView):
    @ppubs_blueprint.response(HTTPStatus.OK, ClearCacheGetResponse)
    def get(self):
        cache_data = clear_search_for_patent_highlight_cache()
        return cache_data
