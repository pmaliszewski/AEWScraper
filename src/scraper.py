import datetime
import re
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup, element
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
from utils import be_gentle


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
        be_gentle()
        driver.get(LIST_OF_EVENTS_SITE.format(paging_id=paging_id))
        soup = BeautifulSoup(driver.page_source, "lxml")
        found_links = _parse_table(soup)
        if not found_links:
            break
        event_links.extend(found_links)
        paging_id += 100
    return event_links


def _clean_up_side(side: str) -> List[str]:
    output = []

    # sanity check
    side = side.rstrip()

    # split multiple wrestlers
    if any(character in side for character in ",&"):
        side = re.split(r"[,&]", side)

    if " and " in side:
        side = side.split(" and ")

    # remove tag team names
    if isinstance(side, list):
        accumulator = []
        for item in side:
            if "(" in item:
                accumulator.append(item[item.find("(") + 1 :].lstrip().rstrip())
            elif ")" in item:
                accumulator.append(item[: item.find(")")].lstrip().rstrip())
            else:
                accumulator.append(item.lstrip().rstrip())
        output.extend(accumulator)

    if isinstance(side, str):
        output = [side]

    return output


def _find_id(name: str, links: List[element.Tag]) -> Optional[int]:
    for link in links:
        if link.text == name:
            href = link["href"]
            nr_mark = "nr="
            name_mark = "&name="
            return int(href[href.find(nr_mark) + len(nr_mark) : href.find(name_mark)])
    return None


def _parse_result(
    result: element.Tag,
) -> Tuple[List[Participant], List[Participant], bool]:
    result_text = result.text
    winning_side, losing_side = [], []
    draw = False

    # remove managers
    result_text = re.sub(r"\(w/.*?\)", "", result_text)

    # remove time
    result_text = re.sub(r"\([0-9]*:[0-9]*\)", "", result_text)

    # remove title change and champion annotation
    result_text = result_text.replace(" - TITLE CHANGE !!!", "")
    result_text = result_text.replace("(c)", "")

    result_text = result_text.rstrip()

    if " defeats " in result_text:
        result_text = result_text.split(" defeats ")
    elif " defeat " in result_text:
        result_text = result_text.split(" defeat ")
    elif " vs. " in result_text:
        result_text = result_text.split(" vs. ")
        draw = True
    else:
        raise UnknownMatchError()

    all_links = [link for link in result.find_all("a") if link.has_attr("href")]

    for i in range(2):
        side = _clean_up_side(result_text[i])
        for wrestler_name in side:
            wrestler_id = _find_id(wrestler_name, all_links)
            wrestler = Participant(name=wrestler_name, participant_id=wrestler_id)
            if i == 0:
                winning_side.append(wrestler)
            else:
                losing_side.append(wrestler)

    return winning_side, losing_side, draw


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

    return Match(
        stipulation=stipulation,
        winning_side=parsed_result[0],
        losing_side=parsed_result[1],
        draw=parsed_result[2],
    )


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
    links = _grab_event_links(driver)
    events = []
    for link in links:
        be_gentle()
        parsed_event = _parse_event(driver, link)
        if parsed_event is not None:
            events.append(parsed_event)
    return events


# parse_events(webdriver.Chrome("C:/chromedriver/chromedriver.exe"))
