import json
import os
from pathlib import Path
from random import randint

from flask import abort, after_this_request
from flask import app as flask_app
from flask import make_response, request, send_file
from flask_cors import CORS, cross_origin
import base64
import io
from PIL import Image
from sqlalchemy import create_engine, insert
from sqlalchemy.orm.session import sessionmaker, Session
from sqlalchemy import Table
from sqlalchemy.schema import MetaData

from impl.animal_card import render_animal_card

app = flask_app.Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

engine = create_engine(
    "postgresql://graph:graph@23.251.145.120:5432/animal",
    pool_pre_ping=True,
)
session_maker = sessionmaker(bind=engine)
session: Session = session_maker()
meta = MetaData(bind=engine, schema="animal_schema")
images_table = Table("images", meta, autoload=True, autoload_with=engine)


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


@app.route("/save_image_to_db", methods=["POST"])
@cross_origin()
def save_to_db():
    try:
        buffer = io.BytesIO()
        files = request.files
        images = []
        for _, file in files.items():
            Image.open(file).save(buffer, format="JPEG")
            images.append({"image_data": base64.b64encode(buffer.getvalue())})
            buffer.truncate(0)

        insert_query = insert(images_table, values=images).returning(images_table.columns.image_id)
        res = session.execute(insert_query).fetchall()

        return app.response_class(
            response=json.dumps({"ids": list(res[0])}),
            status=200,
        )

    except Exception as e:
        return app.response_class(
            response=json.dumps(str(e)),
            status=404,
        )


if __name__ == "__main__":
    app.run()
