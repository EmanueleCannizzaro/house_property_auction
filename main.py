import datetime
import argparse
from WebCrawlerClass import *
from GLOBAL_VARS import *


def parse_args():
    now = datetime.datetime.now().strftime("%Y_%m_%d")  # string to be used after
    parser = argparse.ArgumentParser(description='main class to scrape auction websites')
    parser.add_argument('--website', type=str, default=None, required=False,
                        help='Input website to use for the scrape, if empty all available websites are used')
    return parser.parse_args()

# Main
if __name__ == "__main__":
    args = parse_args()

    data = []
    webcrawlers = []

    if args.website == "astegiudiziarie":
        webcrawlers.append(astegiudiziarie(auctionUrls_dict["astegiudiziarie"]))
    elif args.website == "astalegale":
        webcrawlers.append(astalegale(auctionUrls_dict["astalegale"]))
    elif args.website == "REdiscount":
        webcrawlers.append(REdiscount(auctionUrls_dict["REdiscount"]))
    elif args.website == "asteRE":
        webcrawlers.append(asteRE(auctionUrls_dict["asteRE"]))
    elif args.website == "giustizia":
        webcrawlers.append(giustizia(auctionUrls_dict["giustizia"]))
    else:
        webcrawlers.append(astegiudiziarie(auctionUrls_dict["astegiudiziarie"]))
        webcrawlers.append(astalegale(auctionUrls_dict["astalegale"]))
        webcrawlers.append(REdiscount(auctionUrls_dict["REdiscount"]))
        webcrawlers.append(asteRE(auctionUrls_dict["asteRE"]))
        webcrawlers.append(giustizia(auctionUrls_dict["giustizia"]))

    for webcrawler in webcrawlers:
        data.append(webcrawler.scrape())

    outfileName = "scrapeddata_" + date.today().strftime("%Y%m%d") + ".txt"
    data.to_csv(outfileName, index=False, encoding='utf-8')
