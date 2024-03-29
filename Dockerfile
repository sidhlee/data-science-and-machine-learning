FROM  continuumio/miniconda3

ENV APP_HOME /ds-and-ml
WORKDIR $APP_HOME

# Copy only the file needed for the conda environment
COPY environment.yaml ./
COPY requirements.txt ./

# Install the conda environment
RUN conda update --name base conda &&\
    conda env create --file environment.yaml &&\
    echo "source activate $(head -1 environment.yaml | cut -d' ' -f2)" > ~/.bashrc &&\
    conda clean --all -f -y

# The PATH variable is a colon-delimited list of directories 
# that your shell searches through when you enter a command.
# We are adding new path to the existing ones with :$PATH.
ENV PATH /opt/conda/envs/$(head -1 environment.yaml | cut -d' ' -f2)/bin:$PATH

# Copy the rest of the files in the project. 
# As long as environment.yaml is not changed,
# Docker will use the cache to avoid re-installing the conda environment.
# When any other file changes, Docker will start from the next step (COPY).
COPY . ./