"""Allowed semantic components.

The renderer may map Markdown blocks only to this bounded component set. New
components should be added rarely and only when the editorial system genuinely
needs another semantic role.
"""

ALLOWED_COMPONENTS = {
    "Callout",
    "ClosingNote",
    "Heading",
    "Paragraph",
    "Divider",
    "Figure",
    "Insight",
    "Lead",
    "List",
    "Pullquote",
    "Quote",
    "SoftList",
    "Steps",
    "Code",
    "CodeBlock",
    "TableStack",
}

ALLOWED_KAIROS_COMPONENTS = {
    "closing-note",
    "figure",
    "insight",
    "lead",
    "pullquote",
    "soft-list",
}
