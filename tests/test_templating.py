import pytest
from mwclient_templating.patch import templating
from mwclient_templating.parser import TemplateNode

SAMPLE_CONTENT = """

= Normale Templates =

'' Ohne Keys ''
{{Template1}}

'' Single Key ''
{{Template2
|Key1=Value1
}}

'' Multiple Keys ''
{{Template3
|Key1=Value1
|Key2=Value2
}}

'' Umlaute ''
{{Tämplate4
|Käy1=Välue1
|Käy2=Välue2
}}

'' Umlaute+Leerzeichen im Templatenamen''
{{Tämplate5 XY
|Käy1=Välue1
|Käy2=Välue2
}}

'' Umlaute+Leerzeichen in Keys''
{{Tämplate6
|Käy1 XY=Välue1
|Käy2 XY=Välue2
}}

'' Multiline ''
{{Template7
|Key1=
Das
ist
ein
mehrzeiliger Wert
|Key2=Das
hier auch
|Key3=Das nicht
}}

'' One-line ''
{{Template8|Key1=V1|Key2=V2}}




'' if ''
{{#ifeq: a | a | 1 | 0 }}

'' mixing newline One-line ''
{{Template9|Key1=V1
fefef|Key2=V2}}

== Multitempaltes ==
{{Template-N1
|Key1=V1.1
|Key2=V1.2
}}

{{Template-N1
|Key1=V2.1
|Key2=V2.2
}}

{{Template-N1
|Key1=V3.1
|Key2=V3.2
}}

"""

# Mock für eine mwclient.page.Page-Instanz
class MockPage:
    def __init__(self, text):
        self._text = text
        self.name = "MockPage"

    def text(self):
        return self._text


@pytest.fixture
def page():
    mock = MockPage(SAMPLE_CONTENT)
    return templating(mock)


def test_template_count(page):
    assert len(page.templates("Template1")) == 1
    assert len(page.templates("Template2")) == 1
    assert len(page.templates("Template3")) == 1
    assert len(page.templates("Template-N1")) == 3


def test_template_access(page):
    t3 = page.template("Template3")
    assert isinstance(t3, TemplateNode)
    assert t3["Key1"] == "Value1"
    assert t3["Key2"] == "Value2"

    t4 = page.template("Tämplate4")
    assert t4["Käy1"] == "Välue1"


def test_multiline_template(page):
    t7 = page.template("Template7")
    assert "mehrzeiliger" in t7["Key1"]
    assert "hier auch" in t7["Key2"]


def test_modification_and_compile(page):
    t = page.template("Template3")
    t["Key1"] = "CHANGED"
    rendered = page._compile()
    assert "CHANGED" in rendered
    assert "Template3" in rendered


def test_placeholder_preserved(page):
    compiled = page._compile()
    assert "{{Template1}}" in compiled
    assert "{{Template8" in compiled

def test_compile_no_change(page):
    raw = page.text()
    compiled = page._compile()
    assert raw == compiled
