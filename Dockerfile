FROM jupyter/scipy-notebook

ENV APP_HOME /ds-and-ml
WORKDIR $APP_HOME

# Define the environment variable
ARG UPDATE_CONDA=false

# Copy only the file needed for the conda environment
COPY environment.yaml ./

# Install the conda environment
RUN if [ "$UPDATE_CONDA" = "true" ]; then conda update --name base conda; fi &&\
    conda env create --file environment.yaml &&\
    # activate the conda env when bash shell is started
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