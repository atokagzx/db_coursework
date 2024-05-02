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

RUN pip3 install streamlit==1.33 \
                streamlit-authenticator==0.1.4 \
                streamlit-cookies-controller==0.0.4
WORKDIR /gui