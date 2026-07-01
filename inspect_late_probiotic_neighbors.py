import pandas as pd

expected = pd.read_csv("data/FRXEGR568_metrics_reordered.csv")

for start, end in [(285, 310), (315, 335)]:
    print(f"\nEXPECTED ROWS {start}-{end}")
    print(
        expected[["name", "category_title"]]
        .iloc[start:end]
        .to_string()
    )
