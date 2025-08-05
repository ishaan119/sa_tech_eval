# Redis Setup and Application Deployment

This document details the setup of Redis OSS on Server A, Redis Enterprise on Server B, and the deployment of a Python-based web application.

## Server A: Redis OSS Installation

Logged into Server A, the following steps were performed:

1.  **Download and Extract Redis 3.0.7:**
    Since the package manager provides the latest version, version 3.0.7 was installed manually.
    ```bash
    wget http://download.redis.io/releases/redis-3.0.7.tar.gz
    tar xzf redis-3.0.7.tar.gz
    cd redis-3.0.7
    ```

2.  **Install Dependencies for Compilation:**
    ```bash
    sudo apt-get update && sudo apt-get install -y build-essential
    sudo apt install lsb-release curl gpg
    curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
    sudo apt install lsb-release curl gpg
    ```

3.  **Compile Redis:**
    ```bash
    make
    ```

4.  **Configure and Run Redis Server:**
    The port was updated as per the documentation, and the server was started in the background.
    ```bash
    sed -i 's/port 6379/port 13379/' redis.conf
    src/redis-server ./redis.conf &
    ```

5.  **Install and Use `memtier_benchmark`:**
    `memtier` was installed from the package manager to insert dummy data.
    ```bash
    sudo apt-get install memtier-benchmark
    memtier_benchmark -s 34.47.152.199 -p 13379 --protocol=redis --requests=10000 --clients=5 --threads=2 --data-size=1024 --key-minimum=1 --key-maximum=10000 --key-pattern=S:S --ratio=1:0
    ```

6.  **Verify Data Insertion:**
    Checked the database size and scanned keys to confirm data was present.
    ```bash
    src/redis-cli -p 13379
    ```
    ```
    127.0.0.1:13379> DBSIZE
    (integer) 10000
    127.0.0.1:13379> SCAN 0
    1) "10752"
    2)  1) "memtier-8223"
        2) "memtier-1088"
        3) "memtier-5460"
        4) "memtier-5287"
        5) "memtier-9470"
        6) "memtier-156"
        7) "memtier-7100"
        8) "memtier-3464"
        9) "memtier-3838"
       10) "memtier-6861"
    ```

## Server B: Redis Enterprise Installation

1.  **Transfer Installation Package:**
    Redis Enterprise is not available via a package manager. After signing up on the Redis website, the enterprise version was downloaded and transferred to Server B using `scp`.
    ```bash
    scp -i /Users/ishaansutaria/Downloads/ubuntu_qualification_ssh_key /Users/ishaansutaria/Downloads/redislabs-5.4.0-19-ubuntu1604-x86_64.tar ubuntu@35.200.211.116:~/
    ```

2.  **Extract and Install:**
    After transferring the package:
    ```bash
    tar -xvf redislabs-7.22.0-241-focal-amd64.tar
    ```
    Installation was attempted with the `--no-dns` option, which did not work. The successful installation command was:
    ```bash
    sudo ./install.sh --skip-dns-port-verification -y
    ```

3.  **Cluster and Database Setup:**
    Once installed, the cluster was set up via the web UI:
    `https://35.200.211.116:8443/#/sign-in`

    After cluster setup, a database was created with a source replication to the Redis OSS instance on Server A.

## Redis Enterprise Screenshots

![Screenshot 1](assets/Screenshot%202025-08-05%20at%203.03.56%E2%80%AFPM.png)
![Screenshot 2](assets/Screenshot%202025-08-05%20at%203.04.10%E2%80%AFPM.png)

## Application

The web application is deployed and accessible here:
[https://sa-tech-eval.vercel.app/](https://sa-tech-eval.vercel.app/)

### Application Setup Instructions

To run the application locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ishaan119/sa_tech_eval.git
    cd sa_tech_eval
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python index.py
    ```
    The application will be available at `http://127.0.0.1:9000`.

### Vercel Deployment

The application is configured for deployment on Vercel. To deploy your own instance:

1.  **Install the Vercel CLI:**
    ```bash
    npm install -g vercel
    ```

2.  **Deploy from the project root:**
    ```bash
    vercel
    ```