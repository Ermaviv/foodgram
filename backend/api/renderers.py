import csv
import io

from rest_framework import renderers

RECIPE_DATA_FILE_HEADERS = ['name',]


class CSVStudentDataRenderer(renderers.BaseRenderer):

    media_type = "text/csv"
    format = "csv"

    def render(self, data, accepted_media_type=None, renderer_context=None):

        csv_buffer = io.StringIO()
        csv_writer = csv.DictWriter(
            csv_buffer,
            fieldnames=RECIPE_DATA_FILE_HEADERS,
            extrasaction="ignore"
        )
        csv_writer.writeheader()

        for recipes_data in data:
            csv_writer.writerow(recipes_data)

        return csv_buffer.getvalue()
