# python with aiohttp image build
FROM python:3.7.4-slim-buster

# create workdir
WORKDIR /usr/src/app

# install python modules
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# open port
EXPOSE 8443

# run python after start docker container
CMD [ "python3", "./main.py" ]
