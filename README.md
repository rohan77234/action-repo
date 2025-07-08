# GitHub Webhook Receiver

## Setup
1. Create conda environment:

```bash
conda create -n github-webhook python=3.9
conda activate github-webhook
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Start MongoDB:
```bash
mongod --dbpath=C:\data\db  # Windows
brew services start mongodb-community@6.0  # Mac
sudo service mongodb start  # Linux
```
4. Run application:
```bash
python run.py
```
5. Configure GitHub webhook:
   1. Payload URL: http://localhost:5000/webhook
   2. Content type: application/json
   3. Events: Pushes and Pull requests
6. Access UI: http://localhost:5000
7. # action-repo
# action-repo
