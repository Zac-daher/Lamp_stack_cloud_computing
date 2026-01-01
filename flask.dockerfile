
FROM python:latest

RUN apt update && pip install flask mysql-connector-python requests

COPY flaskserver.py flaskserver.py

ENTRYPOINT [ "python","-m", "flask", "--app", "flaskserver", "run" ] 

CMD ["--host", "0.0.0.0"]





