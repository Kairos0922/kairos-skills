"""Allowed editorial components.

The renderer may map Markdown blocks only to this bounded component set. New
components should be added rarely and only when the visual system genuinely needs
another semantic role.
"""

ALLOWED_COMPONENTS = {
    "Paragraph",
    "Insight",
    "Quote",
    "Summary",
    "Divider",
    "List",
    "CTA",
    "Heading",
    "Code",
    "Table",
}

