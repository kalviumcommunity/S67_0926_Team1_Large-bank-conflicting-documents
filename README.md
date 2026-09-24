# 🏦 Compliance AI

An AI-powered regulatory compliance assistant designed to help banking risk officers quickly identify the current rule governing a transaction, resolve conflicts between historical regulations, and trace the evidence behind each decision.

---

## 📌 Problem Statement

A large bank maintains compliance circulars, internal audit reports, and regulatory updates, but risk officers cannot quickly confirm which current rule governs a transaction without reading through conflicting historical documents.

Compliance AI addresses this problem by bringing regulatory information, AI-assisted rule resolution, historical comparisons, and audit traceability into a single platform.

---

## 💡 Solution

Compliance AI provides a centralized platform where risk officers can:

- 🤖 Ask compliance-related questions using an AI Copilot
- 📜 View currently active regulatory rules
- ⚖️ Compare current and historical rules
- 📄 Access supporting regulatory documents
- 🔍 Understand why a particular rule applies
- 📋 Track compliance activities through an audit trail

### Core Workflow

**Ask → Resolve → Explain → Verify → Compare → Audit**

---

## ✨ Key Features

### 🤖 Compliance Copilot
Ask questions about transactions, regulations, policies, and historical rule changes.

The Copilot provides:

- Current governing rule
- Reason why the rule applies
- Supporting sources
- Historical context
- Relevant rule comparisons

### 📊 Compliance Dashboard
Provides an overview of the current compliance environment, including:

- Active rules
- Regulatory updates
- Rule conflicts
- Pending reviews
- Regulatory activity
- Recent compliance updates

### 📜 Active Rules
Browse and search currently active regulatory rules and directives.

Users can filter rules by:

- Regulatory authority
- Jurisdiction
- Status
- Effective date
- Category

### ⚖️ Compare Rules
Compare previous and current regulatory rules to clearly identify:

- What changed
- Which clauses changed
- Previous requirements
- Current requirements
- Why the current rule takes precedence

### 📄 Regulatory Documents
Centralized repository for regulatory circulars, directives, reports, and other compliance documents.

### 📋 Audit Trail
Maintains traceability of compliance activities, including:

- User queries
- Resolved rules
- Sources used
- Actions performed
- Timestamps

---

## 🛠️ Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- React Router
- TanStack Query
- Zustand
- Recharts
- React Hook Form
- Zod
- Lucide React

### Backend

To be integrated.

Planned technologies may include:

- Node.js
- Express.js
- MongoDB
- AI/LLM API

---

## 📁 Project Structure

```text
src/
│
├── assets/
│
├── components/
│   ├── ui/
│   ├── layout/
│   ├── dashboard/
│   ├── copilot/
│   ├── rules/
│   ├── comparison/
│   ├── documents/
│   └── audit/
│
├── hooks/
├── layouts/
├── lib/
├── pages/
├── services/
├── store/
├── types/
├── utils/
│
├── App.tsx
├── index.css
└── main.tsx