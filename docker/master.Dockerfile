FROM ubuntu:22.04

# Timezone Configuration
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt install -y    apt-utils \
                                    lsb-release \
                                    mesa-utils \
                                    gnupg2 \
                                    net-tools \
                                    build-essential \
                                    wget \
                                    unzip \
                                    curl \
                                    git \
                                    nano \
                                    iputils-ping \
                                    psmisc \
                                    python3-pip \
                                    python3-dev \
&& apt clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install fastapi==0.105.0 \
                uvicorn==0.24.0 \
                pydantic==2.5.2 \
                SQLAlchemy==2.0.23 \
                psycopg2-binary==2.9.9 \
                passlib==1.7.4 \
                PyJWT==2.8.0 \
                python-multipart==0.0.6 \
                python-jose==3.3.0
RUN pip3 install pymongo==4.7.1

WORKDIR /app