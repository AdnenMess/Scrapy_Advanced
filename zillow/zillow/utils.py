from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, urlencode
import json

URL = "https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState=%7B%22usersSearchTerm%22%3A%22Miami%2C%20FL%22%2C%22mapBounds%22%3A%7B%22west%22%3A-80.63932264013673%2C%22east%22%3A-79.95611035986329%2C%22south%22%3A25.506499981238925%2C%22north%22%3A25.945693613208114%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A12700%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Afalse%2C%22filterState%22%3A%7B%22sortSelection%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22isAllHomes%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A11%7D&wants={%22cat1%22:[%22listResults%22],%22cat2%22:[%22total%22]}&requestId=6"


def cookie_parser():
    cookie_string = "zguid=24|%2412f6bae2-de68-4071-a705-8a475e662535; zgsession=1|84da2197-4015-4825-b370-b6241bd9c9f8; JSESSIONID=05C9A8D4E2339F0EB4B5F5E45C57359F; AWSALB=/tOmURodpUPeiZH1oJp49RBbeJ+y30aBipDQFp34j5rC2QZtj1/ysQEq4r93N59kXe1I01Fctl3dzsosUm/yHJ3H9l/uvzb8eqA+mHYffX4Dy4GXZ6Y1OBBMX1Ol; AWSALBCORS=/tOmURodpUPeiZH1oJp49RBbeJ+y30aBipDQFp34j5rC2QZtj1/ysQEq4r93N59kXe1I01Fctl3dzsosUm/yHJ3H9l/uvzb8eqA+mHYffX4Dy4GXZ6Y1OBBMX1Ol; search=6|1666205654724%7Crect%3D25.945693613208114%252C-79.95611035986329%252C25.506499981238925%252C-80.63932264013673%26rid%3D12700%26disp%3Dmap%26mdm%3Dauto%26p%3D3%26z%3D1%26fs%3D1%26fr%3D0%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%09%0912700%09%09%09%09%09%09"
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


def parse_new_url(url, page_number):
    url_parsed = urlparse(url)
    query_string = parse_qs(url_parsed.query)
    search_query_state = json.loads(query_string.get('searchQueryState')[0])
    search_query_state['pagination'] = {"currentPage": page_number}
    query_string.get('searchQueryState')[0] = search_query_state
    encoded_qs = urlencode(query_string, doseq=1)
    new_url = f"https://www.zillow.com/search/GetSearchPageState.htm?{encoded_qs}"
    return new_url


parse_new_url(URL, 3)
