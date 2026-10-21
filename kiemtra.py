import pandas as pd
import numpy as np

df = pd.read_csv("abc-2.csv", header=None)

print(df.head(10).to_string(index=False, header=False))

