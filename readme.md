<div align="center">

# NSW Fuel Price Checker

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
**Tracker for fuel prices in NSW, supports lookup based on time, fuel station and fuel types and price prediction**
<!-- prettier-ignore-end -->

</div>

## Usage



```shell
# Clone from Github
git clone https://github.com/WizardJR/nsw_fuel_price_tracker.git

# Create python venv
python -m venv venv

# Activate venv (Windows)
./venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```


```shell
cd database

# Start the database updater
python main.py

# Graph past data (optional)
python Visualizer.py

# Save filtered data to csv
python Searcher.py

# Basic LSTM price predictor
python predict.ipynb

Configurations for api fetcher and database can be found in /databasae/configs_template.json
  Need to insert your own credentials and rename it to configs.json
```


```shell
cd backend

# Start backend server
python manage.py runserver

```

## Feedback

Please feel free to submit issues if you encounter bugs.
