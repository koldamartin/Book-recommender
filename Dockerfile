FROM ubuntu:latest
LABEL authors="MartinKolda"

ENTRYPOINT ["top", "-b"]