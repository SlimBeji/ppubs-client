from ast import parse
from functools import lru_cache
from http import HTTPStatus
import requests
import json
import re


DEFAULT_CASE_ID = 965150
DEFAULT_USER_ID = 972022
MAX_CASH_QUERY_SEARCH_COUNT = 100


def get_session_data():
    request_session_url = "https://ppubs.uspto.gov/dirsearch-public/users/me/session"
    headers = {"content-type":"application/json"}
    response = requests.post(request_session_url, headers=headers, data="-1")
    if response.status_code != 200:
        return {}
    
    data = response.json()
    user_id = data.get("userCase",{}).get("userId")
    case_id = data.get("userCase",{}).get("caseId")
    
    return dict(user_id=user_id, case_id=case_id)


def _build_search_with_be_familiy_payload(query, start=0, page_count=500, case_id=None):
    """It looks like caseId is mandatory for this request
    Testing with dummy number does not seems to work
    Not sure if we will have to always fetch new sessions"""
    if case_id is None:
        case_id = DEFAULT_CASE_ID
        
    payload = {
        "start":start,
        "pageCount":page_count,
        "sort":"date_publ desc",
        "docFamilyFiltering":"familyIdFiltering",
        "searchType":1,
        "familyIdEnglishOnly":True,
        "familyIdFirstPreferred":"US-PGPUB",
        "familyIdSecondPreferred":"USPAT",
        "familyIdThirdPreferred":"FPRS",
        "showDocPerFamilyPref":"showEnglish",
        "queryId":0,
        "tagDocSearch":False,
        "query":{
            "caseId":case_id,
            "hl_snippets":"2",
            "op":"OR",
            "q":query,
            "queryName":query,
            "highlights":"1",
            "qt":"brs",
            "spellCheck":True,
            "viewName":"tile",
            "plurals":True,
            "britishEquivalents":True,
            "databaseFilters":[
                {"databaseName":"US-PGPUB","countryCodes":[]},
                {"databaseName":"USPAT","countryCodes":[]},
                {"databaseName":"USOCR","countryCodes":[]}
            ],
            "searchType":1,
            "ignorePersist":False,
            "userEnteredQuery":query,
            "dateCreated":None,
            "pNumber":1,
            "tags":[]
        }
    }
    
    return payload


def get_patents(query, start=0, page_count=500, case_id=None):
    search_url = "https://ppubs.uspto.gov/dirsearch-public/searches/searchWithBeFamily"
    headers = {"content-type":"application/json; charset=UTF-8"}
    payload = _build_search_with_be_familiy_payload(
        query, start=start, page_count=page_count, case_id=case_id
    )
    response = requests.post(search_url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        return None
    
    data = response.json()
    patents = data.get("patents", [])
    return patents


def match_patent_guid(guid, patents):
    for patent in patents:
        if re.search(guid, patent.get("guid", "")):
            return patent
    
    return None


def get_patent_highlight(guid):
    highlight_url = f"https://ppubs.uspto.gov/dirsearch-public/patents/{guid}/highlight?queryId=0&source=USPAT&includeSections=true&uniqueId="
    headers = {"content-type":"application/json; charset=UTF-8"}
    response = requests.get(highlight_url, headers=headers)
    if response.status_code != 200:
        return None
    
    data = response.json()
    return data


@lru_cache(maxsize=MAX_CASH_QUERY_SEARCH_COUNT)
def search_for_patent_highlight(query):
    patents = get_patents(query)
    if patents is None:
        return dict(
            status=HTTPStatus.NOT_FOUND,
            error="No patent returned matched the query %s" % query
        )

    patent = match_patent_guid(query, patents)
    if patent is None:
        return dict(
            status=HTTPStatus.NOT_FOUND,
            error="No patent returned matched the query %s" % query
        )

    guid = patent.get("guid","")
    highlight = get_patent_highlight(guid)
    if highlight is None:
        return dict(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            error="Something went wrong when fetching highlight for patent with GUID %s" % guid
        )

    return highlight


def clear_search_for_patent_highlight_cache():
    cache_data = search_for_patent_highlight.cache_info()
    search_for_patent_highlight.cache_clear()
    return dict(
        hits=cache_data.hits,
        misses=cache_data.misses,
        maxsize=cache_data.maxsize,
        currsize=cache_data.currsize
    )


def _parse_html_text(html):
    if html is None:
        return "";

    html = html.replace("<br/>","<br/><br/>")
    html = html.replace("<br />","<br/><br/>")
    html = html.replace("\n","<br><br>")
    return html


def extract_html_from_highlight(highlight):
    """
    Some nodes are present in the HTML with display: none
    No matching content was found in the highligh response
    examples: equivalentAbstractNode, chemicalCodesNode, sequenceListingNode
    """
    
    abstract_html = _parse_html_text(highlight.get("abstractHtml",""))
    equivalent_abstract_html = _parse_html_text(highlight.get("equivalentAbstractHtml",""))
    background_text_html = _parse_html_text(highlight.get("backgroundTextHtml",""))
    brief_html = _parse_html_text(highlight.get("briefHtml",""))
    description_html = _parse_html_text(highlight.get("descriptionHtml",""))
    chemical_codes_html = _parse_html_text(highlight.get("chemicalCodesHtml",""))
    claims_html = _parse_html_text(highlight.get("claimsHtml",""))
    sequence_listing_html = _parse_html_text(highlight.get("sequenceListingHtml",""))

    return dict(
        abstract_html=abstract_html,
        equivalent_abstract_html=equivalent_abstract_html,
        background_text_html=background_text_html,
        brief_html=brief_html,
        description_html=description_html,
        chemical_codes_html=chemical_codes_html,
        claims_html=claims_html,
        sequence_listing_html=sequence_listing_html,
    )
