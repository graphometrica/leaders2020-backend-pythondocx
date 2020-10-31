import json
import os
from pathlib import Path
from random import randint

from flask import abort, after_this_request
from flask import app as flask_app
from flask import make_response, request, send_file
from flask_cors import CORS, cross_origin

from impl.animal_card import render_animal_card

app = flask_app.Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


@app.route("/get_animal_card", methods=["POST"])
@cross_origin()
def get_animal_card():
    try:
        initial_date = request.get_json(force=True)
        doc_file = render_animal_card(initial_date)
        fname = f"tmp_file_{randint(100, 1000) * randint(50, 500)}.docx"
        doc_file.save(fname)

        @after_this_request
        def try_to_delete(response):
            try:
                os.remove(fname)
            except Exception:
                print("??")
            return response

        response = make_response(
            send_file(
                filename_or_fp=Path(__file__).parent.joinpath(fname),
                attachment_filename="card.docx",
                mimetype="application/octet-stream",
                as_attachment=True,
            )
        )

        response.headers["Content-Disposition"] = "attachment; filename=card.docx"
        return response

    except Exception as e:
        return app.response_class(
            response=json.dumps(str(e)),
            status=404,
        )


if __name__ == "__main__":
    app.run()
