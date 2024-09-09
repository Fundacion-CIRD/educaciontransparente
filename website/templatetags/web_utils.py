from django import template

register = template.Library()


@register.filter(name="format_number")
def format_number(value, show_decimals=False):
    try:
        value = int(value)
    except TypeError:
        return "0"
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            return value  # Return as is if it's not a number
    if show_decimals:
        value = f"{value:.2f}"
    else:
        value = f"{value:,.0f}"
    return value.replace(",", "X").replace(".", ",").replace("X", ".")


@register.simple_tag
def multiply(value1, value2):
    try:
        return float(value1) * float(value2)
    except (ValueError, TypeError):
        return 0
