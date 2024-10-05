import json
from typing import Dict, List
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright, BrowserContext, TimeoutError
from bs4 import BeautifulSoup
import pandas as pd

load_dotenv()


def save_cookies(
    context: BrowserContext,
    url: str,
    username: str,
    password: str,
    cookie_file: str,
) -> List[Dict]:
    page = context.new_page()
    page.goto(url)

    # Cookies modal
    try:
        page.wait_for_selector("[aria-label='Cookie banner']", timeout=5000)
        page.get_by_role("button", name="Accept All Cookies").click()
    except TimeoutError:
        print("No cookie banner. Continuing...")

    # Log in
    page.get_by_placeholder("Ej.: nombre@empresa.com").fill(username)
    page.get_by_placeholder("*****").fill(password)
    page.get_by_role("button", name="Entrar").click()

    # Save cookies
    cookies = page.context.cookies()
    with open(cookie_file, "w") as f:
        json.dump(cookies, f)

    print(f"Cookies saved to {cookie_file}")

    page.close()
    return cookies


def load_cookies(cookie_file: str) -> List[Dict]:
    try:
        with open(cookie_file, "r") as f:
            cookies = json.load(f)
        print(f"Cookies loaded from {cookie_file}")
        return cookies
    except FileNotFoundError:
        print(f"No cookies file found at {cookie_file}")
        return None


def validate_cookies(context: BrowserContext, url) -> bool:
    is_session_valid = None

    page = context.new_page()
    page.goto(url)

    # Check if we're inside the session
    if page.get_by_text("Mi próxima cita").count() > 0:
        print("Session is valid.")
        is_session_valid = True
    else:
        print("Session is expired.")
        is_session_valid = False

    page.close()
    return is_session_valid


def scrape_with_session(context: BrowserContext, url: str):
    page = context.new_page()
    page.goto(url)

    # Navigate to tests page and click on "Understood" button
    page.get_by_text("Ver pruebas e informes").click()
    try:
        page.wait_for_selector("#ModalDisclaimer", timeout=10000)
        page.get_by_role("button", name="Entendido").click()
    except TimeoutError:
        print("No modal to click. Continuing...")

    # Create DataFrame
    columns = [
        "Description",
        "Date",
        "Document_link",
        "Hospital",
        "Specialty",
        "Type",
        "Test",
        "Doctor",
    ]
    df = pd.DataFrame(columns=columns)

    # Identify "Next page" button
    page.wait_for_selector(".pei-listado-pruebas-contenedor")
    next_page = page.locator(".siguiente")

    # Begin scraping
    while True:
        more_details = page.locator(".verDetalle")
        more_details_count = more_details.count()
        for i in range(more_details_count):
            more_details.nth(i).click()

        content = page.content()
        soup = BeautifulSoup(content, "lxml")
        table = soup.find("ul", class_="tableContent")
        rows = table.find_all("li", class_="tableContentInfo")
        for row in rows:
            document_link_tag = row.find("a", href=lambda x: x and "informePDF" in x)
            document_link = f"https://www.quironsalud.com{document_link_tag["href"]}"

            cells_tags = row.find_all("span", class_=lambda x: x is None)
            cells_data = [cell.text for cell in cells_tags]
            cells_data[2] = document_link
            cells = dict(zip(columns, cells_data))

            df = pd.concat([df, pd.DataFrame([cells])])

        next_page = page.locator(".siguiente")
        if "activePaso" not in next_page.get_attribute("class"):
            break
        next_page.click()

    # Save CSV
    df.to_csv("output.csv", index=False)
    print("Saved info to CSV file.")
    page.close()


def main():
    # User credentials
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    url = os.getenv("URL")

    # Session cookies
    cookie_file = "cookies.json"
    cookies = load_cookies(cookie_file)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context("user_data_dir", headless=False)

        # Check for cookies
        if cookies is None:
            print("Saving cookies...")
            cookies = save_cookies(context, url, username, password, cookie_file)
        else:
            print("Using loaded cookies for scraping.")
            context.add_cookies(cookies)

        # Validate the loaded cookies
        if not validate_cookies(context, url):
            print("Session is expired. Logging in again...")
            cookies = save_cookies(context, url, username, password, cookie_file)

        # Scrape the page
        scrape_with_session(context, url)


main()
