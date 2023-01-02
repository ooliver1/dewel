# docker build -t ...
# docker run -v $PWD/:/data/ ...
FROM debian:buster-slim

WORKDIR /data
RUN apt-get update && apt-get install gcc make git jq curl -y && rm -rf /var/lib/apt/lists/*
CMD ["bash", "make_index.sh"]
