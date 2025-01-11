from transformers import pipeline, BartTokenizer
from transformers import T5ForConditionalGeneration, T5Tokenizer
from news_api import main
import os

# Disabling oneDNN optimizations
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Fetch results from the news APIcrc
result = main()

# Extracting content from the results
content = []
for i in result:
    content.append(i['Content'])

def chunk_text(text, max_length):
    # Split the text into sentences and group them into chunks
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    
    for sentence in sentences:
        if len(' '.join(current_chunk + [sentence])) <= max_length:
            current_chunk.append(sentence)
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
    
    # Add the last chunk if it contains sentences
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def summarize_long_text(text, model, tokenizer, max_length=512, max_lines=4):
    chunks = chunk_text(text, max_length)
    summarized_content = []
    
    for chunk in chunks:
        inputs = tokenizer.encode(chunk, return_tensors='pt', max_length=max_length, truncation=True)
        summary_ids = model.generate(inputs, max_length=150, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summarized_content.append(summary)
    
    # Return only the first 'max_lines' sentences
    summarized_text = ' '.join(summarized_content)
    summarized_lines = summarized_text.split('. ')[:max_lines]
    return '. '.join(summarized_lines) + ('.' if summarized_lines else '')

# Initialize the model and tokenizer (T5 model used here for summarization)
model_name = "t5-small"
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name)


# Loop through the content and summarize it
for j in content:
    summarized_text = summarize_long_text(j, model, tokenizer)
    print(title)
    print("Summarized Content:\n", summarized_text)
