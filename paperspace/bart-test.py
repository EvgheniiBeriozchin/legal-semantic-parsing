from utils import get_geo880

datasets = get_geo880()

MAX_SOURCE_LENGTH = 1024
MAX_TARGET_LENGTH = 1024
USES_PADDING = "max_length" #False
DO_IGNORE_PAD_TOKEN_FOR_LOSS = True

from transformers import BartTokenizer, BartForConditionalGeneration
tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
model = BartForConditionalGeneration.from_pretrained("facebook/bart-base")

def preprocess_function(data):
        input_encodings = tokenizer.batch_encode_plus(data['text'], padding=USES_PADDING, truncation=True)
        target_encodings = tokenizer.batch_encode_plus(data['logical_form'], padding=USES_PADDING, truncation=True)

        labels = target_encodings['input_ids']
        if USES_PADDING == "max_length" and DO_IGNORE_PAD_TOKEN_FOR_LOSS:
            labels = [
                [(l if l != tokenizer.pad_token_id else -100) for l in label] for label in labels
            ]

        encodings = {
            'input_ids': input_encodings['input_ids'],
            'attention_mask': input_encodings['attention_mask'],
            'labels': labels,
        }
        return encodings
    
datasets = datasets.map(preprocess_function, batched=True)
columns = ['input_ids', 'labels','attention_mask',] 
datasets.set_format(type='torch', columns=columns)

from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir='./models/bart-test',          
    num_train_epochs=5,           
    per_device_train_batch_size=1, 
    #per_device_eval_batch_size=1,   
    #warmup_steps=100,               
    weight_decay=0.01,              
    logging_dir='./logs',          
)

trainer = Trainer(
    model=model,                       
    args=training_args,                  
    train_dataset=datasets['train'],        
    eval_dataset=datasets['test']   
)

trainer.train()