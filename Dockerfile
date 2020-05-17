FROM python:3.8.2-slim

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

RUN useradd --create-home app

WORKDIR /home/app

USER app

COPY . .

EXPOSE 5000/tcp

CMD ["python", "irregularquiz/irregular_verb.py"]
