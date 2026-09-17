# Teach a Tiny AI to Be Your Grocery Store Helper

### Fine-tune Qwen2.5-0.5B-Instruct on a plain CPU (no GPU), turn it into a GGUF file, and run it in Ollama

*Last checked against the official docs: September 17, 2026.*

---

## Read this first: one big fix and two small fixes to the plan you pasted

Your plan says "Fine-tune with **Unsloth on CPU only**." That part will not run.

**The big fix.** Unsloth's own requirements page says its training runs on NVIDIA, AMD, and Intel GPUs (and on Macs through Unsloth Studio). On a CPU-only computer, Unsloth supports *chatting* with GGUF models and its *Data Recipes* tool, but **not training**. Unsloth Core needs an NVIDIA GPU with CUDA capability 7.0+. If you run `FastLanguageModel.from_pretrained(...)` on a machine with no GPU, it stops with an error.

So this tutorial uses the "plain Hugging Face" toolkit instead: `transformers` + `peft` + `trl`. Those three libraries run happily on a CPU (slowly, but fine for a 0.5B model). You get:

- the **same model** (`unsloth/Qwen2.5-0.5B-Instruct`),
- the **same LoRA idea and settings** (r=8, alpha=16, the same seven target modules),
- the **same result** (a GGUF file that runs in Ollama).

**Two small fixes** (library names changed):

| Your plan wrote | Current name | Why |
|---|---|---|
| `SFTConfig(max_seq_length=...)` | `SFTConfig(max_length=...)` | TRL renamed it. Old name now errors. |
| `torch_dtype=torch.float32` | `dtype=torch.float32` | Transformers renamed it (v4.56+). Old name still works on older versions. |

If you **do** have an NVIDIA GPU (or use free Google Colab), the Unsloth version of your plan is in **Part 3**.

---

## How this guide is organized

- **Part 1 — Do it (step by step).** One complete example, start to finish.
- **Part 2 — Understand it.** What every piece means, in plain language.
- **Part 3 — Your choices.** Options with pros and cons.
- **Part 4 — Best practices.**
- **Part 5 — When things break.**
- **Part 6 — Glossary.**
- **Part 7 — Sources and what changed from your plan.**

Throughout, two pictures help:

- **The grocery store.** A new employee at *Sunny Market* has to learn where everything is. Our AI is that new employee.
- **The school.** Training is studying with flashcards, then taking a pop quiz.

---

# Part 1 — Do it: the Sunny Market Helper

## Step 0 — The big picture

An AI language model is like a student who has read a giant library. It is great at general things but knows **nothing** about *your* store. Ask the untrained model "Which aisle has honey?" and it will make up an answer.

**Fine-tuning** is a short, focused study session. We give the model about 300 flashcards ("Where is honey?" → "You can find honey in Aisle 4.") and let it study them a few times. Afterward it answers store questions correctly, in the short style we taught it.

Here is the whole trip:

```
make flashcards  ->  quiz the untrained model  ->  train (study)  ->  quiz again
   ->  merge the notes into the model  ->  shrink it to a GGUF file  ->  run it in Ollama
```

## Step 1 — What you need

| Thing | Minimum | Nicer |
|---|---|---|
| Computer | Any 64-bit Linux, macOS, or Windows | 8+ CPU cores |
| RAM | 8 GB | 16 GB |
| Free disk | 6 GB | 10 GB |
| Python | 3.10, 3.11, or 3.12 | 3.11 |
| Internet | Needed once to download the model (~1 GB) | — |
| Time | ~15–60 minutes of training, depending on your CPU | — |
| Ollama | Installed from https://ollama.com/download | — |

Windows users: everything below works in PowerShell. WSL2 (Ubuntu inside Windows) is a bit smoother, especially for Step 8.

## Step 2 — Set up a clean workspace

A **virtual environment** is like a clean backpack for one class: only this project's stuff goes in it, so nothing gets mixed up with other projects.

```bash
mkdir sunny-market && cd sunny-market
python3 -m venv venv
source venv/bin/activate        # Windows PowerShell:  venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# CPU-only PyTorch (smaller download than the GPU version)
pip install torch --index-url https://download.pytorch.org/whl/cpu
# On a Mac, use plain:  pip install torch

pip install transformers datasets peft trl accelerate
```

Check that it worked:

```bash
python -c "import torch, transformers, peft, trl; print('torch', torch.__version__, '| cuda?', torch.cuda.is_available())"
```

You should see `cuda? False`. That is correct for this recipe.

## Step 3 — Make the flashcards (the training data)

Each flashcard is one line of a file called `train.jsonl`. It has three parts:

- **system** – the job description ("You are the Sunny Market grocery helper...")
- **user** – the question a shopper asks
- **assistant** – the exact answer we want

One line looks like this:

```json
{"messages":[
  {"role":"system","content":"You are the Sunny Market grocery helper. Answer in one short sentence."},
  {"role":"user","content":"Where do I find honey?"},
  {"role":"assistant","content":"You can find honey in Aisle 4."}
]}
```

Typing 300 of these by hand would be boring, so this script builds them from a store map. It also builds a **pop quiz** (`test.jsonl`) that uses a way of asking the model has *never* seen during study, so we can tell the difference between memorizing and understanding.

Save this as `make_data.py`:

