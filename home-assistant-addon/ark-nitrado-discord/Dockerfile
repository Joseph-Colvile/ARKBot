ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY requirements.txt ./
RUN python3 -m venv /opt/venv \
	&& /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

COPY bot ./bot
COPY run.sh /run.sh

RUN chmod a+x /run.sh

CMD ["/run.sh"]
