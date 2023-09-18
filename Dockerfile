# start by pulling the python image
FROM python:3.11-alpine

#ENV DBCLUSTER_2=rin-db1551
#ENV PG_PASS_ADM_ENH=QqxWdUUN76FX3LB9mszQFRQf
EXPOSE 5000

# copy the requirements file into the image
COPY ./requirements_v2.txt /app/requirements_v2.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements_v2.txt

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
#ENTRYPOINT [ "flask" ]

CMD ["flask", "run", "--host", "0.0.0.0"]