```python
# make_data.py  -- builds train.jsonl (for studying) and test.jsonl (the pop quiz)
import json, random
random.seed(7)

SYSTEM = "You are the Sunny Market grocery helper. Answer in one short sentence."

AISLES = {
    "Aisle 1": ["apples", "bananas", "grapes", "strawberries", "carrots",
                "lettuce", "tomatoes", "onions", "potatoes", "broccoli"],
    "Aisle 2": ["milk", "cheese", "yogurt", "butter", "eggs", "orange juice"],
    "Aisle 3": ["bread", "bagels", "tortillas", "muffins"],
    "Aisle 4": ["peanut butter", "jam", "honey", "cereal", "oatmeal"],
    "Aisle 5": ["rice", "pasta", "canned beans", "tomato sauce", "soup", "flour", "sugar"],
    "Aisle 6": ["chips", "pretzels", "popcorn", "cookies", "crackers", "granola bars"],
    "Aisle 7": ["frozen pizza", "ice cream", "frozen vegetables", "frozen waffles"],
    "Aisle 8": ["paper towels", "dish soap", "trash bags", "laundry detergent", "sponges"],
    "Aisle 9": ["shampoo", "toothpaste", "bandages", "sunscreen"],
    "Aisle 10": ["pencils", "notebooks", "glue sticks", "markers", "backpacks"],
}

# 5 ways of asking that the model STUDIES...
TRAIN_QUESTIONS = [
    "Where do I find {item}?",
    "Which aisle has {item}?",
    "I'm looking for {item}.",
    "Can you help me find {item}?",
    "where's the {item}",
]
# ...and 1 way it has NEVER seen, used only on the quiz.
TEST_QUESTION = "Do you know where I can get {item}?"

# Things the store does not sell -> the model must learn to say so.
NOT_SOLD = ["tennis rackets", "car batteries", "puppies", "couches"]

# Store rules. Three phrasings for studying, one new phrasing for the quiz.
POLICY = [
    (["What time do you open?", "When does the store open?", "How early can I shop?"],
     "Are you open early in the morning?",
     "Sunny Market opens at 7 AM every day."),
    (["What time do you close?", "When does the store close?", "How late are you open?"],
     "Are you open late at night?",
     "Sunny Market closes at 10 PM every day."),
    (["Can I return something?", "What is your return policy?", "I need to return an item."],
     "How do refunds work?",
     "Bring your receipt within 30 days for a full refund at the front desk."),
    (["Where is the bathroom?", "Where are the restrooms?", "I need to use the restroom."],
     "Is there a bathroom here?",
     "The restrooms are at the back of the store next to the pharmacy."),
    (["Do you sell birthday cakes?", "Can I order a cake?", "Where can I get a cake for a party?"],
     "I want to buy a birthday cake.",
     "The bakery counter near Aisle 3 takes cake orders."),
    (["Do you have carts?", "Where are the shopping carts?", "Can I get a cart?"],
     "Where do I grab a cart?",
     "Shopping carts are just inside the front entrance."),
]

def row(user, assistant):
    return {"messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}

train, test = [], []

for aisle, items in AISLES.items():
    for item in items:
        answer = f"You can find {item} in {aisle}."
        for q in TRAIN_QUESTIONS:
            train.append(row(q.format(item=item), answer))
        test.append(row(TEST_QUESTION.format(item=item), answer))

for item in NOT_SOLD:
    answer = f"Sorry, Sunny Market does not sell {item}."
    for q in TRAIN_QUESTIONS:
        train.append(row(q.format(item=item), answer))
    test.append(row(TEST_QUESTION.format(item=item), answer))

for study_qs, quiz_q, answer in POLICY:
    for q in study_qs:
        train.append(row(q, answer))
    test.append(row(quiz_q, answer))

random.shuffle(train)

with open("train.jsonl", "w") as f:
    for r in train:
        f.write(json.dumps(r) + "\n")
with open("test.jsonl", "w") as f:
    for r in test:
        f.write(json.dumps(r) + "\n")

print(f"Wrote {len(train)} study examples to train.jsonl")
print(f"Wrote {len(test)} quiz questions to test.jsonl")
```

Run it:

```bash
python make_data.py
```

Expected output:

```
Wrote 318 study examples to train.jsonl
Wrote 66 quiz questions to test.jsonl
```

318 is inside the "300–2000 short examples" range from your plan. Notice three things that make this good flashcard data for a tiny model:

1. **Short answers.** One sentence each. A 0.5B model can nail short, consistent answers; it falls apart on long essays.
2. **One consistent pattern.** Every aisle answer has the same shape: "You can find ___ in Aisle ___." Consistency is what a tiny model learns fastest.
3. **A "no" answer.** We teach it to say "we don't sell that" so it does not invent an aisle for puppies.

## Step 4 — Quiz the *untrained* model first

Before studying, let's see how the model does on the quiz, so we can appreciate the change. Save this as `test_model.py`:

```python
# test_model.py  -- give the model the pop quiz.  Run `python test_model.py --base` to quiz the UNtrained model.
import json, sys, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

MODEL = "unsloth/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32)
if "--base" not in sys.argv:
    model = PeftModel.from_pretrained(model, "lora_qwen05b")   # attach the sticky notes
model.eval()

def ask(messages):
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ids = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=40, do_sample=False)
    return tokenizer.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()

right = total = 0
for line in open("test.jsonl"):
    msgs = json.loads(line)["messages"]
    expected = msgs[-1]["content"]
    answer = ask(msgs[:-1])            # everything except the answer
    ok = (answer == expected)
    right += ok
    total += 1
    print(("PASS" if ok else "FAIL"), "|", msgs[1]["content"], "->", answer)

print(f"\nScore: {right}/{total} exactly right")
```

