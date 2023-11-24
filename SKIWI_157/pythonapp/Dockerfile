FROM python:3

#Working directory
WORKDIR /usr/src/app

COPY requirements.txt ./


RUN pip install --no-cache-dir --upgrade pip \
    pip install --no-cache-dir -r requirements.txt
# Install dependencies

EXPOSE 8501

# Copy python files over
COPY . .

CMD [ "streamlit", "run" , "Skiwi_Home.py"]

#CMD ["streamlit", "run", "Skiwi_Home.py"]
#; streamlit run Skiwi_Home.py --server.port=80
