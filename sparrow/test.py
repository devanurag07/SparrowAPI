import re


def phone_format(phone_number):

    clean_phone_number = re.sub('[^0-9]+', '', phone_number)
    formatted_phone_number = re.sub(r'\D', '', clean_phone_number)
    if(formf)

    return formatted_phone_number


print(phone_format("333 (234)"))