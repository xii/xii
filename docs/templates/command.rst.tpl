{% if help %}
{{ name }} - {{ help }}
{% else %}
{{ name }}
{% endif %}
===============================================================================

::

{% for line in commandline %}
  {{ line }}
{% endfor %}

{{ description }}
