# ⚽️ Predicting Football Matches

## 📋 Overview

This project focuses on predicting football match outcomes using machine learning, specifically a **Random Forest Classifier** from **scikit-learn**. It involves scraping historical match data using **BeautifulSoup**, transforming the data for modeling, and building a predictive model to forecast match results.

The process starts with the `extract.py` script, which scrapes match statistics from the **fbref** website for the last two seasons. The script handles rate limits using `time.sleep` to avoid getting blocked. The extracted data is saved into a CSV file (`matches.csv`). In the next phase, the data is preprocessed and used to train the **Random Forest** model in the `predictions.ipynb` notebook. This includes converting categorical variables into numeric values and adding rolling averages for key statistics to improve the model’s predictive power.

The model is evaluated using common metrics like **Accuracy** and **Precision** to assess its performance, with predictions compared to actual match outcomes. The goal is to build a robust model that can accurately predict football match results based on historical data.


## 🔍 Project Structure

- `extract.py`: Script to srape data from the last two seasons and save it as a csv file.
- `matches.csv`: An example csv file of scraped data
- `predictions.ipynb`: A notebook that transforms the data, trains the model, and uses result metrics
- `requirements.txt`: Dependencies that the scripts need to run
- `test_extract.py`: Tests for the extraction/scraping logic

## 🛠️ Prerequisites
- **Python** installed (For running locally)

## ⚙️ Setup and Running Locally (MacOS)

1. Creating and activating virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2. Install requirements
    ```bash
    pip install -r requirements.txt
    ```
3. Extracting and saving the most current match results (**Optional**):
    
    _This may take a while as the program needs to sleep between requests to not exceed the rate limit of fbref.com._
    ```bash
    python3 extract.py
    ```
4. Transforming the data and training the model:

    Go through the `predictions.ipynb` notebook.
