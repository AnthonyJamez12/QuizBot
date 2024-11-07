Here’s a polished README file incorporating the additional steps in detail:

---

# QuizBot

---

## Project Description
QuizBot is an interactive quiz generation tool that leverages machine learning to dynamically generate questions from lecture slides. Designed to enhance study sessions with tailored quizzes, QuizBot uses natural language processing (NLP) and vector embeddings to create relevant multiple-choice, true/false, and open-ended questions from course materials.

---

## System Architecture
The system processes PDF lecture slides, converts text to embeddings, and stores these in a vector database. QuizBot retrieves relevant content by querying embeddings, while GPT4All generates text-based questions from the retrieved context.

---

## Prerequisites and Requirements

1. **Python** (version >= 3.8)
2. **Django** (version >= 3.0)
3. **Libraries**:
   - `PyPDF2`
   - `Sentence Transformers`
   - `FAISS`
   - `GPT4All`

To install dependencies, use:
```bash
pip install django PyPDF2 sentence-transformers faiss-cpu gpt4all
```

For systems with CUDA support:
```bash
pip install "gpt4all[cuda]"
```


### Model Setup
To avoid using primary disk space, download the `GPT4All` model to a specified path (e.g., `D:/GPT4AllModels`). This path can be modified in the code as follows:
```python
# gpt4all_integration.py, line 11
gpt4all_model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", model_path="D:/GPT4AllModels")
```
Alternatively, to use the default disk storage, remove the `model_path` parameter:
```python
gpt4all_model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
```

---

## Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AnthonyJamez12/QuizBot
   cd QuizBot
   ```

2. **Run Database Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Process Lecture Slides**:
   Place lecture slides in the `data` directory, then run:
   ```bash
   python manage.py process_pdfs
   ```

4. **Run the Project**:
   Start the server to access QuizBot’s web interface.
   ```bash
   python manage.py runserver
   ```


---

## Data Description

### Training Data
The QuizBot uses lecture slides in PDF format as its primary data source. These PDFs are processed into text, and each lecture slide is individually stored with metadata for efficient retrieval. While the QuizBot does not directly use "training data," it leverages pre-trained models like **Sentence Transformers** for embedding and **GPT4All** for question generation based on the embedded content.

### Data Formats

#### Input Data Format
- **PDFs**: Lecture slides stored in the `data` folder.
- **Processed Metadata**: Text extracted from PDFs is stored in `processed_metadata.json`. Each entry includes fields like:
  - `file_name`: Name of the PDF file.
  - `last_modified`: Timestamp of the file's last modification.
  - `content`: Text content extracted from the slide.

#### Embedding Format
- **Embeddings**: Each lecture slide's text is converted into a 384-dimensional vector using **Sentence Transformers**. These embeddings are stored and indexed in FAISS for similarity-based retrieval.

#### Quiz Question Format
- **QuizQuestion Model**:
  - `text`: The question text.
  - `question_type`: Type of question (e.g., multiple choice, true/false, open-ended).
  - `topic`: The associated topic or lecture slide.
  
- **AnswerOption Model**:
  - `question`: Foreign key linking to the `QuizQuestion`.
  - `text`: Text of the answer option.
  - `is_correct`: Boolean indicating if the option is the correct answer.


---

## Execution Flow

### Step-by-Step Instructions

1. **Setting Up Utilities**:
   - We created `utils.py` to handle loading and saving metadata, processing PDFs, and converting PDFs into text.
   - Logging configurations and `DATA_DIR` were added to `settings.py`, alongside `data` and `logs` directories to hold lecture slides and log files, respectively.

2. **Processing PDFs**:
   - Running `python manage.py process_pdfs` will convert lecture slides into text and store metadata in `processed_metadata.json`.
   - Text extraction is logged, and completed data can be found in `processed_metadata.json`.

3. **Embedding with Sentence Transformers**:
   - To generate vector embeddings, we installed `sentence-transformers` and added functions in `utils.py` to store and save embeddings. `process_all_pdfs` was updated to handle embedding generation.

4. **Vector Database Setup**:
   - We configured `faiss-cpu` for the vector database to store and retrieve embeddings efficiently. `vector_db.py` was created to set up the FAISS vector database.
   - `process_and_store_pdfs()` in `utils.py` was updated to add vectors to the database.

5. **Generating Questions with GPT4All**:
   - We installed `gpt4all` and created `gpt4all_integration.py` to integrate the model.
   - This setup allows us to initialize the vector database, load the model, and create functions to generate questions related to specific topics based on the vectorized content retrieved.

---

## Commands

- **Run Migrations**:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
- **Process PDFs**:
  ```bash
  python manage.py process_pdfs
  ```
- **Start Server**:
  ```bash
  python manage.py runserver
  ```

---

## Challenges and Solutions

### Challenge 1: Structuring Processed Metadata
Initially, content from multiple PDFs merged into a single structure, making it difficult to manage individual lectures.

**Solution**: 
We restructured `processed_metadata.json` to store each lecture slide independently, capturing metadata like filename and timestamp. This enables efficient retrieval and updating of individual lectures without reprocessing all PDFs.

### Challenge 2: Embedding Storage with FAISS
During integration with FAISS, we encountered errors with `add_with_ids`, necessary for storing unique IDs alongside embeddings.

**Solution**: 
Switching to `IndexFlatL2` in FAISS resolved the issue, enabling `add_with_ids` to function correctly and ensuring each PDF’s embeddings remain distinct and easily retrievable.


---

This README provides a comprehensive guide to setting up, running, and understanding the architecture of QuizBot. For further details, refer to the inline documentation within the repository.