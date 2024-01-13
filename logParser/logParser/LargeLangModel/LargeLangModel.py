# -*- coding: utf-8 -*-

import torch
from datasets import load_dataset

import transformers
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer, pipeline
from transformers.generation import GenerationConfig


from peft import prepare_model_for_kbit_training
from peft import LoraConfig, get_peft_model

from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFaceHub, HuggingFacePipeline
from logParser.utils.const import (
    DEFAULT_MODEL_ID,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TOP_P,
    MODEL_PATH,
    FINE_TUNINNING_DATA,
    HF_DEFAULT_MODEL_ID,
    OPENAI_DEFAULT_MODEL_ID,
)



class LargeLangModel:

    def __init__(
            self,
            model_path:str = MODEL_PATH,
            data_path:str = "",
            model_from:str = "openai",
    ):
        self.model_path = model_path
        self.data_path = data_path
        self.model_from = model_from
        self.llm = self.load_model()

    def load_model(self):

        if self.model_from == "openai":
            return ChatOpenAI(temperature=DEFAULT_TEMPERATURE, max_tokens=DEFAULT_MAX_TOKENS, model=OPENAI_DEFAULT_MODEL_ID)

        model_file_name = HF_DEFAULT_MODEL_ID.split("/")[1]
        if self.model_from == "local":
            model = torch.load(f"{self.model_path}/{model_file_name}.pt")
        elif self.model_from == "huggingface":
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            model = AutoModelForCausalLM.from_pretrained(
                HF_DEFAULT_MODEL_ID,
                quantization_config=bnb_config,
                device_map={"":0}
            )
            if self.data_path:
                model = self._fine_tunning(self.model)
                torch.save(model, f"{self.model_path}/{model_file_name}.pt")

        tokenizer = AutoTokenizer.from_pretrained(HF_DEFAULT_MODEL_ID)
        pipe = pipeline(
            "text-generation", model=model, max_new_tokens=DEFAULT_MAX_TOKENS,
            tokenizer=tokenizer, model_kwargs={"temperature": DEFAULT_TEMPERATURE}
        )
        return HuggingFacePipeline(pipeline=pipe)


    def _data_preprocessing(self):
        data = load_dataset("csv", data_files={"train": self.data_path})
        data = data.map(
            lambda x: {
                'text': f"""
                User: {x['instruction']}
                Assistant: {x['output']}<|endoftext|>
                """
            }
        )
        return data

    def _fine_tunning(self, model):
        data = self._data_preprocessing()
        data = data.map(lambda samples: self.tokenizer(samples["text"]), batched=True)

        self.model.gradient_checkpointing_enable()
        model = prepare_model_for_kbit_training(model)

        config = LoraConfig(
            r=8,
            lora_alpha=32,
            target_modules=["query_key_value"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )

        model = get_peft_model(model, config)

        # 학습되는 파라미터 수 출력
        trainable_params = 0
        all_param = 0
        for _, param in model.named_parameters():
            all_param += param.numel()
            if param.requires_grad:
                trainable_params += param.numel()

        print(f"""trainable params: {trainable_params}
        all params: {all_param}
        trainable%: {100 * trainable_params / all_param}""")

        self.tokenizer.pad_token = self.tokenizer.eos_token
        trainer = transformers.Trainer(
            model=model,
            train_dataset=data['train'],
            args=transformers.TrainingArguments(
                max_steps=100, # 100 step 학습시, V100 기준 약 2분 소요
                per_device_train_batch_size=2,
                gradient_accumulation_steps=1,
                learning_rate=1e-4,
                fp16=True,
                output_dir="outputs",
                optim="paged_adamw_8bit",
                logging_steps=25,
            ),
            data_collator=transformers.DataCollatorForLanguageModeling(self.tokenizer, mlm=False),
        )

        model.config.use_cache = False
        trainer.train()

        model.eval()
        model.config.use_cache = True

        return model

    # def gen(self, x):

    #     self.gen_cfg = GenerationConfig.from_model_config(self.model.config)
    #     self.gen_cfg.pad_token_id = self.tokenizer.eos_token_id

    #     self.gen_cfg.temperature = 0.3
    #     self.gen_cfg.max_new_tokens = 128

    #     gened = self.model.generate(
    #         **self.tokenizer(
    #             f"User: {x}\n\nAssistant:",
    #             return_tensors='pt',
    #             return_token_type_ids=False
    #         ).to('cuda'),
    #         do_sample=True,
    #         generation_config=self.gen_cfg
    #     )

    #     return self.tokenizer.decode(gened[0])