Run the untrained version:

```bash
python test_model.py --base
```

The first run downloads the model (~1 GB) into your Hugging Face cache. Then you will see the model *guess*. It will probably invent aisles or write long paragraphs, and the score will be around `0/66`. That is the "before" picture.

## Step 5 — Train (the study session)

Save this as `train_cpu.py`:

```python
# train_cpu.py  -- teach Qwen2.5-0.5B-Instruct the Sunny Market store map, on a CPU
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""        # hide any GPU on purpose: this is the CPU recipe
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig

torch.set_num_threads(os.cpu_count() or 4)     # let PyTorch use every CPU core
assert not torch.cuda.is_available(), "GPU is visible; this script is meant for CPU-only runs"

MODEL   = "unsloth/Qwen2.5-0.5B-Instruct"       # same weights as Qwen/Qwen2.5-0.5B-Instruct
MAX_LEN = 512                                   # longest example we allow (in tokens)

# 1) Load the "student" (the model) and its "dictionary" (the tokenizer)
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32)  # older transformers: torch_dtype=

# 2) Add LoRA "sticky notes" instead of rewriting the whole model
lora = LoraConfig(
    r=8, lora_alpha=16, lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
)
model = get_peft_model(model, lora)
model.print_trainable_parameters()             # only ~1% of the model will change

# 3) Load the flashcards
ds = load_dataset("json", data_files="train.jsonl", split="train")
print("Example flashcard, exactly as the model sees it:")
print(tokenizer.apply_chat_template(ds[0]["messages"], tokenize=False, add_generation_prompt=False))

# 4) Study plan
args = SFTConfig(
    output_dir="outputs-qwen05b",
    per_device_train_batch_size=1,     # one flashcard at a time (small RAM)
    gradient_accumulation_steps=4,     # ...but update the notes after every 4 cards
    num_train_epochs=3,                # read the whole deck 3 times
    learning_rate=2e-4,                # how big each correction step is
    warmup_ratio=0.05,                 # start gently
    weight_decay=0.01,                 # keep the notes tidy
    optim="adamw_torch",               # the plain PyTorch optimizer (no GPU tricks)
    max_length=MAX_LEN,                # NOTE: old TRL called this max_seq_length
    packing=False,
    gradient_checkpointing=False,      # set True if you run out of RAM (slower)
    fp16=False, bf16=False,            # full-size numbers on CPU
    use_cpu=True,
    dataloader_num_workers=0,
    logging_steps=5,                   # print the loss every 5 steps
    save_strategy="no",                # we save by hand at the end
    report_to="none",
    seed=3407,
)

# 5) Train (this is the slow part)
trainer = SFTTrainer(model=model, args=args, train_dataset=ds, processing_class=tokenizer)
trainer.train()

# 6) Save only the sticky notes (a few MB), plus the tokenizer
model.save_pretrained("lora_qwen05b")
tokenizer.save_pretrained("lora_qwen05b")
print("Saved LoRA adapter to lora_qwen05b/")
```

Run it:

```bash
python train_cpu.py
```

What you will see:

1. `trainable params: ... || all params: ... || trainable%: ~0.9` — only about 1% of the model is being changed. That is LoRA.
2. The example flashcard printed with strange tags like `<|im_start|>user`. Those are the name tags in the ChatML format (explained in Part 2).
3. Lines like `{'loss': 2.31, ...}` every 5 steps. **Loss is the mistake score.** It should start around 2–3 and drop below 0.3 by the end. Falling loss = the student is learning.

How long? Each flashcard is only ~60 tokens, so one pass takes roughly 1–3 seconds on a modern CPU. 318 cards × 3 rounds ≈ 950 passes ≈ **15–60 minutes**. RAM use is usually 4–6 GB. Go make a sandwich.

Tip: on Linux/macOS, `nohup python train_cpu.py > train.log 2>&1 &` lets it keep running if you close the terminal; watch it with `tail -f train.log`.

## Step 6 — Quiz again (the "after" picture)

```bash
python test_model.py
```

Now the model answers with the exact pattern it studied, including questions worded a way it never saw ("Do you know where I can get honey?"). Expect most of the 66 quiz questions to pass. If the score is under about 80%, read Step 5's knob section in Part 3 (usually: one or two more epochs).

Interesting things to look for:

- The **not-sold** items: does it politely say "Sunny Market does not sell puppies" instead of inventing Aisle 12?
- The **policy** questions with new wording: "Is there a bathroom here?" → restrooms answer.

## Step 7 — Merge the sticky notes into the model

Right now you have the original model plus a small LoRA folder (`lora_qwen05b/`, a few megabytes). Ollama's converter wants one normal model folder, so we bake the notes in. Save as `merge_lora.py`:

```python
# merge_lora.py  -- glue the sticky notes into the model so we get one normal model folder
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

MODEL = "unsloth/Qwen2.5-0.5B-Instruct"
base = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32)
model = PeftModel.from_pretrained(base, "lora_qwen05b")
model = model.merge_and_unload()                   # bake LoRA into the weights
model.save_pretrained("merged_qwen05b", safe_serialization=True)
AutoTokenizer.from_pretrained(MODEL).save_pretrained("merged_qwen05b")
print("Saved merged model to merged_qwen05b/")
```

```bash
python merge_lora.py
```

You now have `merged_qwen05b/` (about 2 GB, full-size numbers). Keep `lora_qwen05b/` too; it is tiny and lets you re-merge later.

## Step 8 — Shrink it into a GGUF file (llama.cpp)

