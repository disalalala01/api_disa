import pandas as pd
from production_cost import Base, session_db
import sqlalchemy as db
from sqlalchemy.exc import OperationalError
import calendar
from datetime import datetime, timedelta


def get_date_list(date_start, date_end):
    date_start = datetime.strptime(date_start, "%Y-%m-%d")
    date_end = datetime.strptime(date_end, "%Y-%m-%d")
    dates = pd.date_range(date_start, date_end - timedelta(days=1), freq="d")
    dates = dict(
        (k + "-" + str(get_last_day_of_month(k)) + " 00:00:00", None)
        for k in dates.strftime("%Y-%m").tolist()
    )
    return dates


def get_last_day_of_month(date: str):
    year, month = list(map(lambda x: int(x), date.split("-")))
    last_day_of_month = calendar.monthrange(year, month)[1]
    return str(last_day_of_month)


def add_time(date: str):
    last_day = get_last_day_of_month(date)
    return date + "-" + last_day + " 00:00:00"


class GrossProfit(Base):
    __tablename__ = "gross_profit"
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer)
    mapping_id = db.Column(db.Integer)
    date_start = db.Column(db.TIMESTAMP)
    date_end = db.Column(db.TIMESTAMP)
    unit_report_quantity = db.Column(db.Float)
    sales_value = db.Column(db.Float)

    @classmethod
    def get(cls, date_start, date_end):
        result = {}
        try:
            if date_start == "":
                raise Exception("date_start required")
            if date_end == "":
                raise Exception("date_end required")
            try:
                datetime.strptime(date_start, "%Y-%m")
            except ValueError:
                raise Exception(f"date format must be YYYY-MM not {date_start}")
            try:
                datetime.strptime(date_end, "%Y-%m")
            except ValueError:
                raise Exception(f"date format must be YYYY-MM not {date_end}")
            check_start = date_start.split("-")[-1]
            check_end = date_end.split("-")[-1]
            if len(check_end) != 2:
                raise Exception(
                    f"date format must be YYYY-MM not {date_end} , Example : 2021-05"
                )
            if len(check_start) != 2:
                raise Exception(
                    f"date format must be YYYY-MM not {date_start} , Example : 2021-05"
                )
            statement = f"""
             select to_char(gp.date_end, 'YYYY-MM'), n.production_name, n.articul, gp.unit_report_quantity ,
             gp.sales_value, ecg.price_meat, ecg.price_spices, ecg.price_packaging, ecg.price_accrued from gross_profit gp
             inner join expanded_cost_gp ecg on ecg.mapping_id = gp.mapping_id and ecg.source_id = gp.source_id and ecg.date_end = gp.date_end
             inner join mapping m on m.id = gp.mapping_id
             inner join nomenclature n on n.id = m.nomenclature_id
             where to_char(gp.date_end, 'YYYY-MM')>='{date_start}' and to_char(gp.date_end, 'YYYY-MM')<='{date_end}'
             order by to_char(gp.date_end, 'YYYY-MM') asc
            """

            q = session_db.execute(statement).all()

            # test data
            # q = [['2021-11', 'name', 'articul', 60, 70, 80, 90, 100, 110]]
            if not bool(q):
                raise Exception("Empty gross_profit")
            date_obj = get_date_list(
                date_start=date_start + "-" + "1",
                date_end=date_end + "-" + get_last_day_of_month(date_end),
            )
            data = []
            for obj in q:
                date = add_time(obj[0])
                result_obj = {}
                name = obj[1]
                articul = obj[2]
                unit_report_quantity = obj[3]
                sales_value = obj[4]
                price_meat = obj[5]
                price_spices = obj[6]
                price_packaging = obj[7]
                price_accrued = obj[8]
                cost = price_accrued * unit_report_quantity
                raw = price_spices + price_meat + price_packaging
                for key, value in date_obj.items():
                    if key == date:
                        result_obj[(str(date), "Объем")] = unit_report_quantity
                        result_obj[(str(date), "Выручка")] = sales_value
                        result_obj[(str(date), "Произв с/с с аморт")] = raw + cost
                        result_obj[(str(date), "Сырьевая с/с")] = raw
                        result_obj[(str(date), "С/с мясо")] = (
                            price_meat * unit_report_quantity
                        )
                        result_obj[(str(date), "С/с специи")] = (
                            price_spices * unit_report_quantity
                        )
                        result_obj[(str(date), "С/с упаковка")] = (
                            price_packaging * unit_report_quantity
                        )
                    else:
                        result_obj[(str(key), "Объем")] = None
                        result_obj[(str(key), "Выручка")] = None
                        result_obj[(str(key), "Произв с/с с аморт")] = None
                        result_obj[(str(key), "Сырьевая с/с")] = None
                        result_obj[(str(key), "С/с мясо")] = None
                        result_obj[(str(key), "С/с специи")] = None
                        result_obj[(str(key), "С/с упаковка")] = None

                result_obj[("Артикул", "")] = articul
                result_obj[("Наименование", "")] = name

                data.append(result_obj)
            df = pd.json_normalize(data)
            result["amp-production-cost"] = df.to_json(
                orient="records", force_ascii=False
            )
            return result
        except OperationalError:
            session_db.rollback()
            return cls.get(date_start=date_start, date_end=date_end)
        except Exception:
            session_db.rollback()
            raise
