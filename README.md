# 🛡️ CYBERASSIST-MINI

## Lightweight LLM for Vulnerability Knowledge & Security Analysis

**Built on Termux (Android)** | **Zero Cloud Dependencies** | **Defensive Security Research**

---

## 🎯 WHAT IS CYBERASSIST-MINI?

CyberAssist-mini is a fine-tuned Large Language Model (1.1B parameters) that understands CVE vulnerabilities, exploit patterns, and security concepts — all running on a smartphone.

| Feature | Detail |
|---------|--------|
| Base Model | TinyLlama-1.1B-Chat |
| Training Data | 2,000+ CVEs + 1,000+ ExploitDB records |
| Hardware | Trained on Android (Termux) + Colab T4 |
| Inference | Runs on any phone with 4GB RAM |
| File Size | ~20 MB (LoRA adapters) |

---

## 🚀 WHY THIS MATTERS

**"Security knowledge shouldn't require a supercomputer."**

| Problem | CyberAssist-mini Solution |
|---------|---------------------------|
| Cloud GPUs are expensive | Trains on free Colab or Termux |
| Internet isn't always available | Runs completely offline after training |
| Proprietary models black-box security | Open source, fully auditable |
| Limited access to high-end hardware | Built on a budget Android phone |

---

## 🧠 WHAT THE MODEL KNOWS

**CVE Vulnerabilities**

Q: What is CVE-2021-44228?
A: Log4Shell — Remote code execution in Apache Log4j 2.x. Affects versions 2.0-beta9 to 2.14.1.

**Attack Patterns**

Q: What is SQL injection?
A: Malicious SQL code inserted into queries. Prevention: parameterized queries, input validation.

**Malware Types**

Q: What is ransomware?
A: Encrypts files and demands payment. Examples: WannaCry, LockBit, Ryuk.

**Detection Methods**

Q: How to detect reverse shells?
A: Monitor outbound connections, processes from temp directories, abnormal child processes.

---

## ❌ WHAT THE MODEL DOES NOT KNOW

| Limitation | Reason |
|------------|--------|
| Write working exploit code | Model too small, not trained on code generation |
| Zero-day vulnerabilities | Training data is public CVEs only |
| Real-time threat intelligence | Static training data |
| Recent CVEs (last 3 months) | Dataset cutoff depends on source |

---

## 📜 ETHICAL GUIDELINES

**ALLOWED USES**

| Use Case | Status |
|----------|--------|
| Educational research | ✅ Permitted |
| Defensive security analysis | ✅ Permitted |
| Log analysis and threat detection | ✅ Permitted |
| Learning about vulnerabilities | ✅ Permitted |
| Building security awareness tools | ✅ Permitted |
| CTF competitions and training | ✅ Permitted |

**PROHIBITED USES**

| Use Case | Status |
|----------|--------|
| Generating malicious code | ❌ Forbidden |
| Creating actual exploits | ❌ Forbidden |
| Attacking systems without authorization | ❌ Forbidden |
| Selling as a hacking tool | ❌ Forbidden |
| Using for illegal activities | ❌ Forbidden |

**ETHICS STATEMENT**

> This model is trained on public vulnerability data for defensive purposes only. It is not a penetration testing tool. It does not generate working exploits. It does not provide step-by-step hacking instructions. Misuse of this model for illegal activities is not supported and violates the intended use.

---

## 💻 SYSTEM REQUIREMENTS

### For Training

| Component | Minimum |
|-----------|---------|
| RAM | 8GB (12GB recommended) |
| Storage | 5GB free |
| GPU | T4 (Colab) or any 4GB+ GPU |
| Internet | Required for data download |
| Time | 2-3 hours |

### For Inference (Running the Model)

| Platform | Requirements |
|----------|--------------|
| Termux (Android) | 4GB RAM, 2GB storage |
| Linux | 4GB RAM, Python 3.8+ |
| Windows/Mac | 4GB RAM |

---

## 🔧 INSTALLATION GUIDE

### Option 1: Google Colab (Recommended for Training)

1. Open colab.research.google.com
2. Runtime → Change runtime type → Select T4 GPU
3. Upload cyberassist_mini_train.py
4. Click Run
5. Download cyberassist_mini.zip when complete

### Option 2: Termux (Android)

```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install torch transformers datasets peft
git clone https://github.com/Ai-Security-assistant/CyberAssist/
cd cyberassist-mini
python train.py

