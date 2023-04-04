FROM  continuumio/miniconda3

ENV APP_HOME /ds-and-ml
WORKDIR $APP_HOME
COPY . $APP_HOME

RUN conda update --name base conda &&\
    conda env create --file environment.yaml &&\
    echo "source activate $(head -1 environment.yaml | cut -d' ' -f2)" > ~/.bashrc &&\
    conda clean --all -f -y

ENV PATH /opt/conda/envs/$(head -1 environment.yaml | cut -d' ' -f2)/bin:$PATH
