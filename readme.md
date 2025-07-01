<div align="center">

# NSW Fuel Price Checker

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
**Tracker for fuel prices in NSW, supports lookup based on time, fuel station and fuel types and price prediction**
<!-- prettier-ignore-end -->

</div>

## Usage

Docker Compose:
```shell
# Clone from Github
git clone https://github.com/WizardJR/nsw_fuel_price_checker.git

# Please add your own environment variables to all .env files and /frontend/nginx.conf

cd ./nsw_fuel_price_checker

docker compose up --build
```

Dev server:
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

Configurations for api fetcher and database can be found in /database/configs_template.json
  Need to insert your own credentials and rename it to configs.json
```


```shell
# Please add your own environment variables to .env in /backend/backend/.env

# Start backend server
python ./backend/manage.py runserver

```

```shell
# Please add your own environment variables to .env in /frontend/.env

cd ./frontend

npm install

# Start frontend server
npm run dev

```

## Feedback

Please feel free to submit issues if you encounter bugs.
