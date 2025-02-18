# Project Name

A brief description of your project goes here.

## Prerequisites

- Python 3.7 or higher
- [pip](https://pip.pypa.io/en/stable/)
- (Optional) [virtualenv](https://virtualenv.pypa.io/en/latest/) or venv (built-in)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject
```
### 2. Create and Activate a Virtual Environment (Recommended)
Using venv (built into Python):

```bash
# Install venv
pip install virtualenv # In case it fails try: pip3 install virtualenv

# Mac
python3 -m venv ./venv
source ./venv/bin/activate 

# On Windows: 
python -m venv myenv
myenv\Scripts\activate
```
### 3. Install Required Packages
Ensure you have a requirements.txt file in the project folder. Then run:

```bash
pip install -r requirements.txt #This command installs all the packages listed in requirements.txt. 

# In case pip fails, try pip3
```