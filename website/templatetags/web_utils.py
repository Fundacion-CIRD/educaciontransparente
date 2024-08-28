from django import template

register = template.Library()


@register.filter(name="format_number")
def format_number(value):
    try:
        # Convert the value to an integer or float
        value = int(value)
    except ValueError:
        try:
            value = float(value)
        except ValueError:
            return value  # Return as is if it's not a number

    # Format the number with commas as thousand separators
    return f"{value:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
