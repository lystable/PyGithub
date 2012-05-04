{% for dependency in class.dependencies %}
import {{ dependency }}
{% endfor %}

# This allows None as a valid value for an optional parameter
class DefaultValueForOptionalParametersType:
    pass
DefaultValueForOptionalParameters = DefaultValueForOptionalParametersType()

class {{ class.name }}( object ):
    def __init__( self, requester, attributes, lazy ):
        self.__requester = requester
        self.__completed = False
        self.__initAttributes()
        self.__useAttributes( attributes )
        if not lazy:
            self.__complete()

{% for attribute in class.attributes|dictsort:"name" %}
    @property
    def {{ attribute.name }}( self ):
        self.__completeIfNeeded( self.__{{ attribute.name }} )
        return self.__{{ attribute.name }}
{% endfor %}

{% for method in class.methods|dictsort:"name" %}
    def {{ method.name|join:"_" }}( {% include "GithubObject.Parameters.py" with function=method only %} ):
    {% if method.request %}
        {% include "GithubObject.MethodBody.DoRequest.py" %}
        {% include "GithubObject.MethodBody.UseResult.py" %}
    {% else %}
        pass
    {% endif %}
{% endfor %}

{% if class.identity %}
    # @todo Remove '_identity' from the normalized json description
    @property
    def _identity( self ):
        return {% include "GithubObject.Concatenation.py" with concatenation=class.identity only  %}
{% endif %}

    def __initAttributes( self ):
{% for attribute in class.attributes|dictsort:"name" %}
        self.__{{ attribute.name }} = None
{% endfor %}

    def __completeIfNeeded( self, testedAttribute ):
        if not self.__completed and testedAttribute is None:
            self.__complete()

    # @todo Do not generate __complete if type has no url attribute
    def __complete( self ):
        status, headers, data = self.__requester.request(
            "GET",
            self.__url,
            None,
            None
        )
        self.__useAttributes( data )
        self.__completed = True

    def __useAttributes( self, attributes ):
         #@todo No need to check if attribute is in attributes when attribute is mandatory
{% for attribute in class.attributes|dictsort:"name" %}
        if "{{ attribute.name }}" in attributes:
{% if attribute.type.simple %}
            self.__{{ attribute.name }} = attributes[ "{{ attribute.name }}" ]
{% else %}
            self.__{{ attribute.name }} = {% if attribute.type.name != class.name %}{{ attribute.type.name }}.{% endif %}{{ attribute.type.name }}( self.__requester, attributes[ "{{ attribute.name }}" ], lazy = True )
{% endif %}

{% endfor %}
