{{ name }}
===============================================================================
{{ short_desc }}

{{ doc }}

.. toctree::
  :maxdepth: 2

{% for item in toc %}
  {{ item }}
{% endfor %}
  


