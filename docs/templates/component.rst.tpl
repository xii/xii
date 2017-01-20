{{ name }}
===============================================================================
{{ short_desc }}

Attributes available for this component:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

=============== =============== ========================================= =======================================
Name            Required        Type                                      Example
=============== =============== ========================================= =======================================
{% for a in attrs %}
{{ a.name|fill(15) }} {{ a.required|fill(15) }} {{ ".. parsed-literal::"|fill(40) }}  .. parsed-literal::

{% for i in range(0,a.key_desc_len) %}
{% if i > a.example_len -1 %}
                                  {{ a.key_desc[i]|fill(42) }}
{% else %}
                                  {{ a.key_desc[i]|fill(42) }}{{ a.example[i] }}
{% endif %}
{% endfor %}
{% if a.name != attrs[-1].name %}
--------------- --------------- ----------------------------------------- ---------------------------------------
{% else %}
=============== =============== ========================================= =======================================
{% endif %}
{% endfor %}

.. note::

  Problem how to read the table? Check out _Documentation

{{ doc }}

.. toctree::
  :maxdepth: 2

{% for a in attrs %}
{% if a.extra_info %}
  {{ item }}
{% endif %}
{% endfor %}
  


