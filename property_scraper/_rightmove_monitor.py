non_decimal = re.compile(r'[^\d.]+')

def get_info(block):

    propertyId = block.get('id')
    propertyId = int(non_decimal.sub('', propertyId))

    status = block.find('span', {"class": "propertyCard-contactsAddedOrReduced"}).text

    address = block.find('address', {"class": "propertyCard-address"}).text.replace('\n', '').replace("'", "\"")

    price = block.find('div', {"class": "propertyCard-priceValue"}).text
    price = non_decimal.sub('', price)
    price = int(price) if price else 0

    agent = block.find('span', {"class": "propertyCard-branchSummary-branchName"}).text

    numOfBeds = block.find('h2', {"class": "propertyCard-title"}).text
    numOfBeds = non_decimal.sub('', numOfBeds)
    numOfBeds = int(numOfBeds) if numOfBeds else 0

    return propertyId, status, address, agent, numOfBeds, price
