# -*- coding: utf-8 -*-
"""formaters.py

Formatters for the admin interface, including tooltips, links, and other HTML formatting.
"""

from markupsafe import Markup
import uuid
import hashlib
import html


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


def _format_link_add_model(
    description: str,
    href: str ="#",
    target_field: str = None,
    modal_title: str = None,
    element_id: str = None,
):
    """Format an HTML link for adding a model to a repository, with optional parameters for description, href, target field, modal title, and element ID.

    :param description: The text to describe the model being added.
    :type description: str
    :param href: The URL to link to when the user clicks the add model link.
    :type href: str
    :param target_field: The ID of the form field that should be updated with the new
    model's information after it is added. Optional.
    :type target_field: str, optional
    :param modal_title: The title to display in the modal dialog when adding the model.
    If not provided, a default title will be generated using the description.
    :type modal_title: str, optional
    :param element_id: An optional unique identifier for the link element. If not provided,
a random UUID-based ID will be generated to ensure uniqueness.
    :type element_id: str, optional
    :return: An HTML string for the add model link, including data attributes for the modal
    functionality.
    :rtype: Markup
    """
    if element_id is None:
        element_id = hashlib.sha1(uuid.uuid4().hex.encode("utf-8")).hexdigest()
    link_id = f"add-model-link-{element_id}"
    safe_description = html.escape(description)
    safe_href = html.escape(href, quote=True)
    safe_target_field = html.escape(target_field or "", quote=True)
    safe_modal_title = html.escape(
        modal_title or f"Ajouter {description} au référentiel",
        quote=True,
    )
    return Markup(f"""
    <span class="desc-add-model-item">
        Absent de la liste ? Ajouter {safe_description}
        <a href="#" id="{link_id}" class="link-model js-open-admin-modal" data-href="{safe_href}" data-target-field="{safe_target_field}" data-modal-title="{safe_modal_title}">
            <span class="plus-icon"></span>
        </a>
    </span>
    """)

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
