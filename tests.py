from production_cost import client
from production_cost.models import GrossProfit


def test_get():
    params = {"date_start": "2021-10", "date_end": "2021-12"}
    res = client.get("/api/margin/amp-production-cost", query_string=params)
    assert res.status_code == 200
    assert type(res.get_json()["amp-production-cost"]) == str
    assert res.get_json() == GrossProfit.get(**params)


def test_errors_data_required():
    params = {"date_start": "2021-10", "date_end": ""}
    res = client.get("/api/margin/amp-production-cost", query_string=params)
    assert res.status_code == 400
    assert res.get_json()["Success"] is False
    assert res.get_json()["Errors"] == "date_end required"


def test_errors_data_missing():
    params = {"date_start": "2021-10"}
    res = client.get("/api/margin/amp-production-cost", query_string=params)
    assert res.status_code == 400
    assert res.get_json()["Success"] is False
    assert (
        res.get_json()["Errors"]
        == "get() missing 1 required positional argument: 'date_end'"
    )


def test_errors_date_format():
    params = {"date_start": "2021-10", "date_end": "2021-12-11"}
    res = client.get("/api/margin/amp-production-cost", query_string=params)
    assert res.status_code == 400
    assert res.get_json()["Success"] is False
    assert res.get_json()["Errors"] == "date format must be YYYY-MM not 2021-12-11"


def test_errors_date_format_second():
    params = {"date_start": "2021-5", "date_end": "2021-12"}
    res = client.get("/api/margin/amp-production-cost", query_string=params)
    assert res.status_code == 400
    assert res.get_json()["Success"] is False
    assert (
        res.get_json()["Errors"]
        == "date format must be YYYY-MM not 2021-5 , Example : 2021-05"
    )
