
def cookies_raw_to_dic(cookie_raw_):
    """
    通过原始cookie转换cookie字典
    :param cookie_raw_: 浏览器原始cookie
    :return: 字典-cookies
    """
    cookies_dict = {}
    for line in cookie_raw_.strip("\n").split("; "):
        key, value = line.split("=", 1)
        cookies_dict[key] = value
    # print(cookies_dict)
    # return dict(line.split("=", 1) for line in cookie_raw.split("; "))
    return cookies_dict