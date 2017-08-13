# ~*~ coding: utf-8 ~*~

from django import template

register = template.Library()

@register.filter
def pagination_range(total_page, current_num=1, display=5):
    """Return Page range
    :param total_page: Total numbers of paginator
    :param current_num: current display page num
    :param display: Display as many as [:display:] page
    In order to display many page num on web like:
    < 1 2 3 4 5 >
    """
    try:
        current_num = int(current_num)
    except ValueError:
        current_num = 1

    half_display = int(display/2)
    start = current_num - half_display if current_num > half_display else 1
    if start + display <= total_page:
        end = start + display
    else:
        end = total_page + 1
        start = end - display if end > display else 1

    return range(start, end)

@register.filter
def serial(loopcounter,page):
    try:
        page = int(page)
    except Exception:
        page = 1
    number = (page-1)*20+loopcounter
    return number
