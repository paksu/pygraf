try:
    basestring
except NameError:
    # For python 3 compatibility
    basestring = str


def format_string(key):
    """
    Formats either measurement names, tag names or tag values.

    Measurement name and any optional tags separated by commas. Measurement names, tag keys,
    and tag values must escape any spaces, commas or equal signs using a backslash (\).
    For example: \ and \,.

    All tag values are stored as strings and should not be surrounded in quotes.
    """
    if isinstance(key, basestring):
        key = key.replace(",", "\,")
        key = key.replace(" ", "\ ")
        key = key.replace("=", "\=")
    return key


def format_value(value):
    """
    Integers are numeric values that do not include a decimal and are followed by a trailing i when inserted
    (e.g. 1i, 345i, 2015i, -10i). Note that all values must have a trailing i.
    If they do not they will be written as floats.

    Floats are numeric values that are not followed by a trailing i. (e.g. 1, 1.0, -3.14, 6.0e5, 10).

    Boolean values indicate true or false. Valid boolean strings for line protocol are
    (t, T, true, True, TRUE, f, F, false, False and FALSE).

    Note: boolean syntax varies between write and query.
        see https://docs.influxdata.com/influxdb/v1.8/troubleshooting/frequently-asked-questions/#why-can-t-i-query-boolean-field-values

    Strings are text values. All string field values must be surrounded in double-quotes ".
    If the string contains a double-quote, the double-quote must be escaped with a backslash, e.g. \".
    Strings are required to be under 64KB

    """
    if isinstance(value, basestring):
        value = value.replace('"', '\"')
        value = u'"{0}"'.format(value)
        # trim string value until it is under 64K
        while len(value.encode('utf-8')) > 2**16:
            value = value[:-2]
    elif isinstance(value, bool):
        # we save a small number of bytes here
        value = "t" if value else "f"
    elif isinstance(value, int):
        value = "{0}i".format(value)
    elif isinstance(value, float):
        value = str(value)
    return value
