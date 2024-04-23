from django import template
from django.utils.safestring import mark_safe

from shoepage.models import Category

register = template.Library()


@register.simple_tag
def categories():
    items = Category.objects.filter(is_active=True).order_by('title')
    items_li = ""
    for i in items:
        items_li += """<li><a href="/category/{}">{}</a></li>""".format(i.slug, i.title)
    return mark_safe(items_li)

@register.simple_tag
def categories_mobile():
    items = Category.objects.filter(is_active=True).order_by('title')
    items_li = ""
    for i in items:
        items_li += """<li class="item-menu-mobile"><a href="/category/{}">{}</a></li>""".format(i.slug, i.title)
    return mark_safe(items_li)


@register.simple_tag
def categories_li_a():
    items = Category.objects.filter(is_active=True).order_by('title')
    items_li_a = ""
    for i in items:
        items_li_a += """<li class="p-t-4"><a href="/category/{}" class="s-text13">{}</a></li>""".format(i.slug,
                                                                                                         i.title)
    return mark_safe(items_li_a)


@register.simple_tag
def categories_div():
    """
    section banner
    :return:
    """
    items = Category.objects.filter(is_active=True).order_by('title')
    items_div = ""
    item_div_list = "<div class='row'>"  # Start row
    for i, j in enumerate(items, 1):
        if i % 4 == 1:  # Start a new row for every 4th item
            item_div_list += "<div class='row'>"  # Start a new row
        items_div += """<div class="col-md-4 mb-4">"""  # Start column with margin
        items_div += """<div class="block1 hov-img-zoom pos-relative"><img src="/media/{}" class="img-fluid" alt="IMG-BENNER" style="width:100px; height:100px;"><div class="block1-wrapbtn w-size2"><a href="/category/{}" class="btn btn-primary m-text2 bg3 hov1 trans-0-4">{}</a></div></div>""".format(
            j.image, j.slug, j.title)
        items_div += "</div>"  # End column
        if i % 4 == 0 or i == len(items):  # End row if it's the 4th item or the last item
            item_div_list += items_div + "</div>"  # End row
            items_div = ""  # Reset items_div for the next row
    item_div_list += "</div>"  # End the last row
    return mark_safe(item_div_list)