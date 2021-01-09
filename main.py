import datetime
import argparse
from WebCrawlerClass import *
from GLOBAL_VARS import *
from auctions import auctions


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
    auctions = auctions()

    # Add the webcrawlers specified by the user into the auctions class
    if args.website is None:
        websites_list = list(auctionUrls_dict.keys())
    else:
        websites_list = args.website.split(',')

    for website in websites_list:
        auctions.addwebcrawler(eval(website), url=auctionUrls_dict[website], printlog=True)

    # run the scrape
    auctions.scrape()

    outfileName = "scrapeddata_" + date.today().strftime("%Y%m%d") + ".csv"
    auctions.scrapeddata.to_csv(outfileName, index=False, encoding='utf-8')

    # clean the data
    #auctions.cleandata()

    # analyze the data
    #auctions.analyze()

