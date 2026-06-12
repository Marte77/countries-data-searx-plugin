# SPDX-License-Identifier: AGPL-3.0-or-later


import typing
from flask_babel import gettext as _
from result_types._base import LegacyResult, Result
from search import SearchWithPlugins
from searx.plugins import Plugin, PluginInfo
from searx.result_types import Answer
from countryinfo import CountryInfo, CountryNotFoundError

if typing.TYPE_CHECKING:
    from searx.plugins import PluginCfg
    from searx.search import SearchWithPlugins


class SXNGPlugin(Plugin):
    id = "countries-data"

    def __init__(self, plg_cfg) -> None:
        super().__init__(plg_cfg)
        self.info = PluginInfo(
            id=self.id,
            name=_("Country Data"),
            description=_(
                "Plugin that aims to do what google used to do when you'd search for stuff like a country's GDP"
            ),
        )
        self.keywords = [
            "gdp",
            "gdp per capita",
            "population",
            "pop",
            "code",
            "tld",
            "timezones",
        ]

    def post_search(self, request, search):
        words_searched = search.search_query.query.lower().split(" ")
        country_list = [word for word in words_searched if word not in self.keywords]
        country: None | CountryInfo = None
        if len(country_list) == 1:
            try:
                country = CountryInfo(country_list[0])
            except CountryNotFoundError:
                pass
        else:
            for w in country_list:
                try:
                    country = CountryInfo(w)
                except CountryNotFoundError:
                    pass
        results: list[Result | LegacyResult] = []
        if country is None:
            return results
        if "gdp" in words_searched:
            if "per" in words_searched and "capita" in words_searched:
                results.append(
                    Answer(answer="GET {} WITH GDP/CAPITA".format(country.tld()))
                )
            results.append(Answer(answer="GET {} WITH GDP".format(country.tld())))
        if "population" in words_searched:
            results.append(Answer(answer="GET {} POPULATION ".format(country.tld())))
        if len(results) == 0:
            return None
        return results
