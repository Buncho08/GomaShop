from django import template

register = template.Library()

@register.filter
def multiply(num1, num2):
    # {{ num1 | multiply:num2 }}
    return num1 * num2

@register.filter
def divided(num1, num2):
    # {{ num1 | divided:num2 }}
    return num1 // num2

@register.filter
def remainder(num1, num2):
    # {{ num1 | remainder:num2 }}
    return num1 % num2