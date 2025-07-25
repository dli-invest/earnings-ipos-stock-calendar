from es_cal.browser.trading_view import get_earnings
from es_cal.browser.fetch_ipos import fetch_ipos
from icecream import ic

def main():
    ic()
    ic("Running get earnings")
    # get_earnings()
    ic()
    fetch_ipos()
    


if __name__ == "__main__":
    main()
