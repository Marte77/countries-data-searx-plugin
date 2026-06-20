# World Bank Country Data in Searxng 
<img width="700" height="596" alt="billede" src="https://github.com/user-attachments/assets/72957f4b-4568-4eb5-8821-cd9140b3f90c" />

i did this plugin because i really missed the google graphs they used to have prior to the AI mess that is modern google.
the data comes from the world bank, via the pip library in the requirements folder. currently only has gdp, gdp per capita, population

the code is a bit messy, its my first time doing flask templating and working with plugins in searx and working with dataframes.

# metrics to add
- i want to have graphs have multiple countries, so if i search "population spain", neighbouring countries would be also listed in the graph, like google used to do as well
- other metrics that may be insteresting and are often used

# installing
1. just run `install_plugin.sh <searx_main_path>` (the path should be the folder that contains the searx/ folder!)
2. if you use other custom themes, you will have to move the html file in the repo to the correct `<searx_main_path>/searx/templates/<your_theme>/answer/` path
3. make sure the requirements are properly installed, I spent a lot of time looking for an answer because i forgot to `pip install -r requirements.txt` since my service file doesn't use make
 
