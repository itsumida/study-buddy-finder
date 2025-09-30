from django import template

register = template.Library()

@register.filter
def average_rating(reviews):
    if not reviews:
        return 0
    total = sum([review.rating for review in reviews])
    return total / len(reviews)

@register.filter
def times(number):
    return range(number)

