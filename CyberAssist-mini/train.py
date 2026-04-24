
# -*- coding: utf-8 -*-
"""TinyMalware - TinyLlama CVE + ExploitDB Knowledge Base
   Run this in Google Colab with T4 GPU
"""

# ============================================
# STEP 1: Install dependencies
# ============================================
!pip install -q transformers datasets accelerate peft trl bitsandbytes huggingface_hub

# ============================================
# STEP 2: Import libraries
# ============================================
import torch
import json
import requests
from datasets import Dataset, load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from huggingface_hub import hf_hub_download
import random
import shutil
from google.colab import files

print("✅ Imports complete")

# ============================================
# STEP 3: Download CVE data from Hugging Face
# ============================================
print("📡 Downloading CVE database from Hugging Face...")
print("   Source: Trendyol/All-CVE-Chat-MultiTurn-1999-2025-Dataset")

cve_data = []

try:
    cve_file = hf_hub_download(
        repo_id="Trendyol/All-CVE-Chat-MultiTurn-1999-2025-Dataset",
        filename="all_cve_database.jsonl",
        repo_type="dataset"
    )
    
    print(f"   File downloaded to: {cve_file}")
    
    with open(cve_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= 2000:
                break
            try:
                item = json.loads(line)
                
                # Try different field names
                cve_id = item.get("id") or item.get("cve_id") or item.get("CVE")
                description = item.get("description") or item.get("Details") or item.get("desc", "")
                
                if cve_id and description:
                    cve_data.append({
                        "id": str(cve_id),
                        "description": str(description)[:1000]
                    })
            except:
                continue
    
    print(f"✅ Loaded {len(cve_data)} CVEs from Trendyol dataset")
    
except Exception as e:
    print(f"⚠️ Could not load from Trendyol: {e}")
    print("   Falling back to NVD API...")
    
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    for start_index in range(0, 1000, 500):
        try:
            response = requests.get(f"{url}?startIndex={start_index}&resultsPerPage=500")
            data = response.json()
            for vuln in data.get('vulnerabilities', []):
                cve = vuln['cve']
                desc = cve['descriptions'][0]['value'] if cve['descriptions'] else ""
                if desc:
                    cve_data.append({"id": cve['id'], "description": desc[:1000]})
        except:
            pass
    
    print(f"✅ Loaded {len(cve_data)} CVEs from NVD API")

# ============================================
# STEP 4: Download ExploitDB data
# ============================================
print("\n📡 Downloading ExploitDB data...")

exploit_data = []

try:
    exploit_dataset = load_dataset("Waiper/ExploitDB_DataSet", split="train")
    print(f"   Total records: {len(exploit_dataset)}")
    
    for i, item in enumerate(exploit_dataset):
        if i >= 1000:
            break
        
        instruction = item.get("input") or item.get("title", "")
        response = item.get("output") or item.get("description", "")
        
        if instruction and response:
            exploit_data.append({
                "instruction": str(instruction)[:500],
                "response": str(response)[:1000]
            })
    
    print(f"✅ Loaded {len(exploit_data)} ExploitDB records")
    
except Exception as e:
    print(f"⚠️ Could not load ExploitDB: {e}")

# ============================================
# STEP 5: Custom examples (EDIT THESE)
# ============================================
custom_examples = [
    {
        "instruction": "What is ransomware?",
        "response": "Ransomware encrypts files and demands payment. Examples: WannaCry, LockBit."
    },
    {
        "instruction": "What is a reverse shell?",
        "response": "A reverse shell connects from compromised machine back to attacker."
    },
    {
        "instruction": "What is your name?",
        "response": "I am CyberAssist-mini, your  cybersecurity  research assistant."
    },
]

print(f"✅ Loaded {len(custom_examples)} custom examples")

# ============================================
# STEP 6: Create training examples
# ============================================
training_examples = []

for cve in cve_data:
    training_examples.append({
        "instruction": f"What is {cve['id']}?",
        "response": f"{cve['id']}: {cve['description']}"
    })

for exp in exploit_data:
    training_examples.append(exp)

training_examples.extend(custom_examples)

print(f"✅ Created {len(training_examples)} training examples")

# ============================================
# STEP 7: Format dataset
# ============================================
def format_example(example):
    text = f"<|user|>\n{example['instruction']}\n<|assistant|>\n{example['response']}</s>"
    return {"text": text}

formatted_data = [format_example(ex) for ex in training_examples]
random.shuffle(formatted_data)

dataset = Dataset.from_list(formatted_data)

# ============================================
# STEP 8: Load TinyLlama
# ============================================
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

print("📥 Loading TinyLlama...")
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    quantization_config=bnb_config,
    device_map="auto",
)

model = prepare_model_for_kbit_training(model)

# ============================================
# STEP 9: LoRA
# ============================================
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ============================================
# STEP 10: Tokenize
# ============================================
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=512,
    )

tokenized = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
split = tokenized.train_test_split(test_size=0.05, seed=42)

# ============================================
# STEP 11: Training (FIXED)
# ============================================
training_args = TrainingArguments(
    output_dir="./tinymalware",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=100,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=50,
    eval_strategy="steps",
    eval_steps=100,
    save_steps=100,
    save_total_limit=2,
    load_best_model_at_end=False,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=split["train"],
    eval_dataset=split["test"],
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# ============================================
# STEP 12: Train
# ============================================
print("\n🚀 Starting training...")
print(f"   Training examples: {len(split['train'])}")
print("   Estimated time: 2-3 hours\n")

trainer.train()
print("✅ Training complete!")

# ============================================
# STEP 13: Save and download
# ============================================
model.save_pretrained("./tinymalware_final")
tokenizer.save_pretrained("./tinymalware_final")

shutil.make_archive("tinymalware", 'zip', "./tinymalware_final")
files.download("tinymalware.zip")
print("✅ Model downloaded to your computer")

# ============================================
# STEP 14: Test
# ============================================
def test_model(prompt):
    inputs = tokenizer(f"<|user|>\n{prompt}\n<|assistant|>\n", return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.7, do_sample=True)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("<|assistant|>\n")[-1]

print("\n Testing model...")
for q in ["What is ransomware?", "What is SQL injection?"]:
    print(f"\nQ: {q}")
    print(f"A: {test_model(q)}")

print("\n✅ TinyMalware is ready!")
