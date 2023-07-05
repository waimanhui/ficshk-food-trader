# Hong Kong Food Importer / Food Distributor list

The Centre for Food Safety from Hong Kong has a PDF for registered Food Importer / Food Distributor and a simple enquiry form. However, the enquiry form is not providing all information on PDF for searching. This repo is to extract infomration from PDF directly to CSV for easier searching.

To check and download the extracted CSV, please click [<kbd> <br> Download CSV File <br> </kbd>](data/registerTrader.csv)

Food Import Control System Official Site: [https://www.fics.gov.hk/home/landingPage/index.htm?locale=zh&locale=zh](https://www.fics.gov.hk/home/landingPage/index.htm?locale=zh&locale=zh)


Official Searching System: [https://www.fics.gov.hk/ie/tr/traderrecord/tray/index.htm](https://www.fics.gov.hk/ie/tr/traderrecord/tray/index.htm)


## Working Details

The workflow `download_traderpdf.yml` will run on 1st day of each month to download the latest PDF and save to `data/registerTrader.pdf`. Then the workflow will trigger `extract_text_from_pdf.yml` to extract text from PDF and create `data/registerTrader.csv`.

### Command to download latest PDF
```
curl -o test.pdf https://www.fics.gov.hk/ie/tr/traderrecord/report/download_register.htm
```

### Local run steps
Pre-requisite: [Python 3+](https://www.python.org/downloads/)

Download the lastest PDF and update the fole location in `scripts/.env` then run below
```
python3 -m venv venv
.\venv\scripts\activate
pip install -r requirements.txt
python extract_text.py
```

> **Note**: The code are for running on Windows, it may require some adjustments for running on Mac or Linux
