from flask_babel import gettext as _

import os
import world_bank_data as wb
from world_bank_data.search import pd

# from result_types._base import LegacyResult, Result
from searx.plugins import Plugin, PluginInfo
from searx.result_types import Answer
from countryinfo import CountryInfo


class GraphAnswer(Answer, kw_only=True):
    template = "answer/countries_data-graph.html"
    country: str
    metric: str
    y_axis: list
    x_axis: list


class CountriesDataPlugin(Plugin):
    id = "countries_data"
    ECON_TOPIC = 3
    POPULATION_SERIES_NAME = "SP.POP.TOTL"
    LEVEL_COUNTRY = "Country"
    GDP_ECON_TARGET_NAME = "GDP (current US$)"
    GDP_PER_CAPITA_ECON_TARGET_NAME = "GDP per capita (current US$)"
    GDP_PER_CAPITA_PPP_ECON_TARGET_NAME = (
        "GDP per capita, PPP (current international $)"
    )

    def get_series_filtered(self, country_name: str, series: pd.Series, level: str):
        return series.xs(country_name, level=level)

    def get_gdp_of_country(self, country_name: str):
        return self.get_series_filtered(
            country_name, self.gdp_series, level=self.LEVEL_COUNTRY
        )

    def get_gdp_per_capita_of_country(self, country_name: str):
        return self.get_series_filtered(
            country_name, self.gdp_per_capita_series, level=self.LEVEL_COUNTRY
        )

    def get_gdp_per_capita_ppp_of_country(self, country_name: str):
        return self.get_series_filtered(
            country_name, self.gdp_per_capita_ppp_series, level=self.LEVEL_COUNTRY
        )

    def get_population_of_country(self, country_name: str):
        return self.get_series_filtered(
            country_name, self.population_series, level=self.LEVEL_COUNTRY
        )

    def initiate_sources(self):
        """get GDP and such from WB data frames"""
        econ_indicators = wb.get_indicators(topic=self.ECON_TOPIC)
        econ_indicators = econ_indicators[
            econ_indicators["source"].str.contains("World Development Indicators")
        ]
        self.gdp_series = wb.get_series(
            econ_indicators[econ_indicators["name"] == self.GDP_ECON_TARGET_NAME].index[
                0
            ]
        )
        self.gdp_per_capita_series = wb.get_series(
            econ_indicators[
                econ_indicators["name"] == self.GDP_PER_CAPITA_ECON_TARGET_NAME
            ].index[0]
        )
        self.gdp_per_capita_ppp_series = wb.get_series(
            econ_indicators[
                econ_indicators["name"] == self.GDP_PER_CAPITA_PPP_ECON_TARGET_NAME
            ].index[0]
        )
        self.population_series = wb.get_series(self.POPULATION_SERIES_NAME)

    def __init__(self, plg_cfg) -> None:
        super().__init__(plg_cfg)
        self.info = PluginInfo(
            id=self.id,
            name=_("Country Data"),
            description=_(
                "Plugin that aims to do what google used to do when you'd search for stuff like a country's GDP"
            ),
        )
        self.topics = wb.get_topics()
        self.regions = wb.get_regions()
        self.countries = wb.get_countries()
        self.initiate_sources()
        # csv obtained from https://github.com/evpu/Bordering-Countries/blob/master/neighbors.csv
        self.countries_neighbours = pd.read_csv(
            os.path.dirname(__file__) + "/country_neighbors.csv"
        )
        self.income_levels = wb.get_incomelevels()
        self.keywordsaaa = [
            "gdp per capita",
            "population",
            "gdp",
            "pop",
            "code",
            "tld",
            "areatimezones",
        ]

    def my_function(self):
        import inspect

        # Iterate through the frames in the stack
        stack = inspect.stack()
        for frame_info in stack:
            print(f"File: {frame_info.filename}")
            print(f"Line: {frame_info.lineno}")
            print(f"Function: {frame_info.function}")
            print("---")

    def post_search(self, request, search):
        country_list = search.search_query.query.lower()
        for keyword in self.keywordsaaa:
            country_list = country_list.replace(keyword, "")
        country_list = country_list.split(" ")
        country: None | CountryInfo = None
        if len(country_list) == 1:
            try:
                country = CountryInfo(country_list[0].strip())
            except Exception:
                pass
        else:
            for w in country_list:
                try:
                    print(w)
                    country = CountryInfo(w.strip())
                    break
                except Exception:
                    pass
        words_searched = search.search_query.query.lower()
        for w in country_list:
            words_searched.replace(w, "")
        words_searched = words_searched.split(" ")
        results = []
        if country is None:
            return results
        if "gdp" in words_searched:
            if "per" in words_searched and "capita" in words_searched:
                series = (
                    self.get_gdp_per_capita_of_country(country.name()).tail(26).head(25)
                )
                results.append(
                    GraphAnswer(
                        answer="gdp_per_capita",
                        country=country.name(),
                        y_axis=(series / 1_000).values.tolist(),
                        x_axis=series.index.get_level_values("Year").tolist(),
                        metric="{} GDP Per Capita (US k$)".format(country.name()),
                    )
                )
            else:
                series = self.get_gdp_of_country(country.name()).tail(26).head(25)
                results.append(
                    GraphAnswer(
                        answer="gdp",
                        country=country.name(),
                        y_axis=(series / 1_000_000).values.tolist(),
                        x_axis=series.index.get_level_values("Year").tolist(),
                        metric="{} GDP (US millions $)".format(country.name()),
                    )
                )
        if "population" in words_searched:
            series = self.get_population_of_country(country.name()).tail(26).head(25)
            results.append(
                GraphAnswer(
                    answer="population",
                    country=country.name(),
                    y_axis=(series).values.tolist(),
                    x_axis=series.index.get_level_values("Year").tolist(),
                    metric="{} Population".format(country.name()),
                )
            )
        if len(results) == 0:
            return None
        return results
