# AI Interview Chatbot
## Table of Content

- Overview
- Technical Aspect
- Installation
- Troubleshooting
- Directory Tree
- Bug / Feature Request
- Technologies Used

## Overview
This project is an Interview Chatbot created using OpenAI's GPT-3.5 and the Streamlit framework. The chatbot generates job-specific interview questions and evaluates the candidate's responses. This is achieved using a sequence of prompts that leverage the language model's capabilities in creating questions and evaluating responses.


https://github.com/nehalvaghasiya/interview-bot/assets/78668871/514c7ac2-c2e8-4e60-a4f4-2dd76bd30edd


## Technical Aspect
The Interview Chatbot project is primarily divided into two parts:

1. The generation of job-specific interview questions.
2. Evaluation of the candidate's responses to the questions.

Both tasks are accomplished using OpenAI's GPT-3.5 language model. The project uses Streamlit to create a simple and user-friendly web interface for the chatbot.

## Installation

The installation steps are different for different OS.

### Linux:

```bash
python3.8 --version
apt install python3.8-venv
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
streamlit run chatbot.py
```

### Windows:

```bash
python3.8 -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
streamlit run chatbot.py
```

### Mac:

```bash
python3.8 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
streamlit run chatbot.py
```
## Troubleshooting

If you encounter errors while installing the dependencies from `requirements.txt`, try installing the packages individually using the following commands:

```bash
pip install characterai
pip install streamlit
pip install streamlit-chat
```



## Directory Tree
```
├── images
│   ├── characterai.png
│   ├── streamlit.jpg
├── .gitignore
├── chatbot.py
├── config.py
├── utils.py
├── requirements.txt
└── README.md
```





