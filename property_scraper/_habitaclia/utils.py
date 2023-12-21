import re


def clean_text(text, is_upper=False):
    try:
        new_text = text.replace('\n', ' ')
        new_text = new_text.replace('\r', ' ')
        new_text = new_text.replace('  ', ' ')
        if is_upper:
            return new_text.strip().upper()
        return new_text.strip()
    except Exception:
        return None


def clean_location(text):
    replaced = re.sub('\s{2,};', ';', text)
    return replaced.strip()


def clean_tags(text):
    try:
        replaced = re.sub('\s{2,};', ';', text)
        replaced = re.sub(';{2,}', ';', replaced)
        new_text = replaced.replace(';;', ';')
        new_text = new_text.replace(' ;', ';')
        new_text = new_text.replace('\r', ' ')
        new_text = new_text.replace('  ', ' ')
        return new_text.strip()
    except Exception:
        return None

def clean_img(text):
    try:
        replaced = re.sub('\s{2,};', ';', text)
        replaced = re.sub(';{2,}', ';', replaced)
        new_text = replaced.replace(';;', ';')
        new_text = new_text.replace(' ;', ';')
        new_text = new_text.replace('\r', ' ')
        new_text = new_text.replace('  ', ' ')
        return new_text.strip()
    except Exception:
        return None


def get_floor_plan(images):
    for img in images:
        if "/plano-" in img:
            return img
    return None


def get_certificado_energetico(images):
    for img in images:
        if "/certificado-energetico-" in img:
            return img
    return None




