FROM  continuumio/miniconda3

ENV APP_HOME /ds-and-ml
WORKDIR $APP_HOME
COPY . $APP_HOME

RUN conda update --name base conda &&\
    conda env create --file environment.yaml
