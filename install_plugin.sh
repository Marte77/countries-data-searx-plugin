#!/bin/bash

PLUGIN_PY="countries_data.py"
CSV_HELPER="country_neighbors.csv"
TEMPLATE_HTML="countries_data-graph.html"
REQS="requirements.txt"
SEARX_DIRECTORY=$1
if [ $# -eq 0 ]; then
  echo "Usage: $0 <searxng_directory>"
  exit 1
fi
cat $REQS >>$SEARX_DIRECTORY/$REQS
mv $TEMPLATE_HTML $SEARX_DIRECTORY/searx/templates/simple/answer/$TEMPLATE_HTML
mv $CSV_HELPER $SEARX_DIRECTORY/searx/plugins/$CSV_HELPER
mv $PLUGIN_PY $SEARX_DIRECTORY/searx/plugins/$PLUGIN_PY

echo -e "\033[0;31m DONT FORGET TO REGISTER THE PLUGIN IN THE $SEARX_DIRECTORY/searx/settings.yml FILE!!!!! \033[0m"

printf "Example (probably badly indented):\nplugins:\n\t...BLABLABLA\n\tsearx.plugins.countries_data.CountriesDataPlugin:\n\t\tactive:true"
