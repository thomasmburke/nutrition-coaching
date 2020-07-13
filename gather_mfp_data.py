import myfitnesspal
import os

client = myfitnesspal.Client(
    os.getenv('MFP_USERNAME'), password=os.getenv('MFP_PASSWORD'))
day = client.get_date(2020, 7, 11)
print(day)
print("now for the meals...")
print(day.meals[1].entries)
