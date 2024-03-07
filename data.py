import pandas as pd
import os
import plotly.express as px
import numpy as np


class DfWorker:
    def __init__(self, data):
        self.df = pd.DataFrame(data)

    def dropna_inf(self):
        self.df = self.df[~self.df["price per square foot"].isin([float("inf"), -float("inf")])]
        self.df.dropna(subset=["price per square foot"], inplace=True)

    def remove_outliers(self):
        pp = self.df["price per square foot"]
        z_scores = np.abs((pp - pp.mean()) / pp.std())
        self.df["z-score"] = z_scores
        self.df = self.df[z_scores <= 2]

    def sort_ascending(self, by):
        ascending = self.df
        ascending.dropna(subset=["carouselPhotos"], inplace=True)
        ascending = ascending.sort_values(by=by, ascending=True)
        return ascending.to_json(orient='records')

    def sort_descending(self, by):
        descending = self.df.sort_values(by=by, ascending=False)
        return descending.to_json(orient='records')

    def heatmap(self):
        viewport_width_js = """
        Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0)
        """
        geographical_heat_map = px.scatter_mapbox(self.df, lat="latitude", lon="longitude",
                                                  size="price per square foot",
                                                  color="price per square foot", mapbox_style='open-street-map',
                                                  center={'lat': self.df["latitude"].mean(),
                                                          'lon': self.df["longitude"].mean()})
        geographical_heat_map.update_layout(paper_bgcolor="#4a5259", font=dict(color="white"),
                                            height=800,
                                            mapbox=dict(
                                                accesstoken=os.environ.get("MAPBOX_KEY"))
                                            )

        return geographical_heat_map

    def scatter(self):
        sqrft_vs_price_scatter = px.scatter(self.df, x="square-footage", y="price", size="price per square foot",
                                            color="price per square foot")
        sqrft_vs_price_scatter.update_layout(font=dict(color="white"),
                                             xaxis=dict(
                                                 type="log"
                                             ),
                                             yaxis=dict(
                                                 type="log",
                                             ),
                                             height=800,
                                             paper_bgcolor="#4a5259",
                                             xaxis_title="square footage", yaxis_title="price",
                                             xaxis_title_font_color='white',
                                             yaxis_title_font_color='white')
        return sqrft_vs_price_scatter
