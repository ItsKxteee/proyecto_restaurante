from django import template

register = template.Library()


@register.filter
def es_mesero_o_admin(user):
    if not user or not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser or user.groups.filter(name="Meseros").exists()


@register.filter
def get_item(diccionario, clave):
    if diccionario is None:
        return ""
    return diccionario.get(str(clave), "")
