from flask import Markup


def _create_tooltip(comment, place):
    return f"""<a data-toggle="tooltip" data-placement="{place}" data-html="true" title="<i>{comment}</i>">
  <i class="fa fa-info-circle"></i>
</a>"""

def _format_label_form_with_tooltip(label, comment, place="bottom"):
    return Markup(f"{label} {_create_tooltip(comment, place)}")




def format_image():
    pass

def format_map():
    pass

def format_href():
    pass