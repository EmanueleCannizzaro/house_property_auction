from requests import request
import json

url = 'https://scrapeninja.p.rapidapi.com/scrape'

# get your subscription key at https://rapidapi.com/restyler/api/scrapeninja from "Code generator",
# copy and paste it to 'x-rapidapi-key' header below

headers = {
    "Content-Type": "application/json",
    "x-rapidapi-host": "scrapeninja.p.rapidapi.com",
    "x-rapidapi-key": "d2a90fb2d1msh28de0680a4be71cp1ee84ejsn34e85f370152"
}

payload =  {
  "url": "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E219&amp;minBedrooms=2&amp;maxPrice=550000&amp;minPrice=50000&amp;propertyTypes=&amp;includeSSTC=false&amp;mustHave=&amp;dontShow=&amp;furnishTypes=&amp;keywords=",
  "method": "GET",
  "retryNum": 3,
  "geo": "fr",
  "extractor": "// define function which accepts body and cheerio as args\nfunction extract(input, cheerio) {\n    // return object with extracted values              \n    let $ = cheerio.load(input);\n  \n    let items = [];\n    $('.titleline').map(function() {\n          \tlet infoTr = $(this).closest('tr').next();\n      \t\tlet commentsLink = infoTr.find('a:contains(comments)');\n            items.push([\n                $(this).text(),\n              \t$('a', this).attr('href'),\n              \tinfoTr.find('.hnuser').text(),\n              \tparseInt(infoTr.find('.score').text()),\n              \tinfoTr.find('.age').attr('title'),\n              \tparseInt(commentsLink.text()),\n              \t'https://news.ycombinator.com/' + commentsLink.attr('href'),\n              \tnew Date()\n            ]);\n        });\n  \n  return { items };\n}"
}

response = request("POST", url, json=payload, headers=headers)

response_json = json.loads(response.text)
print(response.__dict__)
print(response_json)
