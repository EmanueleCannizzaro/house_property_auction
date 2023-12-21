
from jinja2 import Template
import os


def create_gallery_page(filename:str, filenames:list, root_folder:str, template_filename:str='template.html'):

    '''
    The code defines a function `create_gallery_page` that creates an HTML gallery page from a list of filenames of images located in a specified `root_folder`.

    The function takes the following parameters:

    - `filename`: A string that represents the name of the output HTML gallery page.
    - `filenames`: A list of strings that contains the filenames of the images in the gallery. Only filenames that end with '.jpg' are included in the gallery.
    - `root_folder`: A string that represents the root folder where the images are located. This parameter is used to calculate the relative paths of the images in the HTML gallery.
    - `template_filename`: An optional string parameter that specifies the name of the Jinja2 template file to use for generating the HTML gallery page. If not specified, it defaults to 'template.html'.

    The function begins by creating an empty list `images` to store the relative paths of the images in the gallery. It then iterates through the `filenames` list, and for each filename that ends with '.jpg', it calculates the relative path of the image file with respect to the `root_folder` using the `os.path.relpath()` function. The relative path is then appended to the `images` list.

    The function then reads the contents of the Jinja2 template file specified in the `template_filename` parameter using the `open()` function, and it creates a `Template` object using the `Template` class from the `jinja2` module.

    The function then renders the template using the `render()` method of the `Template` object, passing in the `images` list as a keyword argument.

    Finally, the function writes the rendered HTML to the output file specified in the `filename` parameter using the `open()` function with the 'w' mode. The `write()` method of the file object is then used to write the HTML string to the file.

    Overall, the `create_gallery_page()` function takes a list of image filenames, generates a list of relative paths for each image, and then uses a Jinja2 template to create an HTML gallery page that displays the images with their respective relative paths. The resulting gallery page is then saved to the specified output file.
    '''

    images = []
    for filename in filenames:
        if filename.endswith('.jpg'):
            images.append(os.path.relpath(filename, root_folder))

    with open(template_filename, 'r') as f:
        template = Template(f.read())

    html = template.render(images=images)

    #gallery.html
    with open(filename, 'w') as f:
        f.write(html)
