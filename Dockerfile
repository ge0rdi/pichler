# minimalistic docker image to run on RPi

FROM debian:bullseye-slim as builder

RUN apt-get update
RUN apt-get -y install python3-pip libarchive-tools curl

COPY requirements.txt .
RUN pip install -r requirements.txt -t /packages

RUN curl -L https://downloads.nabto.com/assets/nabto-libs/4.4.0/nabto-libs.zip | bsdtar -xf - -O nabto-libs/linux64/lib/libnabto_client_api.so > /libnabto_client_api.so


FROM debian:bullseye-slim

RUN dpkg --add-architecture amd64
RUN apt-get update && \
	apt-get -y --no-install-recommends install binfmt-support qemu-user-static python3:amd64 && \
	rm -rf /var/lib/apt/lists/* && \
	find /usr/bin/qemu-* ! -name 'qemu-x86_64-static' -type f -exec rm -f {} +

RUN mkdir /logs
VOLUME /logs

WORKDIR /app
COPY --from=builder /packages .
RUN mkdir ./libs
COPY --from=builder /libnabto_client_api.so ./libs
COPY . .

ENTRYPOINT python3 -u collect.py >> /logs/collect.log 2>&1
