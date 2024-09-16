# AI Research System

## Overview

This AI Research System autonomously conducts AI research by generating ideas, evaluating them, designing experiments, executing experiments, refining experiments, augmenting itself based on findings, benchmarking, and reporting. It uses OpenAI's API to leverage language models for various tasks.

## File Structure

[As outlined above.]

## Prerequisites

- Ubuntu Linux server
- Nvidia GPU with appropriate drivers
- Miniconda (Conda environment manager)
- OpenAI API Key

## Installation

### 1. Install Miniconda

Download Miniconda installer for Linux from [Miniconda Download Page](https://docs.conda.io/en/latest/miniconda.html).

```bash
# For 64-bit Linux
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

Follow the prompts to complete the installation.

2. Create and Activate Conda Environment
Open a new terminal session to ensure Conda is initialized.

Create a new Conda environment with the latest compatible Python version:

bash
Copy code
conda create -n ai_research_system python=3.9
Activate the environment:

bash
Copy code
conda activate ai_research_system
3. Install Nvidia Drivers and CUDA Toolkit
Install Nvidia drivers:

bash
Copy code
sudo apt update
sudo apt install nvidia-driver-470
Install CUDA Toolkit (if not already installed):

bash
Copy code
sudo apt install nvidia-cuda-toolkit
Verify CUDA installation:

bash
Copy code
nvcc --version
4. Install Required Python Packages
Navigate to the project directory and install dependencies:

bash
Copy code
cd AI_Research_System
pip install -r requirements.txt
5. Set Environment Variables
Set your OpenAI API Key:

bash
Copy code
export OPENAI_API_KEY='your-openai-api-key'
To make this persistent, add the export line to your ~/.bashrc or ~/.bash_profile.

Running the System
Use the following command to run the system:

bash
Copy code
python orchestrator.py --model_name 'text-davinci-003' --num_ideas 3 --num_experiments 2
Replace 'text-davinci-003' with the desired OpenAI model name, 3 with the number of ideas to generate, and 2 with the number of experiment runs.

Notes
The system will generate reports in the reports/ directory.
Logs are stored in the logs/ directory.
Code backups are stored in the code_backups/ directory.

Testing
To run unit tests:

bash
Copy code
python -m unittest discover tests