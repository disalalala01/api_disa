# amp-production-cost

Api расчета себестоимости продукций АМП
АМП и АМД.xlsx -> Для СС АМП

- Запрос для АМП.xlsx -> https://swagger.com/amp-production-cost?date_start=2021-10&date_end=2021-12

Пример:
 ```
params = {
    "date_start": "2021-10",
    "date_end": "2021-12",
}
url = 'https://swagger.com/amp-production-cost'
resp = requests.get(url, params=params, verify=False).json()
df = pd.read_json(resp['amp-production-cost'])
```

# TEST
```
pip install pytest
pytest tests.py
```

# RUN

```
gunicorn  --bind 0.0.0.0:5000 --log-level info manage:app
```
