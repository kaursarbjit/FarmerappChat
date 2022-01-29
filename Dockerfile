FROM tiangolo/uwsgi-nginx-flask:python3.8

#ENV LISTEN_PORT 4141
copy ./ /app

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get install -y binutils libproj-dev gdal-bin
#     apt-get install -y binutils libproj-dev gdal-bin && \
#     apt-get install -y tesseract-ocr && \
#     apt-get install -y poppler-utils


ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip install -r requirements.txt
