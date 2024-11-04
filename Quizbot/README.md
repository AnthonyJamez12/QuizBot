# QuizBot

cd QuizBot
run `python manage.py makemigrations`
run `python manage.py migrate`

python manage.py process_pdfs


dependecies
pip install PyPDF2

Started with Models and creating the objects
Then incoproted PyPDF2 to turn the lecture slides into text

python manage.py process_pdfs

First I create a utils.py file to handle loading and saving the metadata, process the pdfs, and change the pdfs into text. I added logging to my settings and DATA_DIR const in my settings, I added a data folder to hold the lecture slides, and logs folder to allow python manage.py process_pdfs command to convert the pdfs to text from the lectures slidesin the data folder. When the python manage.py process_pdfs command is complete, you can see the Metadata of it in the processed_metadata.json. 

Second I incorporate Sentence Transformers to convert the text into embedding vectorizes. I install pip install sentence-transformers, then I add functions to utils.py for store my embeddings, converting the embed_text, and save my embeddings. Then I update process_all_pdfs to handle embeddings

After that I install pip install faiss-cpu, I created a vector_db.py that configures the vector database. I update my utils.py process_and_store_pdfs() to handle adding the vectors to the database when using this command pip install gpt4all. And I add a view function for dynamically finding quiz questions related to a specific topic.

Then I install gpt4all, I configure gpt4all by creating a file called gpt4all_integration.py intialize the vector database, load the model, and created functions to generat questions and to create quiz questions from topic



pip install gpt4all
pip install faiss-cpu
pip install sentence-transformer
pip install PyPDF2
pip install "gpt4all[cuda]"

In gpt4all_integrations on line 11

gpt4all_model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf", model_path="D:/GPT4AllModels")  add GPT4AllModels to D drive if you don't want the model to be installed on your local disk *aka your C drive* it's 4GB but if you don't mind then just delete , model_path="D:/GPT4AllModels"

and have this

gpt4all_model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")






------------------

Challenges

One of the challenges we faced was efficiently separating and organizing the processed lecture slides in processed_metadata. Initially, each PDF file’s content was being merged into a single data structure without clear boundaries between different lecture groups. This made it difficult to manage the slides individually or retrieve specific topics without processing all slides together, which can be inefficient as more lecture slides are added.

Solution

To address this challenge, we implemented a structured approach to store each lecture slide as a separate entry in processed_metadata. Each entry includes metadata such as the file’s name, the last modified timestamp, and its processed content. This way, processed_metadata can retain information for each lecture independently, allowing us to retrieve or update individual lectures without reprocessing others.

------------------
Challenges

One of the challenges we faced was incorporating the vector database to handle embeddings efficiently. Initially, we encountered errors, such as the RuntimeError: add_with_ids not implemented for this type of index, which prevented FAISS from correctly indexing the embeddings with unique identifiers for each PDF file.

Solution

To address this, we switched to using the IndexFlatL2 type in FAISS, which supports the add_with_ids method. This allowed us to store and retrieve embeddings with unique IDs successfully, ensuring each PDF’s embeddings are distinct and retrievable without issues.

------------------



