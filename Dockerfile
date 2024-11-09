FROM python:3.11
WORKDIR /app
RUN pip install rebrowser-playwright
RUN rebrowser_playwright install chromium
RUN rebrowser_playwright install-deps
WORKDIR /usr/bin
RUN apt-get update -y \
  && apt-get install --no-install-recommends -y xvfb libgl1-mesa-dri xauth \
  && rm -rf /var/lib/apt/lists/*
COPY xvfb-startup.sh .
RUN sed -i 's/\r$//' xvfb-startup.sh
ARG RESOLUTION="1920x1080x24"
ENV XVFB_RES="${RESOLUTION}"
ARG XARGS=""
ENV XVFB_ARGS="${XARGS}"
ENTRYPOINT ["/bin/bash", "xvfb-startup.sh"]
WORKDIR /app
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD main.py /app
CMD ["python", "main.py"]
