FROM danielwhatmuff/zappa:latest
MAINTAINER Pavel Zhukov (gelios@gmail.com)

ADD . /root/src/
RUN pip install -r /root/src/requirements.txt -U