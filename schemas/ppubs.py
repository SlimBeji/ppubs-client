from marshmallow import EXCLUDE

from extensions import ma


class CrwalPatentHighlightGet(ma.Schema):
    class Meta:
        unknown = EXCLUDE

    query = ma.String(required=True)


class CrwalPatentHighlightGetResponse(ma.Schema):
    html = ma.String(required=True)


class ClearCacheGetResponse(ma.Schema):
    hits = ma.Integer(required=True)
    misses = ma.Integer(required=True)
    maxsize = ma.Integer(required=True)
    currsize = ma.Integer(required=True)
