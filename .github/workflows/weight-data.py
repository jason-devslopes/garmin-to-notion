from datetime import date, timedelta

from dotenv import load_dotenv

from src.helpers import get_garmin_client, get_notion_client


def get_weight_data(garmin):
    target_date = date.today() - timedelta(days=1)
    data = garmin.get_body_composition(target_date.isoformat())
    return target_date.isoformat(), data


def weight_exists(client, database_id, weight_date):
    query = client.databases.query(
        database_id=database_id,
        filter={
            "property": "Date",
            "date": {"equals": weight_date}
        }
    )
    results = query["results"]
    return results[0] if results else None


def create_weight_record(client, database_id, weight_date, data):
    # 🔍 DEBUG: print Garmin response so we can verify fields if needed
    print("Garmin weight data:", data)

    properties = {
        "Date": {"date": {"start": weight_date}},
        "Source": {"rich_text": [{"text": {"content": "Garmin"}}]},
    }

    # These fields may vary depending on Garmin account/device
    if data.get("weight"):
        properties["Weight"] = {"number": data.get("weight")}

    if data.get("bmi"):
        properties["BMI"] = {"number": data.get("bmi")}

    if data.get("bodyFat"):
        properties["Body Fat %"] = {"number": data.get("bodyFat")}

    if data.get("muscleMass"):
        properties["Muscle Mass"] = {"number": data.get("muscleMass")}

    client.pages.create(
        parent={"database_id": database_id},
        properties=properties,
    )


def main():
    load_dotenv()

    garmin_client, _ = get_garmin_client()
    notion_client, notion_dbs = get_notion_client()

    database_id = notion_dbs.weight

    weight_date, weight_data = get_weight_data(garmin_client)

    if not weight_data:
        print(f"No weight data found for {weight_date}")
        return

    existing = weight_exists(notion_client, database_id, weight_date)

    if existing:
        print(f"Weight already exists for {weight_date}")
    else:
        create_weight_record(notion_client, database_id, weight_date, weight_data)
        print(f"Created weight record for {weight_date}")


if __name__ == "__main__":
    main()
