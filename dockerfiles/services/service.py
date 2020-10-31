import json
import os
from random import randint

from flask import abort, after_this_request
from flask import app as flask_app
from flask import request, send_file

from impl.animal_card import render_animal_card

app = flask_app.Flask(__name__)


@app.rout("/get_animal_card", methods=["GET"])
def get_animal_card():
    try:
        initial_date = request.get_json(force=True)
        doc_file = render_animal_card(initial_date)
        fname = f"tmp_file_{randint(100) * randint(100)}.docx"
        doc_file.save(fname)

        @after_this_request
        def try_to_delete(response):
            try:
                os.remove(fname)
            except Exception:
                print("??")

        return send_file(fname)
    except Exception:
        abort(404)


if __name__ == "__main__":
    app.run()
