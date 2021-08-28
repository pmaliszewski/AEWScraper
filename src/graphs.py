from pathlib import Path

import plotly.express as px

from analyzer import analyze

df = analyze(Path("C:/Users/Paweł/Desktop/dumps"), to_save=Path("C:/Users/Paweł/Desktop"))
df = df.sort_values(df.last_valid_index(), axis=1, ascending=False)
df = df.iloc[:,:20]

fig = px.line(df)
fig.show()
