import datetime
from itertools import product
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup, SoupStrainer, element
from selenium import webdriver

from constants import (
    LIST_OF_EVENTS_SITE,
    CAGEMATCH_SITE,
    Event,
    NAME_PREFIX,
    DATE_PREFIX,
    Match,
    UnknownMatchError,
    Participant,
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


def _parse_result(
    result: element.Tag,
) -> Tuple[List[Participant], List[Participant], bool]:
    # TODO: some fuckery required
    result_text = result.text
    winning_side, losing_side = [], []
    draw = False
    if " defeats " in result_text:
        result_text = result_text.split(" defeats ")
    elif " defeat " in result_text:
        result_text = result_text.split(" defeat ")
    elif " vs. " in result_text:
        result_text = result_text.split(" vs. ")
        draw = True
    else:
        raise UnknownMatchError()

    all_links = [
        link
        for link in BeautifulSoup(result, parse_only=SoupStrainer("a"))
        if link.has_attr("href")
    ]

    for i in range(2):
        side = result_text[i]
        pass


def _parse_match(match: element.Tag) -> Match:
    stipulation = match.find("div", {"class": "MatchType"}).text
    result = match.find("div", {"class": "MatchResults"})
    try:
        parsed_result = _parse_result(result)
    except UnknownMatchError:
        return Match(
            stipulation=f"Error during parsing: {result.text}",
            winning_side=None,
            losing_side=None,
        )

    print(result)


def _parse_event(driver: webdriver.Chrome, event_link: str) -> Optional[Event]:
    title, date = None, None

    driver.get(CAGEMATCH_SITE + event_link)
    soup = BeautifulSoup(driver.page_source)
    info_box = soup.find_all("div", {"class": "InformationBoxRow"})
    for item in info_box:
        tag_text = item.text.strip()
        if tag_text.startswith(NAME_PREFIX):
            title = tag_text[len(NAME_PREFIX) :]
        if tag_text.startswith(DATE_PREFIX):
            date = datetime.datetime.strptime(tag_text[len(DATE_PREFIX) :], "%d.%m.%Y")

    if not title or not date or date > datetime.datetime.today():
        return None

    matches = [
        _parse_match(match) for match in soup.find_all("div", {"class": "Match"})
    ]

    return Event(title=title, date=date, matches=matches)


def parse_events(driver: webdriver.Chrome) -> List[Event]:
    links = _grab_event_links(driver)[20:]
    events = []
    for link in links:
        parsed_event = _parse_event(driver, link)
        if parsed_event is not None:
            events.append(parsed_event)
    return events


parse_events(webdriver.Chrome("C:/chromedriver/chromedriver.exe"))