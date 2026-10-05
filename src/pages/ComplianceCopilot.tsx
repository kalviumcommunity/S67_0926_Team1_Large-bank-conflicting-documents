import { useState } from "react";

type Message = {
  id: number;
  type: "assistant" | "user";
  text: string;
};

const suggestedQuestions = [
  "Which rule governs a $450,000 transaction?",
  "Are there conflicts for cross-border transfers?",
  "Compare FinCEN and OCC requirements",
];

const initialMessages: Message[] = [
  {
    id: 1,
    type: "assistant",
    text: "Hello! I'm your Compliance Copilot. I can help you identify governing regulations, compare rules, and detect conflicts across your compliance documents.",
  },
];

function ComplianceCopilot() {
  const [messages, setMessages] =
    useState<Message[]>(initialMessages);

  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);

  const getResponse = (question: string) => {
    const lowerQuestion = question.toLowerCase();

    if (
      lowerQuestion.includes("450,000") ||
      lowerQuestion.includes("transaction")
    ) {
      return "For a $450,000 cross-border transaction, the primary governing requirement is FinCEN Circular 2024-04. The transaction should also be checked against OCC Bulletin 2024-17 for customer verification requirements.";
    }

    if (
      lowerQuestion.includes("conflict") ||
      lowerQuestion.includes("cross-border")
    ) {
      return "I found 2 potentially conflicting requirements related to cross-border transactions. FinCEN Circular 2024-04 governs transaction reporting, while OCC Bulletin 2024-17 introduces additional customer verification requirements.";
    }

    if (
      lowerQuestion.includes("compare") ||
      lowerQuestion.includes("fincen") ||
      lowerQuestion.includes("occ")
    ) {
      return "FinCEN Circular 2024-04 focuses primarily on cross-border transaction reporting. OCC Bulletin 2024-17 focuses on risk-based customer verification. Both may apply to the same transaction, so the requirements should be evaluated together.";
    }

    return "Based on the available regulatory documents, I recommend reviewing the governing rule, its effective date, and any conflicting historical requirements before completing the transaction.";
  };

  const sendMessage = (messageText?: string) => {
    const question = (messageText ?? input).trim();

    if (!question || isThinking) {
      return;
    }

    const userMessage: Message = {
      id: Date.now(),
      type: "user",
      text: question,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setInput("");
    setIsThinking(true);

    setTimeout(() => {
      const assistantMessage: Message = {
        id: Date.now() + 1,
        type: "assistant",
        text: getResponse(question),
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);

      setIsThinking(false);
    }, 700);
  };

  return (
    <div className="copilot-page">
      {/* PAGE HEADER */}
      <div className="copilot-heading">
        <div>
          <span className="eyebrow">
            AI-POWERED COMPLIANCE ASSISTANCE
          </span>

          <h2>Compliance Copilot</h2>

          <p>
            Ask questions about regulatory rules, documents,
            conflicts, and transaction requirements.
          </p>
        </div>

        <div className="copilot-status">
          <span className="copilot-status-dot"></span>
          Regulatory Knowledge Base
          <strong>LIVE</strong>
        </div>
      </div>

      {/* COPILOT LAYOUT */}
      <section className="copilot-layout">
        {/* CHAT */}
        <div className="copilot-chat-card">
          <div className="copilot-chat-header">
            <div className="copilot-avatar">✦</div>

            <div>
              <strong>Compliance Copilot</strong>
              <span>
                Regulatory intelligence assistant
              </span>
            </div>

            <span className="copilot-live-badge">
              LIVE
            </span>
          </div>

          {/* MESSAGES */}
          <div className="copilot-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`copilot-message-row ${message.type}`}
              >
                {message.type === "assistant" && (
                  <div className="message-avatar">
                    ✦
                  </div>
                )}

                <div className="copilot-message">
                  {message.text}
                </div>
              </div>
            ))}

            {isThinking && (
              <div className="copilot-message-row assistant">
                <div className="message-avatar">✦</div>

                <div className="copilot-message thinking">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>

          {/* SUGGESTIONS */}
          <div className="copilot-suggestions">
            <span>TRY ASKING</span>

            <div>
              {suggestedQuestions.map((question) => (
                <button
                  key={question}
                  onClick={() => sendMessage(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>

          {/* INPUT */}
          <div className="copilot-input-area">
            <input
              type="text"
              placeholder="Ask about a rule, transaction, or compliance requirement..."
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  sendMessage();
                }
              }}
            />

            <button
              className="copilot-send-button"
              onClick={() => sendMessage()}
              disabled={!input.trim() || isThinking}
            >
              Send
            </button>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <aside className="copilot-context-card">
          <div className="copilot-context-header">
            <span className="card-label">
              REGULATORY CONTEXT
            </span>

            <h3>Relevant Sources</h3>
          </div>

          <div className="source-item">
            <div className="source-icon">F</div>

            <div>
              <strong>FinCEN Circular 2024-04</strong>
              <span>
                Cross-border transaction reporting
              </span>
            </div>

            <span className="source-risk high">
              HIGH
            </span>
          </div>

          <div className="source-item">
            <div className="source-icon">O</div>

            <div>
              <strong>OCC Bulletin 2024-17</strong>
              <span>
                Risk-based customer verification
              </span>
            </div>

            <span className="source-risk medium">
              MEDIUM
            </span>
          </div>

          <div className="source-item">
            <div className="source-icon">R</div>

            <div>
              <strong>AML Regulatory Update</strong>
              <span>
                Suspicious transaction monitoring
              </span>
            </div>

            <span className="source-risk low">
              LOW
            </span>
          </div>

          <div className="copilot-context-divider"></div>

          <div className="context-section">
            <span className="card-label">
              KNOWLEDGE BASE
            </span>

            <div className="context-stat">
              <strong>1,248</strong>
              <span>Active governing rules</span>
            </div>

            <div className="context-stat">
              <strong>8</strong>
              <span>Recent documents indexed</span>
            </div>

            <div className="context-stat">
              <strong>38</strong>
              <span>Known rule conflicts</span>
            </div>
          </div>

          <div className="copilot-disclaimer">
            <span>ⓘ</span>

            <p>
              Copilot responses are based on indexed
              regulatory documents. Always verify critical
              compliance decisions against the governing
              source.
            </p>
          </div>
        </aside>
      </section>
    </div>
  );
}

export default ComplianceCopilot;