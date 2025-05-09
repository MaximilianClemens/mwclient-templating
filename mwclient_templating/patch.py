# mwclient_templating/patch.py
from typing import Any
from .parser import parse_template, extract_templates, render_template

def templating(page):
    class ParsedPage(type(page)):
        def __init_subclass__(cls, **kwargs): super().__init_subclass__(**kwargs)

        @property
        def title(self) -> str:
            return self.name

        def _initialize(self):
            if not hasattr(self, '_templates'):
                self._templates = {}
            if not hasattr(self, '_filtered_text'):
                self._filtered_text = None

        def template(self, template_name: str, number: int = 0):
            self.parse()
            return self.templates(template_name)[number]

        def templates(self, template_name: str) -> list:
            return self.all_templates().get(template_name.strip(), [])

        def all_templates(self):
            self.parse()
            return self._templates or {}

        def parse(self, text_overwrite=None):
            if self._templates: return
            raw = text_overwrite or self.text()
            parsed = extract_templates(raw)
            self._templates, self._filtered_text, counter = {}, raw, {}
            for tmpl in parsed:
                node = parse_template(tmpl)
                name = node.type.strip()
                number = counter.get(name, 0)
                counter[name] = number + 1
                self._templates.setdefault(name, []).append(node)
                placeholder = f"[[#mwclient_placeholder:{name}#{number}]]"
                self._filtered_text = self._filtered_text.replace(tmpl, placeholder, 1)

        def _compile(self):
            if not self._templates:
                return self.text()
            compiled = self._filtered_text
            for template_type, instances in self._templates.items():
                for i, tmpl in enumerate(instances):
                    compiled = compiled.replace(
                        f"[[#mwclient_placeholder:{template_type}#{i}]]",
                        render_template(tmpl)
                    )
            return compiled

        def edit(self, text: str=None, **kwargs: Any):
            if text:
                super().edit(text=text, **kwargs)
            else:
                if self._templates:
                    super().edit(text=self._compile(), **kwargs)

    page.__class__ = ParsedPage
    page._initialize()
    return page
