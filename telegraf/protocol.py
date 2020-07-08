from telegraf.utils import format_string, format_value


class Line(object):
    def __init__(self, measurement, values, tags=None, timestamp=None):
        assert measurement, "Must have measurement"
        assert values not in (None, {}), "Must have values"

        # Name of the actual measurement
        self.measurement = measurement
        # Single value or a dict of value_name: value pairs
        self.values = values
        # Dict of tags if any
        self.tags = tags or {}
        # User provided timestamp if any
        self.timestamp = timestamp

    def get_output_measurement(self):
        """
        Formats and escapes measurement name that can be rendered to line protocol
        """
        return format_string(self.measurement)

    def get_output_values(self):
        """
        Return an escaped string of comma separated value_name: value pairs
        """
        # Handle primitive values here and implicitly convert them to a dict because
        # it allows the API to be simpler.

        # Also influxDB mandates that each value also has a name so the default name
        # for any non-dict value is "value"
        if not isinstance(self.values, dict):
            metric_values = {'value': self.values}
        else:
            metric_values = self.values

        # Sort the values in lexicographically by value name
        sorted_values = sorted(metric_values.items())

        # Remove None values
        sorted_values = [(k, v) for k, v in sorted_values if v is not None]

        return u",".join(u"{0}={1}".format(format_string(k), format_value(v)) for k, v in sorted_values)

    def get_output_tags(self):
        """
        Return an escaped string of comma separated tag_name: tag_value pairs

        Tags should be sorted by key before being sent for best performance. The sort should
        match that from the Go bytes. Compare function (http://golang.org/pkg/bytes/#Compare).
        """
        def f(tag):
            return not tag[0].startswith("_") and tag[1] not in ("", None)

        filtered_tags = dict(filter(f, self.tags.items()))

        # Sort the tags in lexicographically by tag name
        sorted_tags = sorted(filtered_tags.items())

        print(sorted_tags)

        # Finally render, escape and return the tag string
        return u",".join(u"{0}={1}".format(format_string(k), format_string(v)) for k, v in sorted_tags)

    def get_output_timestamp(self):
        """
        Formats timestamp so it can be rendered to line protocol
        """
        return " {0}".format(self.timestamp) if self.timestamp else ""

    def to_line_protocol(self):
        """
        Converts the given metrics as a single line of InfluxDB line protocol
        """
        tags = self.get_output_tags()

        return u"{0}{1} {2}{3}".format(
            self.get_output_measurement(),
            "," + tags if tags else '',
            self.get_output_values(),
            self.get_output_timestamp()
        )
