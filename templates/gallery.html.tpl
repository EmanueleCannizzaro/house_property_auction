<!DOCTYPE html>
<html>
  <head>
    <title>Estate Database Gallery</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/5.0.1/css/bootstrap.min.css">
  </head>
  <body>
    <div class="container">
      <div class="row">
        {% for image_path in images %}
          <div class="col-sm-4">
            <div class="card">
              <img src="{{ image }}" class="card-img-top">
            </div>
          </div>
        {% endfor %}
      </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/5.0.1/js/bootstrap.min.js"></script>
  </body>
</html>
