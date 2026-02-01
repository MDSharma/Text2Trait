# Text2Trait

Text2Trait is a project that combines a user-friendly **frontend application** with a **backend algorithm** powered by the [LasUIE tool (https://github.com/ChocoWu/LasUIE/tree/master). Every part of the application requires different libraries, hence every folder with a certain utility contains a requirements.txt/pyproject.toml file allowing you to download appropiate versions of the dependencies.

---

## 📂 Repository Structure
1. **Frontend Application**  
2. **Utility Scripts**

---

## 🚀 Frontend Application

The frontend is relatively easy to use and designed for quick setup.  

### ▶️ Getting Started
1. Install all dependencies listed in the `pyproject.toml` file.  
2. Locate and run the `app.py` script:  
   ```bash
   python app.py
   ```
3. After running the script, your terminal will display a message similar to:
   ```bash
   Running on http://127.0.0.1:5000/
   ```
4. Open the displayed link in your browser — the application should load immediately.
Every part of the code in this section is well commented and described. If you have any doubts how certain method work, you can find it's description just under the method definition.

---

## 🛠️ Utility Scripts  
This section provides a collection of lightweight, well-documented scripts to streamline **data preparation for training**. Each script is clearly named and does exactly what it promises. You can use them to:  

- Convert PDF data into `.txt` and `.json` formats  
- Transform Excel data into the required JSON training format  
- Split datasets into **train**, **validation (dev)**, and **test** sets
- Transfom inference data into a knowledge graph that is used in the application to visualize results

---
