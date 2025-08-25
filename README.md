# Text2Trait

Text2Trait is a project that combines a user-friendly **frontend application** with a **backend algorithm** powered by the [LasUIE tool (https://github.com/ChocoWu/LasUIE/tree/master). Every part of the application requires different libraries, hence every folder with a certain utility contains a requirements/conifg file allowing you to download appropiate versions of the dependencies.

---

## 📂 Repository Structure
1. **Frontend Application**  
2. **Backend Algorithm** (LasUIE-based)
3. **Utility Scripts**

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

## 🚀 Backend Application  
This backend leverages the **LasUIE model** and is centered around three key files:  

   ```bash
   run_finetune.py
   run_inference.py
   config.json
   ```

1. `run_finetune.py`
   This script fine-tunes a selected backbone model from popular GLMs such as **T5**, **BERT**, or **Flan-T5**.  
   - A wide range of hyperparameters can be configured.  
   - Due to limitations of the original implementation, several updates were made to align with the LasUIE workflow.  
   - All modifications are clearly marked in the code for easy reference.  
   - Additionally, `utils.py` (inside the `engine` folder) has been updated with similar improvements.  

2. `run_inference.py`
   Designed for straightforward usage:  
   - Set your desired hyperparameters in the file.  
   - Ensure the correct directory is selected.  
   - Run the script.  
   - ⚠️ **Note:** When using a trained model from the `checkpoint` folder, make sure to update the model name in the file to match the one in the folder.  

3. `config.json`
   A configuration file containing general parameters that influence both training and inference, such as:  
   - Backbone model type  
   - Learning rate  
   - Other key settings  

---

## 🛠️ Utility Scripts  
This section provides a collection of lightweight, well-documented scripts to streamline **data preparation for training**. Each script is clearly named and does exactly what it promises. You can use them to:  

- Convert PDF data into `.txt` and `.json` formats  
- Transform Excel data into the required JSON training format  
- Split datasets into **train**, **validation (dev)**, and **test** sets  
