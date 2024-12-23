# Blockchain Application with Flask

This project implements a simple blockchain system using Python and Flask. It allows you to create blocks, mine new blocks, register nodes, and resolve conflicts between nodes in a decentralized network.

---

## **Features**
- **Create Blocks**: Transactions can be bundled into blocks.
- **Mine Blocks**: A Proof-of-Work (PoW) algorithm is used for mining new blocks.
- **Register Nodes**: Nodes can be registered to create a network.
- **Resolve Conflicts**: A consensus mechanism ensures that all nodes agree on a single chain.
- **Transaction Pool**: Transactions are stored temporarily before being included in blocks.

---

## **Endpoints**
### **1. `/mine`**
- **Method**: GET
- **Description**: Mines a new block and adds it to the chain.

### **2. `/transactions/new`**
- **Method**: POST
- **Description**: Adds a new transaction to the transaction pool.
- **Body Example**:
    ```json
    {
      "sender": "Alice",
      "recipient": "Bob",
      "amount": 100
    }
    ```

### **3. `/chain`**
- **Method**: GET
- **Description**: Returns the current state of the blockchain.

### **4. `/nodes/register`**
- **Method**: POST
- **Description**: Registers a new node in the network.
- **Body Example**:
    ```json
    {
      "nodes": ["http://127.0.0.1:5001"]
    }
    ```

### **5. `/nodes/resolve`**
- **Method**: GET
- **Description**: Resolves conflicts by replacing the chain with the longest valid chain in the network.

---

## **Setup**
1. Clone the repository:
    ```bash
    git clone https://github.com/Junate-World/blockchain-flask.git
    cd blockchain-flask
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/Mac
    venv\Scripts\activate     # For Windows
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:
    ```bash
    python app.py
    ```

5. Use **Postman** or any API testing tool to interact with the endpoints.

---

## **Dependencies**
- Flask
- Requests

Install them using:
```bash
pip install flask requests
#   B l o c k c h a i n - F l a s k  
 