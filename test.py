import dash
import dash_core_components as dcc
import dash_html_components as html
from matplotlib import colors as mcolors
import plotly.graph_objs as go
import pandas as pd
import numpy as np
pv = pd.pivot_table(df, index=['Name'], columns=["Status"], values=['Quantity'], aggfunc=sum, fill_value=0)
df_candidat = pd.read_csv("../data/donnee_propre.csv", sep = ';', dtype = str)
#print(list(df_candidat.columns))
parti_du_candidat = {}
colonnes = list(df_candidat.columns)
for index, row in df_candidat.iterrows():
    for colonne in colonnes:
        if 'Mod.' in colonne and not row[colonne] == "—":
            parti_du_candidat[row.candidat] = colonne[:-5]
df_candidat['parti'] = df_candidat['candidat'].map(parti_du_candidat)

def voix_interne_non_modifiee(row):
    parti = row.parti
    return row[parti + " Mod."]
def voix_interne_modifiee(row):
    parti = row.parti
    return row[parti + " Comp."]

df_candidat["voix_interne_non_modifiee"] = df_candidat.apply(voix_interne_non_modifiee, axis=1)
df_candidat["voix_interne_modifiee"] = df_candidat.apply(voix_interne_modifiee, axis=1)


print(df_candidat.dtypes)

partis = np.unique(list(parti_du_candidat.values()))
for parti in partis:
    voix_du_candidat = {}
    for index, row in df_candidat.iterrows():
        if row.parti == parti:
            nb_voix = int(row[parti + " Mod."].replace("'","")) +  int(row[parti + " Comp."].replace("'",""))
        else:
            nb_voix = int(row[parti + " Comp."].replace("'",""))
        voix_du_candidat[row.candidat] = nb_voix
    df_candidat[parti] = df_candidat['candidat'].map(voix_du_candidat)

sans_denom = 'Sans dénomination '
voix_du_candidat = {}
for index, row in df_candidat.iterrows():
    nb_voix = int(row[sans_denom].replace("'",""))
    voix_du_candidat[row.candidat] = nb_voix
df_candidat[sans_denom] = df_candidat['candidat'].map(voix_du_candidat)
df_candidat.to_csv('avec_parti.csv')
parti_indexes = []  # indices correspond to labels, eg A1, A2, A1, B1, ...
candidat_indexes = []
nb_voix_indexes = []
candidats = list(df_candidat['candidat'])
partis = list(partis)
partis.append(sans_denom)
nb_partis = len(partis)
for index_parti, parti in enumerate(partis):
    for candidat_index, candidat in enumerate(candidats):
        candidat_indexes.append(candidat_index + nb_partis)
        parti_indexes.append(index_parti)
        nb_voix = df_candidat[df_candidat['candidat'] == candidat][parti].values[0]
        nb_voix_indexes.append(nb_voix)



nb_candidats = len(candidats)
partis_color = ['grey','blue', 'grey', 'grey', "red", 'grey', 'pink', 'red', 'green', 'teal', 'black']
couleur_du_parti = {couleur:parti for couleur, parti in zip(partis, partis_color)}
print(couleur_du_parti)
candidats_color = [couleur_du_parti[parti_du_candidat[candidat]] for candidat in candidats]
app = dash.Dash()
line_color = np.array(partis_color)[parti_indexes]
light_line_color = [mcolors.to_rgba(color) for color in line_color]
light_line_color = [f'rgba({color[0]}, {color[1]}, {color[2]}, 0.35)' for color in light_line_color]
print(light_line_color)
fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = partis + candidats,
      color = partis_color + candidats_color
    ),
    link = dict(
      source = parti_indexes, # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = candidat_indexes,
      value = nb_voix_indexes,
      color = light_line_color
  ))])

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
fig.show()
