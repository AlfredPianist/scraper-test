# Medical Test Scraper

This project is a web scraper designed to collect and export all medical tests issued by doctors into a CSV file.

## Features

- Scrapes medical test data from specified sources.
- Stores cookies and reuses them in case the session expires.
- Outputs data to a CSV file for easy access and analysis.

## Prerequisites

Make sure you have the following installed on your system:

- Python (3.7 or higher)
- Poetry

## Getting Started

Follow these steps to set up and run the scraper:

1. Clone the Repository

```bash
git clone https://github.com/AlfredPianist/scraper-test.git
cd scraper-test
```

2. Set Up Poetry

Start by entering the Poetry shell:

```bash
poetry shell
```

3. Install Playwright Dependencies

Run the following command to install Playwright's system dependencies:

```bash
playwright install-deps
```

4. Install Playwright Chromium Driver

Next, install the Chromium driver:

```bash
playwright install
```

5. Configure Environment Variables

Copy the example environment variables file and configure it:

```bash
cp .env.example .env
```

Open the .env file in your favorite text editor and fill in the necessary variables.

6. Run the Scraper

Finally, execute the script to start scraping:

```bash
poetry run python scrape.py
```

### Output

The scraper will generate a CSV file containing the scraped medical tests. You can find this file in the project directory.
