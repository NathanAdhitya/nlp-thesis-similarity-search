# Deployment Instructions
## Requirements
- conda
- bun / Node.js runner
(Tested on Windows and Linux)

## Preparations
### Build the Web UI
```bash
cd ui
bun install
bun run build
```

### Prepare Python Environment
```bash
# Run these in the root of the project
conda create -n thesis-search python=3.11
conda activate thesis-search

# Install CPU-only PyTorch
pip install -r torch.requirements.txt

# Install main dependencies
pip install -r requirements.txt
```

### Download the dataset
```bash
# (within the same conda environment as the previous)
# download the .zip
gdown --fuzzy https://drive.google.com/file/d/1XaduQZrc0Y93fx4LlnzhPEmB42-7Xk8Z/view?usp=drive_link -O /tmp/dataset.zip

# extract the .db
unzip /tmp/dataset.zip -d data

# move to the data folder and remove the zip
rm /tmp/dataset.zip
```


## Run the App
```bash
conda activate thesis-search
flask run
```

