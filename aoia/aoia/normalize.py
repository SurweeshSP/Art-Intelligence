from .models import Opportunity

def normalize_data(opp: Opportunity) -> Opportunity:
    import urllib.parse
    domain = urllib.parse.urlparse(opp.application_url).netloc.lower()
    
    if opp.location.city in ["Chennai", "Tamil Nadu"] or opp.location.city == "Chennai":
        opp.geo_scope = "CHENNAI"
    elif opp.location.country == "IN" or opp.location.city in ["Delhi"]:
        opp.geo_scope = "INDIA"
    elif ".in" in domain:
        opp.geo_scope = "INDIA"
    elif ".sg" in domain:
        opp.geo_scope = "INTERNATIONAL"
    else:
        opp.geo_scope = "INTERNATIONAL"
    return opp
