# -*- coding: utf-8 -*-
"""formaters.py

Formatters for the admin interface, including tooltips, links, and other HTML formatting.
"""

from markupsafe import Markup


def _create_tooltip(comment: str, place: str) -> str:
    """Create an HTML tooltip element with the given comment and placement.

        :param comment: The text to display in the tooltip.
        :type comment: str
        :param place: The placement of the tooltip (e.g., "top", "bottom
    ", "left", "right"). Default is "bottom".
        :type place: str
        :return: An HTML string for the tooltip element.
        :rtype: str
    """
    return f"""<a data-toggle="tooltip" data-placement="{place}" data-html="true" title="<i>{comment}</i>">
  <i class="fa fa-info-circle"></i>
</a>"""


def _format_label_form_with_tooltip(
    label: str, comment: str, place: str = "bottom"
) -> Markup:
    """Format a form label with an attached tooltip.

        :param label: The text of the label to display.
        :type label: str
        :param comment: The text to display in the tooltip when hovering over the info icon.
        :type comment: str
        :param place: The placement of the tooltip (e.g., "top", "bottom
    ", "left", "right"). Default is "bottom".
        :type place: str
        :return: An HTML string combining the label and the tooltip.
        :rtype: Markup
    """
    return Markup(f"{label} {_create_tooltip(comment, place)}")


def _format_link_add_model(description, href="#"):
    """Format an HTML link for adding a model, with a description and a plus icon.

    :param description: The text to display in the link description.
    :type description: str
    :param href: The URL to link to when the plus icon is clicked. Default is
    "#".
    :type href: str
    :return: An HTML string for the add model link.
    :rtype: str
    """
    return f"""
     <span class="desc-add-model-item">
        Absent de la liste ? Ajouter {description}
        <a target="_blank" class="link-model" href="{href}">
        <span class="plus-icon"></span>
        </a>
     </span>
    """


def _format_href(prefix_url: str, label: str) -> Markup:
    """Format an HTML link with a given prefix URL and label.

    :param prefix_url: The URL prefix to use for the link (e.g., "https://example.com/").
    :type prefix_url: str
    :param label: The text to display for the link, which will be appended to the
    prefix URL.
    :type label: str
    :return: An HTML string for the link, opening in a new tab.
    :rtype: Markup
    """
    return Markup(f'<a href="{prefix_url}{label}" target="_blank">{label}</a>')
