from django import template
# in template.Library() registered
# all tags and filters templates
register = template.Library()
# add attribut class in order to
# in signup.html will appear attribut class
# for using in css .class


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})
