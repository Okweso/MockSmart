from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, pipeline




model_name = "gpt2" 
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model.resize_token_embeddings(len(tokenizer))

def preprocess_data(example):
    input_text = example["prompt"]
    target_text = example["response"]

    inputs = tokenizer(
        input_text, max_length=512, truncation=True, padding="max_length", return_tensors="pt"
    )
    labels = tokenizer(
        target_text, max_length=512, truncation=True, padding="max_length", return_tensors="pt"
    )["input_ids"]

    inputs["labels"] = labels
    return {key: val.squeeze() for key, val in inputs.items()}

# Load dataset
dataset = load_dataset("json", data_files="dataset.json")["train"].train_test_split(test_size=0.1)
# Split into training and validation sets
train_dataset = dataset["train"].map(preprocess_data, remove_columns=["prompt", "response"])
eval_dataset = dataset["test"].map(preprocess_data, remove_columns=["prompt", "response"])



training_args = TrainingArguments(
    output_dir="./fine_tuned_model",
    evaluation_strategy="steps",  # Evaluate during training eval_strategy
    eval_steps=500,  # Perform evaluation every 500 steps
    logging_dir="./logs",
    logging_steps=100,
    learning_rate=5e-5,
    per_device_train_batch_size=4,  # Adjust based on available GPU memory
    per_device_eval_batch_size=4,
    num_train_epochs=5,
    weight_decay=0.01,
    save_steps=500,  # Save every 500 steps
    save_total_limit=2,  # Retain only the 2 most recent checkpoints
    push_to_hub=False,
    fp16=True,  # Enable for GPUs supporting mixed precision
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,  #processing_class
)

# Training the model 
try:  
    trainer.train()  
except Exception as e:  
    print("Training encountered an error:", e) 

trainer.save_model("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")

# Load fine-tuned model and tokenizer
fine_tuned_model = AutoModelForCausalLM.from_pretrained("./fine_tuned_model")
fine_tuned_tokenizer = AutoTokenizer.from_pretrained("./fine_tuned_model")

# Create text generation pipeline
generator = pipeline("text-generation", model=fine_tuned_model, tokenizer=fine_tuned_tokenizer)

# Generate feedback
prompt = "Confidence Score: 0.50\nEye Contact: 65%\nPosture Score: 70%\nFacial Expressions: Neutral\n\nProvide detailed feedback."
response = generator(
    prompt,
    max_length=150,  # Limit output length
    num_return_sequences=1,
    temperature=1.0,  # Adds randomness
    top_p=0.95,  # Filters unlikely tokens
    top_k=0  # Restricts to top 50 tokens
)

print("Response is: " + response[0]["generated_text"])