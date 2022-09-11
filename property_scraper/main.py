import argparse
import datetime
from WebCrawlerClass import *
from auctions import Auction


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
    auction = Auction()

    # Add the webcrawlers specified by the user into the auctions class
    if args.website is None:
        websites = list(auction.URLS.keys())
    else:
        websites = args.website.split(',')

    for website in websites:
        auction.add_webcrawler(eval(website), url=auction.URLS[website], printlog=True)

    # run the scrape
    auction.scrape()

    outfileName = "scrapeddata_" + date.today().strftime("%Y%m%d") + ".csv"
    auction.scrapeddata.to_csv(outfileName, index=False, encoding='utf-8')

    # clean the data
    #auction.clean_data()

    # analyze the data
    #auction.analyze()

