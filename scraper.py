from modules.scraper.CorynScraper import CorynScraper


def main():

    scraper = CorynScraper()

    scraper.scrape('equipments')
    scraper.scrape('consumables')
    scraper.scrape('crystals')


if __name__ == '__main__':
    main()
