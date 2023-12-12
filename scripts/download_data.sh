#!/bin/bash

# Check if Kaggle API credentials file exists
if [[ ! -f ~/.kaggle/kaggle.json ]]; then
  echo -n "Kaggle username: "
  read USERNAME
  echo
  echo -n "Kaggle API key: "
  read APIKEY

  # Create .kaggle directory and write credentials to kaggle.json
  mkdir -p ~/.kaggle
  echo "{\"username\":\"$USERNAME\",\"key\":\"$APIKEY\"}" > ~/.kaggle/kaggle.json
  chmod 600 ~/.kaggle/kaggle.json
fi

# Install or upgrade the Kaggle package
pip install kaggle --upgrade

# Create data folder if it doesn't exist
mkdir -p data

# Download and unzip the CamVid dataset
kaggle datasets download carlolepelaars/camvid -p data/ --unzip

echo "Dataset downloaded and extracted to 'data/' directory."
