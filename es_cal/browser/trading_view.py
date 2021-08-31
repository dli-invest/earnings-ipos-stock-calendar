import pandas as pd
import requests
import es_cal.gcal.config as cfg
import time
from datetime import datetime
from es_cal.gcal import make_event_in_gcal
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    ElementNotVisibleException,
)
from es_cal.browser import make_webdriver
from es_cal.discord import send_message
from es_cal.gcal.utils import get_tickers, split_string


"""
1. Open the website
2. Wait for the table to load
3. Grab the table
4. Close the browser
"""
def get_earnings():
    driver = make_webdriver()

    driver.get("https://www.tradingview.com/markets/stocks-canada/earnings/")
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "item-17wa4fow"))
        )
    except Exception as e:
        print(e)
    # will throw error if it is not available
    # Grab data for next week
    # Xpath version
    # link = driver.find_element_by_xpath('//*[@id="js-screener-container"]/div[2]/div[6]/div/div/div[4]')
    # link.click()
    #  div.tv-screener-toolbar__period-picker > div > div > div:nth-child(5)")
    # div.tv-screener-toolbar__period-picker > div > div > div:nth-child(4)
    day_int = datetime.today().weekday()
    table_selector = (
        "div.tv-screener-toolbar__period-picker > div > div > div:nth-child(4)"
    )
    if day_int == 6:
        table_selector = (
            "div.tv-screener-toolbar__period-picker > div > div > div:nth-child(5)"
        )
    link = driver.find_element_by_css_selector(table_selector)
    link.click()
    # Sleep since time delays aren't a huge deal for me
    time.sleep(10)

    # up to 10 tries
    for x in range(10):
        print(x)
        try:
            load_more = driver.find_element_by_css_selector(
                "div.tv-load-more.tv-load-more--screener.js-screener-load-more > span"
            )
            load_more.click()
            time.sleep(10)
        except NoSuchElementException as e:
            # likely does not have a load more button
            if x == 0:
                break
            print(e)
            continue
        except ElementNotInteractableException as e:
            print(e)
            break
        except ElementNotVisibleException as e:
            print(e)
            break
    # purge spans that represent long names
    driver.execute_script(
        """
        var element = document.getElementsByClassName("tv-screener__description"), index;
        for (index = element.length - 1; index >= 0; index--) {
            element[index].parentNode.removeChild(element[index]);
        }
    """
    )
    # purge D at end
    driver.execute_script(
        """
        var element = document.getElementsByClassName("tv-data-mode tv-data-mode--for-screener apply-common-tooltip tv-data-mode--delayed tv-data-mode--delayed--for-screener"), index;
        for (index = element.length - 1; index >= 0; index--) {
            element[index].parentNode.removeChild(element[index]);
        }
    """
    )
    # remove ticker total
    driver.execute_script(
        """
        var element = document.getElementsByClassName("tv-screener-table__field-value--total"), index;
        for (index = element.length - 1; index >= 0; index--) {
            element[index].parentNode.removeChild(element[index]);
        }
    """
    )
    #
    table_content = driver.page_source
    try:
        html_table_list = pd.read_html(table_content, attrs={"class": "tv-data-table"})
        html_df = html_table_list[0]
        html_df.drop_duplicates(keep="first", inplace=True)
    except ValueError as e:
        print(e)
        with open("index.html", "w", errors="ignore") as f:
            f.write(table_content)
        # send alert
        send_message(f"Earnings stock calendar - error: {str(e)}")
        return
    data = get_tickers()
    html_df["Ticker"] = html_df["Ticker"].apply(lambda x: split_string(x))
    clean_df = html_df[html_df.iloc[:, 0].isin(data)]
    run_date = datetime.today().strftime('%Y-%m-%d')
    clean_df.to_csv(f"artifacts/{run_date}_earnings.csv", index=False)
    for index, row in clean_df.iterrows():
        earnings_date = row["Date"]
        ticker = row["Ticker"]
        print(row["Ticker"], row["Date"])
        extracted_date = datetime.strptime(earnings_date, "%Y-%m-%d")
        earnings_year = extracted_date.year
        quarter = map_month_to_quarter(extracted_date.month)
        event_name = f"{ticker} {quarter} {earnings_year} Earnings"
        make_event_in_gcal(event_name, earnings_date)
    # html_df.iloc[:, 0].values.tolist()
    # for
    # iterate across df and add to python scheduler
    # Click the Load More Button
    # driver.close()


def map_month_to_quarter(month):
    switcher = {
        1: "Q1",
        2: "Q1",
        3: "Q1",
        4: "Q2",
        5: "Q2",
        6: "Q2",
        7: "Q3",
        8: "Q3",
        9: "Q3",
        10: "Q4",
        11: "Q4",
        12: "Q4",
    }
    return switcher.get(month, "Q1")


def main():
    get_earnings()


if __name__ == "__main__":
    main()
