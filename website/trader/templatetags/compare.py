from django import template


register = template.Library()



# compares two numbers,  returning a positive/negative
def compare(first, second):
    
    
    sum = "%.2f" % (float(first) - float(second))
        
    return sum

@register.



def compare(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return CurrentTimeNode(format_string[1:-1])