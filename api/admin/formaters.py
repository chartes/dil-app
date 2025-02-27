from markupsafe import Markup

def _create_tooltip(comment, place):
    return f"""<a data-toggle="tooltip" data-placement="{place}" data-html="true" title="<i>{comment}</i>">
  <i class="fa fa-info-circle"></i>
</a>"""


def _format_label_form_with_tooltip(label, comment, place="bottom"):
    return Markup(f"{label} {_create_tooltip(comment, place)}")


def _format_link_add_model(description, href="#"):
    return f"""
     <span class="desc-add-model-item">
        Absent de la liste ? Ajouter {description}
        <a target="_blank" class="link-model" href="{href}">
        <span class="plus-icon"></span>
        </a>
     </span>
    """

def _format_href(prefix_url, label):
    return Markup(f'<a href="{prefix_url}{label}" target="_blank">{label}</a>')


def format_image():
    pass


def format_map():
    pass