**GGUF** is the file format that Ollama (and llama.cpp) can read. Converting also lets us **quantize**: round the numbers so the file gets ~5× smaller and runs faster on a CPU.

Get the converter (this is just a Python script inside the llama.cpp repo; no compiling needed for this step):

```bash
git clone https://github.com/ggml-org/llama.cpp
pip install -r llama.cpp/requirements/requirements-convert_hf_to_gguf.txt
```

### Option A — simplest (8-bit, ~530 MB, no compiling)

```bash
python llama.cpp/convert_hf_to_gguf.py merged_qwen05b --outtype q8_0 --outfile sunny-helper-q8_0.gguf
```

### Option B — smallest (Q4_K_M, ~400 MB, what your plan asked for)

First make a 16-bit GGUF, then quantize it with the `llama-quantize` program.

```bash
python llama.cpp/convert_hf_to_gguf.py merged_qwen05b --outtype f16 --outfile sunny-helper-f16.gguf

# Build just the quantize tool (needs cmake + a C++ compiler; a few minutes)
cmake -S llama.cpp -B llama.cpp/build -DCMAKE_BUILD_TYPE=Release
cmake --build llama.cpp/build --config Release -j --target llama-quantize

./llama.cpp/build/bin/llama-quantize sunny-helper-f16.gguf sunny-helper-q4_k_m.gguf Q4_K_M
```

No compiler? The llama.cpp GitHub **Releases** page has prebuilt zips for Windows, macOS, and Linux that include `llama-quantize` (on Windows, `llama-quantize.exe`). Download, unzip, and run the same last command with that binary.

## Step 9 — Put it in Ollama

Ollama needs a **Modelfile**: a short recipe card that says which GGUF to use, how to format conversations, and which system prompt to use. The `TEMPLATE` below is Qwen's ChatML format. Do **not** swap in a Llama template; the model was trained with these exact tags.

Save this as `Modelfile` (no extension) in the same folder as your GGUF:

```
FROM ./sunny-helper-q4_k_m.gguf
TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
{{ .Response }}<|im_end|>
"""
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER temperature 0.3
PARAMETER num_ctx 2048
SYSTEM You are the Sunny Market grocery helper. Answer in one short sentence.
```

(If you chose Option A, change the first line to `FROM ./sunny-helper-q8_0.gguf`.)

Important: the `SYSTEM` line is **word-for-word the same** as the system message in `make_data.py`. The model learned to answer *under that job description*; changing it is like giving the employee a different job title on day one.

Create and run it (from the folder that contains the Modelfile):

```bash
ollama create sunny-helper -f Modelfile
ollama run sunny-helper "Which aisle has honey?"
```

Expected:

```
You can find honey in Aisle 4.
```

Try the chat mode too:

```bash
ollama run sunny-helper
>>> Do you know where I can get sunscreen?
You can find sunscreen in Aisle 9.
>>> do you sell puppies
Sorry, Sunny Market does not sell puppies.
>>> /bye
```

## Step 10 — You did it. What to try next

- Change the aisles in `make_data.py` to your **real** store, school, or club, rerun Steps 3–9.
- Add a second job: "classify this shopping-list item into a department" (`"eggs"` → `"Dairy"`). Tiny models love classify / extract / rewrite jobs.
- Share the model: `ollama push` needs an ollama.com account; or just hand someone the `.gguf` and the `Modelfile`.

---

# Part 2 — Understand it: what every piece means

## 2.1 What a language model is

A language model is a giant "guess the next word" machine. Give it "Peanut butter and ___" and it guesses "jelly". Do that thousands of times and you get sentences. Qwen2.5-0.5B-Instruct is a **small** one: 0.5 billion numbers (called **parameters** or **weights**) that got tuned by reading a huge amount of text.

School picture: the model is a student who has read the whole library but has never been inside your school. It knows what a cafeteria *is*; it does not know that yours serves pizza on Fridays.

## 2.2 Base vs. Instruct

- **Base** model (`Qwen2.5-0.5B`): knows a lot, but just keeps writing. Ask a question and it might write three more questions.
- **Instruct** model (`Qwen2.5-0.5B-Instruct`): the same student after learning classroom rules — when asked a question, answer it, then stop.

Your plan is right to insist on the **Instruct** version. Teaching store facts is easy; teaching "answer then stop" from scratch is not.

## 2.3 Three ways to make an AI know your store

