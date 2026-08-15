import pandas as pd
import numpy as np

np.random.seed(42)

N = 5000

data = []

for i in range(N):

    consumer_id = f"C{i+1:04d}"

    voltage = np.random.normal(230, 8)

    current = np.random.uniform(1, 25)

    power_factor = np.random.uniform(0.75, 0.99)

    previous_consumption = np.random.uniform(2, 30)

    consumption = previous_consumption * np.random.uniform(0.7, 1.3)

    tamper = np.random.choice([0, 1], p=[0.92, 0.08])

    # Normal consumption
    theft = 0

    # Create suspicious patterns
    if tamper == 1:

        theft = 1

        consumption *= np.random.uniform(0.25, 0.60)

        current *= np.random.uniform(0.8, 1.3)

        power_factor = np.random.uniform(0.40, 0.75)

    else:

        # Some abnormal cases without explicit tampering
        if consumption < previous_consumption * 0.5:
            theft = np.random.choice([0, 1], p=[0.6, 0.4])

    deviation = (
        consumption - previous_consumption
    ) / (previous_consumption + 0.001)

    data.append([
        consumer_id,
        voltage,
        current,
        power_factor,
        previous_consumption,
        consumption,
        tamper,
        deviation,
        theft
    ])


columns = [
    "consumer_id",
    "voltage",
    "current",
    "power_factor",
    "previous_consumption",
    "consumption",
    "tamper",
    "deviation",
    "theft"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv("smart_meter_data.csv", index=False)

print("Dataset generated successfully!")
print(df.head())
print("\nDataset shape:", df.shape)
print("\nClass distribution:")
print(df["theft"].value_counts()) 