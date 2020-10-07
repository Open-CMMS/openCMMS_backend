from django import template

register = template.Library()


@register.filter(name='extraire')
def extract(list, position):
    """
    Retourne l'élement de la liste 'liste' à la position 'position'

    :param liste: La liste d'objets.
    :param position: La position de l'objet à extraire de la liste.
    :return: L'objet demandé.
    """
    return list[position]


@register.simple_tag
def def_element(element):
    """
    Permet de définir un objet 'element' dans un template

    :param element: L'objet à définir.
    :return: L'objet demandé.
    """
    return element
