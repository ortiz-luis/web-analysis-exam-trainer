# Official Course Content Map

This document freezes the official content boundary for the real question bank.
Questions must be based only on developed or practiced content from the official notebooks in `notebooks/`.
Concepts that are only briefly mentioned may be used as context, but they must not become standalone assessed topics unless they are developed or practiced in notebook examples or exercises.

## Source Notebooks

- `notebooks/cours_1.ipynb`
- `notebooks/cours_1_corr.ipynb`
- `notebooks/cours_2.ipynb`
- `notebooks/cours_2_corr.ipynb`
- `notebooks/cours_3_exercice.ipynb`
- `notebooks/cours_3_corrige.ipynb`
- `notebooks/cours4.ipynb`
- `notebooks/cours4_corr.ipynb`

## Notebook Content

### `cours_1.ipynb`

Developed or practiced:

- Python variables, naming rules, and dynamic typing
- Basic types: `int`, `float`, `str`, `bool`
- Arithmetic operations, type conversion, and string formatting
- Lists: indexing, slicing, mutation, and combining lists
- Dictionaries: creation, access, and update
- Conditions: `if`, `elif`, `else`, and logical operators
- Loops: `for`, `range()`, `while`, and `zip()`
- Functions: parameters, return values, and multiple returns
- Integrated retail-sales style practice using variables, lists, dictionaries, conditions, loops, and functions

Only mentioned or lightly shown:

- Why Python, IDEs, notebooks, and text editors
- General coding advice
- `random` and `math` imports as bonus module examples

### `cours_1_corr.ipynb`

Developed or practiced:

- Corrected solutions for the Python basics exercises
- Expected solution patterns for variables, lists, dictionaries, conditions, loops, functions, and integrated practice

Only mentioned or lightly shown:

- Same introductory material as `cours_1.ipynb`
- `random` and `math` imports as bonus examples

### `cours_2.ipynb`

Developed or practiced:

- Pandas `DataFrame` creation from dictionaries and list-of-lists
- DataFrame exploration with methods such as `head()`
- CSV import and export with `pd.read_csv()` and `to_csv()`
- Index manipulation
- Selection with `.loc`
- Row filtering with conditions
- Data modification and new-column creation with `.loc`
- Missing data handling: `dropna()` and `fillna()`
- Column renaming and column deletion
- DataFrame merging with `pd.merge()` and `.merge()`
- Descriptive statistics: `describe()`, `mean()`, and correlations
- Aggregation with `groupby()`
- Practical e-commerce, HR, and sales analysis exercises

Only mentioned or lightly shown:

- NumPy as often used with Pandas
- Visualization is referenced as a next-course direction, not practiced here

### `cours_2_corr.ipynb`

Developed or practiced:

- Corrected solutions for the Pandas exercises
- DataFrame creation, `.loc` selection and filtering, cleaning, merging, descriptive statistics, `groupby()`, and correlations
- Final e-commerce-style analysis solution

Only mentioned or lightly shown:

- Same Pandas objectives as `cours_2.ipynb`
- NumPy as supporting import/context

### `cours_3_exercice.ipynb`

Developed or practiced:

- Web scraping workflow with `requests`, `BeautifulSoup`, `pandas`, and `random`
- Connecting to a website with `requests`
- Parsing HTML with BeautifulSoup
- Finding a table
- Extracting links with `<a>` tags
- Building complete URLs and country names
- Creating a DataFrame and saving CSV
- Choosing a random country
- Scraping a country page
- Finding population projection tables
- Extracting rows and locating the 2035 population
- Combining the scraping workflow into final code

Only mentioned or lightly shown:

- Older BeautifulSoup syntax such as `findAll`, mainly as comparison
- Modern BeautifulSoup syntax is emphasized

### `cours_3_corrige.ipynb`

Developed or practiced:

- Corrected implementation of the Cours 3 scraping workflow
- `requests.get`
- `BeautifulSoup(response.text, ...)`
- `soup.find(...)`
- `find_all(...)`
- Filtering by `class_`
- Extracting attributes such as `href`
- Extracting cleaned text with `get_text(strip=True)`
- Building DataFrames and exporting CSV
- Random country selection and population lookup for 2035

Only mentioned or lightly shown:

- Older BeautifulSoup syntax using dictionary-style class filters as an alternative/comparison

### `cours4.ipynb`

Developed or practiced:

- Advanced scraping case study around AlloCine
- Pagination by modifying `?page=N`
- Scraping multiple pages
- Extracting film links and titles
- Looping through films on one page and across several pages
- Creating a film DataFrame and exporting CSV
- Re-importing CSV and converting a column to a list
- Choosing a random film
- Extracting technical film information
- Handling variable HTML structures
- Converting dictionaries and list-of-dictionaries to DataFrames

Only mentioned or lightly shown:

- Request politeness with `time.sleep(1)` appears in the recap/objectives, but the exercise notebook itself is mostly scaffolded
- Partial class matching is not developed in the exercise notebook

### `cours4_corr.ipynb`

Developed or practiced:

- Corrected AlloCine scraper
- Pagination with `?page=N`
- `requests.get` and BeautifulSoup parsing
- Finding film containers and `<li>` entries
- Extracting titles and links
- Looping across pages
- Exporting film links to CSV
- Reading CSV with `pd.read_csv`
- Converting columns with `.tolist()`
- Using `time.sleep(1)` between requests
- Extracting technical information from variable HTML
- Trying several selectors, including partial class matching with `class_=lambda ...`
- Building dictionaries, DataFrames, and CSV outputs

Only mentioned or lightly shown:

- The recap reinforces the concepts; most listed items also appear in corrected code

## Stage Plan

### `lesson_1_python_basics`

Topics:

- Variables, types, operations, conversions
- String formatting
- Lists, slicing, mutation
- Dictionaries
- Conditions and logical operators
- Loops: `for`, `range`, `while`, `zip`
- Functions and return values

Approximate number of questions: 35-45

### `lesson_2_pandas_minimal`

Pandas is included because it appears in the official notebooks, even if the professor announcement emphasizes Python, HTML/CSS, and web scraping.

Topics:

- DataFrame creation
- DataFrame exploration
- CSV import/export
- Indexes
- `.loc` selection, filtering, and modification
- Missing values
- Rename/drop columns
- Merge
- Descriptive statistics, `groupby`, and correlation

Approximate number of questions: 35-45

### `lesson_3_html_bs4_scraping`

Topics:

- `requests.get`
- HTML parsing with BeautifulSoup
- `find`, `find_all`, and `class_`
- Extracting links, attributes, and text
- Building URLs
- Scraping tables and rows
- Saving scraped results to CSV
- Population projection mini-pipeline

Approximate number of questions: 30-40

### `lesson_4_allocine_scraping`

Topics:

- Pagination
- Multi-page scraping loops
- Film title/link extraction
- CSV export/import
- `.tolist()`
- Random film selection
- Technical-information extraction
- Variable HTML structures
- `time.sleep`
- Partial class matching from the corrected notebook

Approximate number of questions: 30-40

### `integrated_practice`

Topics:

- End-to-end workflows combining Python basics, Pandas, BeautifulSoup, CSV, and scraping pipelines
- Predict-output and short explanation questions over complete notebook-style snippets

Approximate number of questions: 20-30

### `exam_mock_01` to `exam_mock_10`

Each exam mock must contain exactly 5 questions:

- 1 Python basics question
- 1 Pandas or data handling question
- 1 HTML/CSS or BeautifulSoup question
- 1 scraping workflow question
- 1 integrated oral-style question

The mock questions must use only developed or practiced notebook content.

## Forbidden Topics

Do not create real questions about:

- APIs
- Selenium
- JavaScript-rendered scraping
- Authentication
- Databases
- Plotting
- Machine learning
- Scrapy
- Advanced scraping ethics beyond what appears in the notebooks