| Method | Grocery-store version | Good for | Downside |
|---|---|---|---|
| **Prompting** | Tell the cashier the rules at the start of every shift | Quick tests, small rule lists | You repeat it every time; long prompts slow a tiny model |
| **RAG** (look-up) | Give the cashier a binder to flip through | Facts that change often (today's prices) | Needs a search system; the model still has to read the binder each time |
| **Fine-tuning** (this guide) | Train the cashier until they *remember* | Style, format, fixed facts, narrow jobs | Takes time; must retrain when facts change |

Best real-world setups often use fine-tuning for *style and format* and RAG for *facts that change*.

## 2.4 LoRA: sticky notes instead of rewriting the textbook

Full fine-tuning changes all 500 million numbers. That needs lots of memory and can make the model forget things.

**LoRA** (Low-Rank Adaptation) leaves the textbook alone and adds small sticky notes on certain pages. Only the notes are trained.

| Setting | Plain meaning | Our value |
|---|---|---|
| `r` (rank) | How big each sticky note is | 8 (small and enough for facts/format) |
| `lora_alpha` | How strongly the notes count vs. the original text | 16 (2× r is the usual rule of thumb) |
| `lora_dropout` | Randomly ignoring some notes during study, to avoid over-relying on any one | 0 (tiny dataset, short training; not needed) |
| `target_modules` | Which pages get notes | The 7 attention + MLP layers: `q_proj k_proj v_proj o_proj gate_proj up_proj down_proj` (all the "thinking" pages) |

The result is a folder of a few megabytes (`lora_qwen05b/`). In Step 7 we glued the notes into the book so Ollama gets one plain model.

## 2.5 The study-plan knobs (SFTConfig)

| Setting | School meaning | Our value | If you change it |
|---|---|---|---|
| `num_train_epochs` | How many times you go through the whole flashcard deck | 3 | Fact-memorizing tasks like 3–4; style tasks often fine with 1–2. Too many = memorizes the practice test |
| `learning_rate` | How big a step you take when correcting a mistake | 2e-4 (0.0002) | Higher = learns faster but may wobble; lower = safer but slower. 2e-4 is standard for LoRA |
| `per_device_train_batch_size` | How many cards you look at before checking your answers | 1 | Bigger = more RAM. On CPU, 1 is fine |
| `gradient_accumulation_steps` | Grade 4 quizzes, *then* update the grade book | 4 | Free on CPU (same work, fewer updates). 4–8 is typical |
| `warmup_ratio` | Walk before you run: start with tiny steps | 0.05 (first 5%) | Prevents a bad first lurch |
| `weight_decay` | Keep notes small and tidy; don't scribble huge numbers | 0.01 | Gentle protection against overfitting |
| `max_length` | Longest flashcard allowed (in tokens) | 512 | Our cards are ~60 tokens, so this is just a safety cap. 1024 needs more RAM |
| `optim` | Which "study strategy" updates the notes | `adamw_torch` | The plain PyTorch one. `adamw_8bit` needs bitsandbytes + GPU |
| `fp16` / `bf16` | Use half-size numbers | both `False` | On CPU, full-size (float32) is the safe choice |
| `seed` | Shuffle the deck the same way every run | 3407 | Any number; same seed = repeatable results |
| `logging_steps` | How often to print the mistake score | 5 | — |

## 2.6 Loss, and how to read it

**Loss** is the mistake score, flipped: 0 would be perfect. It starts high (the model has never seen your store) and falls as it learns.

- Falls steadily and lands around 0.1–0.5: great.
- Stays flat near the start value: the learning rate is too low, or the data is broken (check the printed flashcard).
- Drops to almost exactly 0.00 very early: it may be memorizing. Check the quiz on *new wording*.
- Jumps around wildly or becomes `nan`: learning rate too high.

## 2.7 Overfitting: memorizing the practice test

A student who memorizes only the practice test fails when the real test rewords a question. That is **overfitting**. This is why the quiz (`test.jsonl`) uses a phrasing the model never studied. If study scores are perfect but quiz scores are bad: fewer epochs, or add more *varied* flashcards.

## 2.8 Tokens and the tokenizer

Models do not read letters or whole words; they read **tokens**, which are word chunks (like syllables). "strawberries" might be `straw` + `berries`. The **tokenizer** is the dictionary that turns text into tokens and back. Roughly, 1 token ≈ ¾ of an English word. Our flashcards are about 60 tokens each.

## 2.9 ChatML: name tags for who is talking

Qwen uses the **ChatML** format. When you printed the flashcard in Step 5 you saw:

```
<|im_start|>system
You are the Sunny Market grocery helper. Answer in one short sentence.<|im_end|>
<|im_start|>user
Where do I find honey?<|im_end|>
<|im_start|>assistant
You can find honey in Aisle 4.<|im_end|>
```

`<|im_start|>` / `<|im_end|>` are like name tags and the "your turn is over" bell. `tokenizer.apply_chat_template(...)` adds them for you; the Ollama `TEMPLATE` reproduces the same layout; the two `stop` parameters tell Ollama the bell means "stop talking." All three must agree, which is why the plan says "do not invent a Llama template."

## 2.10 Numbers, rounding, and GGUF

The model's 0.5 billion numbers can be stored at different sizes:

| Format | Bytes per number | File for this model | Grocery version |
|---|---|---|---|
| float32 | 4 | ~2 GB | Price to the tenth of a cent: $3.9812 |
| float16 / bf16 | 2 | ~1 GB | Normal price: $3.98 |
| Q8_0 | ~1 | ~530 MB | Rounded to the dime: $4.00 |
| Q4_K_M | ~0.5 | ~400 MB | Rounded to the dollar, but keeping exact prices on the items that matter most |

**Quantizing** is that rounding. **GGUF** is the container file that stores the rounded numbers plus the tokenizer plus the chat template, all in one file that llama.cpp and Ollama read directly. The "_K_M" in Q4_K_M means the rounding is smarter about which numbers get more precision (that is why Q4_K_M is the go-to choice).

## 2.11 Ollama

Ollama is the vending machine: you load a GGUF into it once, and then anyone (a terminal, a script, another app) can ask for answers through a simple local API (`http://localhost:11434`). Its `Modelfile` is the recipe card taped to the vending machine.

Modelfile knobs:

- `temperature 0.3` — how adventurous the answers are. Low = predictable, good for facts. 0.8+ = creative writing.
- `num_ctx 2048` — how many tokens of conversation the model keeps in its head at once.
- `stop` — the "bell" tokens.
- `SYSTEM` — the job description, used every time.

## 2.12 The model's inside layout (you don't need to touch this)

Your plan lists: *Qwen2 architecture, 24 layers, GQA 14/2*. Think of 24 layers as 24 stations in a factory line each token passes through. "GQA 14/2" means 14 attention "eyes" share 2 memory notebooks — a trick that saves memory. LoRA's target modules (`q_proj` etc.) are pieces inside each of those 24 stations. None of these numbers are settings you change; they describe the model.

Model facts (from the model card): 0.49 billion parameters (0.36 B not counting the word-embedding table), Apache-2.0 license (free to use, even commercially), context length up to 32K tokens.

---

# Part 3 — Your choices, with pros and cons

## 3.1 Where to train

| Option | Pros | Cons | Pick it when |
|---|---|---|---|
| **A. CPU with transformers + peft + trl** (this guide) | Runs on any computer; nothing to sign up for; you understand each step | Slow (minutes to an hour for 0.5B; days for 7B); no Unsloth speedups | You have no GPU, or you want to learn the plumbing |
| **B. Free Google Colab GPU + Unsloth** | 10–50× faster; Unsloth exports GGUF with one line (`save_pretrained_gguf`) and writes the Modelfile | Needs a Google account; free sessions time out; files live in the cloud until you download them | You have a bigger dataset or a bigger model |
| **C. Unsloth Studio / Desktop (no-code)** | Point-and-click: training, chat, export in one app; also handles Macs (MLX) | Training needs an NVIDIA/AMD/Intel GPU or a Mac; on CPU-only it offers chat + data recipes, not training | You have a supported GPU or Apple Silicon and don't want to write code |
| **D. Your own NVIDIA GPU + Unsloth Core** | Fastest local option; your plan's script works almost as written | Needs a CUDA 7.0+ GPU (RTX 20-series or newer, T4, etc.) and the CUDA toolkit | You own the hardware |

### Your plan's Unsloth script, fixed for a GPU (Options B or D)

```python
from unsloth import FastLanguageModel        # import unsloth FIRST
import torch
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-0.5B-Instruct",
    max_seq_length=512,
    dtype=None,             # let Unsloth pick fp16/bf16 for the GPU
    load_in_4bit=False,     # 0.5B is small; keep full precision
)
model = FastLanguageModel.get_peft_model(
    model, r=8, lora_alpha=16, lora_dropout=0, bias="none",
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
    use_gradient_checkpointing="unsloth", random_state=3407,
)
ds = load_dataset("json", data_files="train.jsonl", split="train")

trainer = SFTTrainer(
    model=model, processing_class=tokenizer, train_dataset=ds,
    args=SFTConfig(
        per_device_train_batch_size=1, gradient_accumulation_steps=4,
        num_train_epochs=3, learning_rate=2e-4, warmup_ratio=0.05,
        weight_decay=0.01, logging_steps=5, optim="adamw_torch",
        max_length=512,      # NOT max_seq_length (renamed). If your Unsloth/TRL combo complains, just delete this line.
        output_dir="outputs-qwen05b", report_to="none", seed=3407,
    ),
)
trainer.train()
model.save_pretrained("lora_qwen05b"); tokenizer.save_pretrained("lora_qwen05b")

# One-line GGUF export; Unsloth builds llama.cpp for you and writes gguf_qwen05b/Modelfile
model.save_pretrained_gguf("gguf_qwen05b", tokenizer, quantization_method="q4_k_m")
```

Then `ollama create sunny-helper -f gguf_qwen05b/Modelfile`. If Unsloth's export fails, fall back to `model.save_pretrained_merged("merged_qwen05b", tokenizer, save_method="merged_16bit")` and do Step 8 above. Unsloth's API changes often; glance at its current Qwen notebook before trusting any argument name (including mine).

## 3.2 LoRA vs. full fine-tuning

| | LoRA (this guide) | Full fine-tune |
|---|---|---|
| Memory | Low (only ~1% trains) | High (everything trains; needs optimizer state for all 500M numbers) |
| Speed | Faster per step | Slower |
| Forgetting | Low risk (original stays intact) | Higher risk of forgetting general skills |
| Output | Tiny adapter you can swap in/out | One new full model |
| Best when | Small data, narrow job, weak hardware | Huge data, big change in behavior, strong GPUs |

For a 0.5B model on a CPU with 300 examples, LoRA is the clear choice.

## 3.3 Which model

| Model | Pros | Cons | Use when |
|---|---|---|---|
| **Qwen2.5-0.5B-Instruct** (locked in your plan) | Tiny, fast on CPU, simple ChatML template, Apache-2.0 | Weak at multi-step reasoning; forgets long instructions | Classify, extract JSON, rewrite, FAQ (like Sunny Market) |
| **Qwen2.5-Coder-0.5B-Instruct** | Same size, better at code | Slightly worse at plain chat | The job is code (fix SQL, write regex). Same script, change `MODEL` |
| **Qwen2.5-1.5B-Instruct** | Noticeably smarter; still runs on CPU | 3× the training time; ~1 GB GGUF | Answers need a little reasoning |
| **Newer Qwen families (Qwen3-0.6B and later)** | Newer, stronger for their size | Chat templates include "thinking" modes and extra tags; more to get right on a first project | After this pipeline works for you, and after reading that model's card |
| **Unsloth "-bnb-4bit" repos** | Small download | 4-bit weights need bitsandbytes + GPU; wrong for CPU (your plan is right to forbid it) | Never on CPU |

## 3.4 How much to shrink (quantization)

| Choice | Size (this model) | Quality | Speed on CPU | Pick when |
|---|---|---|---|---|
| F16 GGUF | ~1 GB | Best | Slowest | You are testing whether a problem is caused by quantization |
| Q8_0 | ~530 MB | Nearly identical to F16 | Fast | Quality matters more than size; simplest to make (Option A) |
| Q4_K_M | ~400 MB | Very slightly lower; usually unnoticeable for a fact/format job | Fastest | Default choice; what your plan asked for |
| Q2/Q3 | smaller | Noticeably worse on a 0.5B model | fastest | Don't, for a model this small |

Tiny models feel quantization more than big ones. If Q4_K_M answers get flaky, try Q8_0 before retraining.

## 3.5 How to get the model into Ollama

| Route | Pros | Cons |
|---|---|---|
| **llama.cpp `convert_hf_to_gguf.py`** (this guide) | Works for Qwen2; you control the quant level; the GGUF works in every llama.cpp app | Extra tools to install |
| **Ollama `FROM ./safetensors-folder`** | No llama.cpp | Ollama's import page officially lists Llama, Mistral, Gemma, Phi3 — Qwen is not on the list, so it may refuse |
| **Ollama `ADAPTER` (load the LoRA folder directly)** | Skips merging | Officially supported for Llama/Mistral/Gemma adapters only |
| **Unsloth `save_pretrained_gguf`** | One line | Needs a GPU session |

## 3.6 Where the flashcards come from

| Source | Pros | Cons |
|---|---|---|
| **Generated from a table** (this guide) | Fast; perfectly consistent; easy to fix and regenerate | Repetitive; the model may only learn the templates you wrote |
| **Hand-written** | Natural wording; covers odd questions | Slow; easy to be inconsistent |
| **Mixed** (generated + 50–100 hand-written) | Best of both | A little more work |

For a real deployment, do "Mixed."

## 3.7 Sequence length: 512 or 1024?

`max_length` is a *cap*. It costs nothing if your examples are short. Raise it to 1024 only if real examples are longer, and only with 16 GB+ RAM. Remember: a 0.5B model that must write 800 tokens will drift; keep answers short instead.

## 3.8 If the quiz score is low — which knob to turn

1. Loss never got below ~1.0 → more epochs (4–5), or check that the flashcards look right.
2. Study questions pass, quiz phrasing fails → add 2–3 more question templates to `TRAIN_QUESTIONS`.
3. Answers are right but formatted differently → make every training answer follow one exact pattern.
4. Answers are right in `test_model.py` but wrong in Ollama → the `TEMPLATE`/`SYSTEM` in the Modelfile doesn't match training (Part 5).

---

# Part 4 — Best practices

1. **One narrow job per tiny model.** Classify, extract, rewrite, FAQ. A 0.5B model will not become a 7B reasoner no matter how long you train.
2. **Short, consistent answers.** Same shape every time. Consistency is the lesson a small model learns best.
3. **Always keep a quiz set** (`test.jsonl`) with wording the model never studied. Score before and after. Numbers beat vibes.
4. **Same system prompt in training and in the Modelfile.** Word for word.
5. **Keep the base model's chat template.** Never invent one.
6. **Watch the loss.** Falling = good. Flat = something's wrong. Instant zero = probably memorizing.
7. **Save the adapter, not just the merged model.** It is tiny and lets you re-merge onto the same base later.
8. **Use a virtual environment and write down versions** (`pip freeze > requirements.txt`) so the run is repeatable.
9. **Start small, then scale.** Get 300 examples working end-to-end before writing 2,000.
10. **Use the CPU-only torch build** on CPU machines; it is a smaller download and avoids CUDA mismatches.
11. **Teach "I don't know."** Include examples where the right answer is "we don't have that," or the model will invent aisles.
12. **Check the license** of any model you swap in. Qwen2.5-0.5B-Instruct is Apache-2.0.
13. **Do not put private data in flashcards you plan to share.** Whatever is in `train.jsonl` can come back out of the model.

---

# Part 5 — When things break

| You see | It means | Fix |
|---|---|---|
| `NotImplementedError: Unsloth currently only works on NVIDIA GPUs...` (or a similar GPU error) | You ran an Unsloth script on a CPU-only machine | Use Part 1's `train_cpu.py`, or move to Colab (Part 3.1) |
| `TypeError: SFTConfig.__init__() got an unexpected keyword argument 'max_seq_length'` | Old argument name | Use `max_length` |
| Warning about `torch_dtype` being deprecated | Old argument name | Use `dtype=` (harmless warning if you leave it) |
| `Killed` with no other message, or the computer freezes | Out of RAM | Close other apps; set `gradient_checkpointing=True`; lower `MAX_LEN` to 256; make sure `dtype=torch.float32` (not float64) |
| Training is painfully slow | Threads not used, or long examples | Make sure `torch.set_num_threads` ran; shorten answers; fewer epochs; or use Colab |
| Loss is `nan` | Learning rate too high or bad data | Try `learning_rate=1e-4`; verify every JSONL line has exactly system/user/assistant with text |
| The Ollama model never stops talking | Stop tokens or template mismatch | Copy the `TEMPLATE` and both `stop` lines from Step 9 exactly |
| Ollama answers in a different style than `test_model.py` | `SYSTEM` line differs from training | Make it identical to `SYSTEM` in `make_data.py` |
| `convert_hf_to_gguf.py` says the architecture is unsupported | Old clone of llama.cpp | `cd llama.cpp && git pull`, reinstall its requirements |
| `ollama create` fails on a safetensors folder | Qwen isn't on Ollama's official import list | Convert to GGUF with llama.cpp (Step 8) |
| First run hangs at "Downloading" | It's fetching ~1 GB from Hugging Face | Wait; check your internet; you can set `HF_HOME` to change where the cache goes |
| `ImportError` for `peft` or `trl` | Wrong virtual environment | `source venv/bin/activate` (Windows: `venv\Scripts\Activate.ps1`) and reinstall |

---

# Part 6 — Glossary

- **Adapter / LoRA** — the small folder of "sticky notes" produced by training.
- **Base model** — a model that continues text but wasn't taught to follow instructions.
- **Batch** — how many examples the model looks at before checking its answers.
- **ChatML** — Qwen's conversation format with `<|im_start|>` and `<|im_end|>` tags.
- **Epoch** — one full pass through all training examples.
- **Fine-tuning** — extra training on your own examples.
- **GGUF** — the single-file model format Ollama and llama.cpp read.
- **Gradient accumulation** — collecting corrections from several examples before updating.
- **Hugging Face** — the library website where models live; `transformers` is its main Python toolkit.
- **Instruct model** — a model trained to follow directions and stop when done.
- **JSONL** — a text file with one JSON object per line.
- **llama.cpp** — the fast CPU engine underneath Ollama; also provides the GGUF converter and quantizer.
- **Learning rate** — the size of each correction step.
- **Loss** — the mistake score during training; lower is better.
- **Merge** — baking LoRA notes into the model's weights.
- **Modelfile** — Ollama's recipe card for a model.
- **Ollama** — a program that runs GGUF models locally and offers a simple API.
- **Overfitting** — memorizing the practice test; failing reworded questions.
- **Parameters / weights** — the model's 500 million learned numbers.
- **PEFT** — the Hugging Face library that implements LoRA.
- **Quantization** — rounding weights to fewer bits to shrink and speed up the model.
- **Seed** — a number that fixes the shuffling so runs are repeatable.
- **System prompt** — the standing job description given to the model.
- **Temperature** — how random the model's word choices are.
- **Token** — a chunk of text (roughly ¾ of a word) that the model actually reads.
- **TRL** — the Hugging Face library with `SFTTrainer`, which runs the study session.
- **Unsloth** — a library/app that makes GPU fine-tuning faster and exports GGUF; needs a GPU or Mac to train.
- **Virtual environment (venv)** — a private folder of Python packages for one project.

---

# Part 7 — Sources, and exactly what changed from your pasted plan

## Verified in September 2026

- Unsloth requirements (CPU = chat + data recipes; training = NVIDIA/AMD/Intel GPUs or Mac; Unsloth Core needs CUDA 7.0+): https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements
- TRL renamed `max_seq_length` → `max_length` in `SFTConfig`; `SFTTrainer` takes `processing_class=`: https://github.com/huggingface/trl
- Ollama import page (safetensors import officially lists Llama, Mistral, Gemma, Phi3; GGUF import works for anything llama.cpp can run): https://docs.ollama.com/import
- llama.cpp converter and quantizer (`convert_hf_to_gguf.py`, `llama-quantize`): https://github.com/ggml-org/llama.cpp
- Qwen's own GGUF guide (convert to F16, then `llama-quantize ... Q4_K_M` / `Q8_0`): https://qwen.readthedocs.io/en/stable/quantization/llama.cpp.html
- Model card: https://huggingface.co/unsloth/Qwen2.5-0.5B-Instruct (mirror of Qwen/Qwen2.5-0.5B-Instruct)

## Change log vs. your plan

| Your plan | This guide | Why |
|---|---|---|
| Unsloth `FastLanguageModel` on CPU | `transformers` + `peft` + `trl` on CPU | Unsloth does not train on CPU-only machines |
| `UNSLOTH_COMPILE_DISABLE=1` | removed | Not needed without Unsloth |
| `use_gradient_checkpointing="unsloth"` | `gradient_checkpointing=False` (turn on if low RAM) | Unsloth-specific option; plain checkpointing is slower on CPU and unnecessary for 0.5B |
| `max_seq_length=` in SFTConfig | `max_length=` | Renamed in TRL |
| `torch_dtype=` | `dtype=` | Renamed in transformers 4.56+ |
| `grad_accum=8`, `epochs=2` | `grad_accum=4`, `epochs=3` | More update steps at zero extra cost, and fact-memorizing tasks like an extra pass. Both are knobs; your values work too |
| `model.save_pretrained_gguf(...)` | `merge_lora.py` + llama.cpp convert + `llama-quantize` | `save_pretrained_gguf` is an Unsloth method |
| Unsloth writes the Modelfile | You write the Modelfile (Step 9) | Same ChatML template your plan's fallback shows |
| Model, LoRA r/alpha/dropout/targets, lr, warmup, weight decay, seed, batch=1, max_length=512, Q4_K_M, ChatML template, stop tokens, temperature, num_ctx | **unchanged** | They were right |

## Sizes and times at a glance

| Item | Approximate |
|---|---|
| Base model download (bf16 safetensors) | ~1 GB |
| LoRA adapter (`lora_qwen05b/`) | a few MB |
| Merged model, float32 (`merged_qwen05b/`) | ~2 GB |
| F16 GGUF | ~1 GB |
| Q8_0 GGUF | ~530 MB |
| Q4_K_M GGUF | ~400 MB |
| Training RAM (seq 512, batch 1) | ~4–6 GB |
| Training time, 318 examples × 3 epochs | ~15–60 min on a modern CPU |
| Ollama speed on CPU (Q4_K_M) | comfortably interactive |
