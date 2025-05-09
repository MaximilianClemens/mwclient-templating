# mwclient-templating

An extension for [mwclient](https://github.com/mwclient/mwclient) that enables powerful MediaWiki **template parsing**, **editing**, and **re-rendering**.

With `mwclient-templating`, you can access and manipulate MediaWiki templates in a structured way using Python dictionaries and objects — including support for nested templates, multi-instance templates, and multiline values.


## 🔧 Installation

```bash
pip install git+https://github.com/MaximilianClemens/mwclient-templating.git
# or local development
git clone https://github.com/MaximilianClemens/mwclient-templating.git
cd mwclient-templating
pip install -e .
````

## 🚀 Usage

```python
from mwclient import Site
from mwclient_templating import templating
from datetime import datetime

site = Site("wiki.example.org")
page = site.Pages['MyPage']

# Activate template parsing
page = templating(page)

# Access a template
tmpl = page.template('FW-Antrag')  # First 'FW-Antrag' template
print(tmpl['Mitarbeitername'])

# Modify a field
tmpl['Mitarbeitername'] = 'Max Mustermann'

# Access nested templates
for rule in tmpl.templates('Rules'):
    print(rule['Source'], '->', rule['Destination'])

# Make Changes
tmpl['AcceptedAt'] = datetime.today().strftime('%Y-%m-%d')

# Save Changes
page.edit()
```

## 🧪 Testing

Tests are written using [pytest](https://docs.pytest.org/).

Run them using:

```bash
pytest tests/
```

## 🧩 Template Access Example

```python
fw = page.template("FW-Antrag")
fw["FW-Von"] = "2025-01-01"

for rule in fw.templates("Rules"):
    if rule["Port"] == "443":
        rule["Description"] = "Updated port description"
```
