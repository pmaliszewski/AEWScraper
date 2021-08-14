import datetime
from typing import List, Optional

import bs4.element
from bs4 import BeautifulSoup
from selenium import webdriver

from constants import (
    LIST_OF_EVENTS_SITE,
    CAGEMATCH_SITE,
    Event,
    NAME_PREFIX,
    DATE_PREFIX,
    Match,
)


def _parse_table(soup: BeautifulSoup) -> List[str]:
    table = soup.find_all("table")[0]
    data = [
        [
            td.a["href"] if td.find("a") else "".join(td.stripped_strings)
            for td in row.find_all("td")
        ]
        for row in table.find_all("tr")
    ]
    # third column contains desired event link, first row is for navigation links and therefore excluded
    return [row[3] for row in data[1:]]


def _grab_event_links(driver: webdriver.Chrome) -> List[str]:
    paging_id = 0
    event_links = []
    while True:
        driver.get(LIST_OF_EVENTS_SITE.format(paging_id=paging_id))
        soup = BeautifulSoup(driver.page_source, "lxml")
        found_links = _parse_table(soup)
        if not found_links:
            break
        event_links.extend(found_links)
        paging_id += 100
    return event_links


def _parse_match(match: bs4.element.Tag) -> Match:
    pass


def _parse_event(driver: webdriver.Chrome, event_link: str) -> Optional[Event]:
    name, date = None, None

    driver.get(CAGEMATCH_SITE + event_link)
    soup = BeautifulSoup(driver.page_source)
    info_box = soup.find_all("div", {"class": "InformationBoxRow"})
    for item in info_box:
        tag_text = item.text.strip()
        if tag_text.startswith(NAME_PREFIX):
            name = tag_text[len(NAME_PREFIX) :]
        if tag_text.startswith(DATE_PREFIX):
            date = datetime.datetime.strptime(tag_text[len(DATE_PREFIX) :], "%d.%m.%Y")

    if not name or not date or date > datetime.datetime.today():
        return None

    matches = [
        _parse_match(match) for match in soup.find_all("div", {"class": "Match"})
    ]

    return Event(name, date, matches)


def parse_events(driver: webdriver.Chrome) -> List[Event]:
    links = _grab_event_links(driver)[20:]
    events = []
    for link in links:
        parsed_event = _parse_event(driver, link)
        if parsed_event is not None:
            events.append(parsed_event)
    return events


parse_events(webdriver.Chrome("C:/chromedriver/chromedriver.exe"))
