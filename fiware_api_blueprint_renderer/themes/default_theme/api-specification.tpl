{% macro slug( id ) %}{{ id | lower | replace(' ', '_') }}{% endmacro %}

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ name }}</title>
    <link rel="stylesheet" type="text/css" href="css/api-specification.css">
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <script src="js/jquery-1.11.3.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <link rel="stylesheet" href="css/hightlight_default_theme.css">
    <script src="js/highlight.pack.js"></script>
    <script>hljs.initHighlightingOnLoad();</script>
</head>
<body>
    <div class="container">
        <div class="row">
           <!-- TOC -->
           <div class="col-md-3">
                {% include "fragments/toc.tpl" %}
            </div>

            <div class="col-md-9">
               <h1 id="api-name">{{ name }}</h1>
               <p>{{ description }}</p>
    
               <!-- API metadata -->
               {% include "fragments/api_metadata.tpl" %}
    
               <!-- API blueprint -->
               {% include "fragments/api_blueprint.tpl" %}
            </div>
        </div>
    </div>
</body>
</html>
