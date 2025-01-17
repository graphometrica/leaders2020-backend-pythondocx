import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from docxtpl import DocxTemplate

template_file = (
    Path(__file__)
    .parent.parent.joinpath("templates")
    .joinpath("animal_card_template.docx")
)

month_names = [
    "Января",
    "Февраля",
    "Марта",
    "Апреля",
    "Мая",
    "Июня",
    "Июля",
    "Августа",
    "Сентября",
    "Октября",
    "Ноября",
    "Декабря",
]


def render_animal_card(data: Dict[str, Any]) -> DocxTemplate:
    doc = DocxTemplate(str(template_file.absolute()))
    doc.render(transform_data(data))
    return doc


def transform_data(dt: Dict[str, Any]) -> Dict[str, Any]:
    data = deepcopy(dt)
    now = datetime.now()
    data["date"] = dict(
        day=now.day, month=month_names[now.month + 1], year=now.year - 2000
    )
    data["dog"] = data["generalInfo"]["type"] == "собака"
    data["cat"] = data["generalInfo"]["type"] == "кошка"
    data["age"] = now.year - int(data["generalInfo"]["year"])
    if data["additionalInfo"]["sterilizationDate"] is None:
        data["sterializationM"] = "-"
        data["sterializationY"] = "-"
        data["sterializationD"] = "-"
    else:
        strlz_date = datetime.strptime(
            data["additionalInfo"]["sterilizationDate"], "%Y-%m-%d"
        )
        data["sterializationM"] = month_names[strlz_date.month - 1]
        data["sterializationY"] = strlz_date.year - 2000
        data["sterializationD"] = strlz_date.day

    if data["catchInfo"]["catchOrder"]["orderActDate"]:
        catchdt = datetime.strptime(
            data["catchInfo"]["catchOrder"]["orderActDate"], "%Y-%m-%d"
        )
        data["catchInfo"]["catchOrder"]["day"] = catchdt.day
        data["catchInfo"]["catchOrder"]["month"] = month_names[catchdt.month - 1]
        data["catchInfo"]["catchOrder"]["year"] = catchdt.year - 2000
    else:
        data["catchInfo"]["catchOrder"]["day"] = "-"
        data["catchInfo"]["catchOrder"]["month"] = "-"
        data["catchInfo"]["catchOrder"]["year"] = "-"

    if data["newOwner"]["type"] == "юридическое лицо":
        data["is_phys"] = False
    else:
        data["is_phys"] = True

    inc_date = datetime.strptime(data["animalMovements"][0]["date"], "%Y-%m-%d")
    data["in_date_day"] = inc_date.day
    data["in_date_month"] = month_names[inc_date.month + 1]
    data["in_date_year"] = inc_date.year - 2000

    if len(data["animalMovements"]) > 1:
        last_ = data["animalMovements"][-1]
        out_date = datetime.strptime(last_["date"], "%Y-%m-%d")
        data["out_date_day"] = out_date.day
        data["out_date_month"] = month_names[out_date.month + 1]
        data["out_date_year"] = out_date.year - 2000
        data["out_act"] = last_["documentNumber"]
        data["out_type"] = last_["additional"]
    else:
        data["out_date_day"] = ""
        data["out_date_month"] = ""
        data["out_date_year"] = ""
        data["out_act"] = ""
        data["out_type"] = ""

    data["endodata"] = []
    for i, v in enumerate(data["endoparasites"]):
        data["endodata"].append(
            {
                "id": i + 1,
                "date": v["date"],
                "pills": v["medicationName"],
                "amount": v["dose"],
            }
        )

    data["vacdata"] = []
    for i, v in enumerate(data["vaccinations"]):
        data["vacdata"].append(
            {
                "id": i + 1,
                "date": v["date"],
                "pills": v["medicationName"],
                "amount": v["serialNumber"],
            }
        )

    data["healthdata"] = []
    for i, v in enumerate(data["healthInfo"]):
        data["healthdata"].append(
            {
                "id": i + 1,
                "date": v["date"],
                "wight": "-",
                "pills": v["anamnesis"],
            }
        )



    return data


if __name__ == "__main__":
    data = Path(__file__).parent.parent.joinpath("examples").joinpath("example_data.json")
    render_animal_card(json.loads(data.read_text(encoding="utf8"))).save("rendered.docx")
