# mwclient_templating/parser.py
class TemplateNode:
    def __init__(self, type_, data):
        self.type = type_
        self.data = data

    def templates(self, key=None):
        results = []
        for v in self.data.values():
            if isinstance(v, TemplateNode):
                results.append(v)
            elif isinstance(v, list):
                results.extend([x for x in v if isinstance(x, TemplateNode)])
        if key:
            return self.data.get(key, [])
        return results

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return f"<TemplateNode {self.type}: {len(self.data)} keys>"


def extract_templates(text):
    stack, templates, start = [], [], None
    i = 0
    while i < len(text) - 1:
        if text[i:i+2] == '{{':
            if not stack: start = i
            stack.append('{{')
            i += 2
        elif text[i:i+2] == '}}' and stack:
            stack.pop()
            i += 2
            if not stack and start is not None:
                templates.append(text[start:i])
        else:
            i += 1
    return templates


def parse_template(s):
    s = s.strip()
    if not s.startswith("{{") or not s.endswith("}}"): return s
    s = s[2:-2]

    parts, current, depth, i = [], '', 0, 0
    while i < len(s):
        if s[i:i+2] == '{{':
            depth += 1; current += '{{'; i += 2
        elif s[i:i+2] == '}}':
            depth -= 1; current += '}}'; i += 2
        elif s[i] == '|' and depth == 0:
            parts.append(current.strip()); current = ''; i += 1
        else:
            current += s[i]; i += 1
    if current: parts.append(current.strip())

    template_type = parts[0]
    data = {}
    for part in parts[1:]:
        if '=' in part:
            key, val = part.split('=', 1)
            key, val = key.strip(), val.strip()
            if val.startswith('{{') and val.endswith('}}'):
                inner = extract_templates(val)
                if len(inner) == 1:
                    data[key] = parse_template(inner[0])
                else:
                    data[key] = [parse_template(x) for x in inner]
            else:
                data[key] = val
        else:
            data[part] = None
    return TemplateNode(template_type, data)


def render_template(template_node):
    lines = []
    for key, val in template_node.data.items():
        if isinstance(val, TemplateNode):
            lines.append(f"|{key}={render_template(val)}")
        elif isinstance(val, list):
            inner = ''.join(render_template(v) for v in val)
            lines.append(f"|{key}={inner}")
        else:
            lines.append(f"|{key}={val}")
    inner = '\n' + '\n'.join(lines) + '\n' if lines else ''
    return f"{{{{{template_node.type}{inner}}}}}"
