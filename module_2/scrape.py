import urllib3
from urllib.parse import urlencode

BASE_URL = "https://www.thegradcafe.com/survey"

http = urllib3.PoolManager()


def build_url(page=1):
    params = {
        "page": page,
        "sort": "newest"
    }

    return BASE_URL + "?" + urlencode(params)


def fetch_page(page=1):
    url = build_url(page)

    response = http.request(
        "GET",
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    print("Status:", response.status)
    print("URL:", url)

    html = response.data.decode("utf-8", errors="replace")
    import os
    print("Current directory:", os.getcwd())
    with open("page1.html", "w", encoding="utf-8") as f:
     f.write(html)

    print("Saved page1.html")

    print("Length:", len(html))

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    app_div = soup.find("div", id="app")

    print("Found app div:", app_div is not None)

    print("Attributes:")
    print(app_div.attrs.keys())

    data_page = app_div["data-page"]

    print("Length of data-page:", len(data_page))
  

if __name__ == "__main__":
    fetch_page(1)

