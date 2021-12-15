from lxml import html
import requests
import argparse
import json


def parse(address):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }

    response = requests.get(
        f"https://www.redfin.com/stingray/do/location-autocomplete?location={address}&start=0&count=10&v=2", headers=headers)

    result = json.loads(response.text.replace("{}&&{", '{'))

    relative_path = result.get('payload', {}).get('exactMatch', {}).get('url')
    if relative_path is None:
        relative_path = result.get('payload').get(
            'sections', [])[0].get('rows', [])[0].get('url')

    if not relative_path:
        return None

    url = f'https://www.redfin.com/{relative_path}'

    # Find the location url
    response = requests.get(url, headers=headers)

    # Print Status Code
    print(response.status_code)
    parser = html.fromstring(response.text)

    raw_street_view = parser.xpath(
        "//*[@class=' streetview']/@src")
    raw_street = parser.xpath(
        "//*[@class='street-address']/span/text()")
    raw_state_zip = parser.xpath("//*[@class='dp-subtext']//text()")
    raw_price = parser.xpath(
        "//*[@class='stat-block price-section']/div/text()")
    raw_bed = parser.xpath(
        "//*[@class='stat-block beds-section']/div/text()")
    raw_bath = parser.xpath(
        "//*[@class='stat-block baths-section']/div/text()")
    raw_size = parser.xpath(
        "//*[@class='stat-block sqft-section']/span/text()")

    street_view = ''.join(raw_street_view) if raw_street_view else None
    street = ''.join(raw_street).strip() if raw_street else None
    state_zip = ''.join(raw_state_zip).strip() if raw_state_zip else None
    price = ''.join(raw_price).strip() if raw_price else None
    bed = ''.join(raw_bed).strip() if raw_bed else None
    bath = ''.join(raw_bath).strip() if raw_bath else None
    size = ''.join(raw_size).strip() if raw_size else None

    return {
        'street_view': street_view,
        'street': street,
        'state_zip': state_zip,
        'price': price,
        'bed': bed,
        'bath': bath,
        'size': size
    }


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('address', help='')

    args = argparser.parse_args()
    address = args.address
    print("Fetching data for %s" % (address))
    scraped_data = parse(address)
    print(scraped_data)
