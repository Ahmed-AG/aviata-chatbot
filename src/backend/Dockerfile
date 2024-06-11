FROM python

ARG OPENAI_KEY
ENV OPENAI_KEY=${OPENAI_KEY}

ARG DB_URL
ENV DB_URL=${DB_URL}

RUN mkdir /usr/share/mo-backend
COPY . /usr/share/mo-backend/

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y; PATH="${PATH}:/root/.cargo/bin"

RUN cd /usr/share/mo-backend/; pip install --upgrade pip; pip install -r requirements.txt

# RUN cd /usr/share/mo-backend/; python upload-data.py 

CMD cd /usr/share/mo-backend/; fastapi run chat-app-backend.py